"""AstrBot ↔ Feedling resident-agent bridge.

This plugin is deliberately a transport, never a second brain:
  QQ private text from an allowlisted owner -> Feedling shared v1 envelope
  Feedling decrypted agent reply -> AstrBot active message to the saved UMO

It never calls an AstrBot provider or any LLM API.
"""
from __future__ import annotations

import asyncio
import base64
import hashlib
import time
import uuid
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

import httpx
from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, MessageChain, filter
from astrbot.api.star import Context, Star

try:
    from .content_encryption import build_envelope
except ImportError:  # AstrBot may load main.py as a top-level module.
    from content_encryption import build_envelope


_STATE_KEY = "feedling_bridge_state_v1"
_MAX_PROCESSED_IDS = 500
_MAX_DELIVERY_KEYS = 1000
_MAX_PENDING_PARENTS = 200
_ASSISTANT_ROLES = {"agent", "assistant", "openclaw"}
_SELFTEST_COMMAND = "feedling_selftest"


@dataclass(frozen=True)
class FeedlingKeys:
    user_id: str
    user_pk: bytes
    enclave_pk: bytes


def _clean_url(value: Any) -> str:
    return str(value or "").strip().rstrip("/")


def _valid_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _owner_ids(value: Any) -> set[str]:
    if isinstance(value, str):
        raw: Iterable[Any] = value.replace("，", ",").split(",")
    elif isinstance(value, Iterable):
        raw = value
    else:
        raw = ()
    return {str(item).strip() for item in raw if str(item).strip()}


def _as_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "on"}:
            return True
        if lowered in {"0", "false", "no", "off"}:
            return False
    return default


def _message_key(message: dict[str, Any]) -> str:
    explicit = str(message.get("id") or message.get("message_id") or "").strip()
    if explicit:
        return explicit
    fingerprint = "|".join(
        [
            str(message.get("ts", message.get("timestamp", 0)) or 0),
            str(message.get("role") or ""),
            str(message.get("content") or ""),
        ]
    )
    return "fallback:" + hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:24]


def _message_ts(message: dict[str, Any]) -> float:
    try:
        return float(message.get("ts", message.get("timestamp", 0)) or 0)
    except (TypeError, ValueError):
        return 0.0


def _message_text(message: dict[str, Any]) -> str:
    value = (
        message.get("content")
        or message.get("text")
        or message.get("plaintext")
        or ""
    )
    return str(value).strip()


def _reply_parent(message: dict[str, Any]) -> str:
    return str(
        message.get("reply_to_message_id")
        or message.get("parent_message_id")
        or ""
    ).strip()


class FeedlingBridge(Star):
    """Pure transport bridge. No provider or LLM APIs are used."""

    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.context = context
        self.config = config
        self.api_url = _clean_url(config.get("feedling_api_url"))
        self.api_key = str(config.get("feedling_api_key") or "").strip()
        self.enclave_url = _clean_url(config.get("feedling_enclave_url"))
        self.owners = _owner_ids(config.get("owner_qq"))
        try:
            configured_interval = float(config.get("poll_interval", 20) or 20)
        except (TypeError, ValueError):
            configured_interval = 20
        self.poll_interval = max(10.0, configured_interval)
        self.forward_app_messages = _as_bool(
            config.get("forward_app_messages"),
            True,
        )

        self._api_http = httpx.AsyncClient(timeout=15.0)
        # Phala/dstack endpoints commonly use a self-signed certificate.
        # Certificate verification is disabled ONLY for the configured enclave.
        self._enclave_http = httpx.AsyncClient(timeout=20.0, verify=False)
        self._whoami_lock = asyncio.Lock()
        self._state_lock = asyncio.Lock()
        self._state_loaded = asyncio.Event()
        self._stop = asyncio.Event()
        self._keys: FeedlingKeys | None = None
        self._keys_loaded_at = 0.0

        self._cursor = 0.0
        self._origins: dict[str, str] = {}
        self._processed_ids: list[str] = []
        self._delivery_keys: list[str] = []
        self._pending_parents: list[str] = []
        self._poll_task = asyncio.create_task(
            self._poll_loop(),
            name="astrbot-feedling-bridge-poll",
        )

    def _config_errors(self) -> list[str]:
        errors = []
        if not _valid_http_url(self.api_url):
            errors.append("feedling_api_url 不是有效的 http(s) URL")
        if not self.api_key:
            errors.append("feedling_api_key 为空")
        if not _valid_http_url(self.enclave_url):
            errors.append("feedling_enclave_url 不是有效的 http(s) URL")
        if not self.owners:
            errors.append("owner_qq 白名单为空")
        return errors

    async def _load_state(self) -> None:
        try:
            raw = await self.get_kv_data(_STATE_KEY, {})
            if not isinstance(raw, dict):
                raw = {}
            self._cursor = max(0.0, float(raw.get("cursor") or 0))
            origins = raw.get("origins") or {}
            if isinstance(origins, dict):
                self._origins = {
                    str(owner): str(umo)
                    for owner, umo in origins.items()
                    if str(owner) in self.owners and str(umo).strip()
                }
            self._processed_ids = [
                str(item)
                for item in (raw.get("processed_ids") or [])
                if str(item)
            ][-_MAX_PROCESSED_IDS:]
            self._delivery_keys = [
                str(item)
                for item in (raw.get("delivery_keys") or [])
                if str(item)
            ][-_MAX_DELIVERY_KEYS:]
            self._pending_parents = [
                str(item)
                for item in (raw.get("pending_parents") or [])
                if str(item)
            ][-_MAX_PENDING_PARENTS:]
        except Exception as exc:
            logger.error("Feedling bridge state load failed: %s", exc)
        finally:
            self._state_loaded.set()

    async def _persist_state_locked(self) -> None:
        await self.put_kv_data(
            _STATE_KEY,
            {
                "cursor": self._cursor,
                "origins": dict(self._origins),
                "processed_ids": self._processed_ids[-_MAX_PROCESSED_IDS:],
                "delivery_keys": self._delivery_keys[-_MAX_DELIVERY_KEYS:],
                "pending_parents": self._pending_parents[-_MAX_PENDING_PARENTS:],
            },
        )

    async def _wait_state(self) -> None:
        await asyncio.wait_for(self._state_loaded.wait(), timeout=10.0)

    async def _fetch_keys(self, *, force: bool = False) -> FeedlingKeys:
        async with self._whoami_lock:
            if (
                not force
                and self._keys is not None
                and time.monotonic() - self._keys_loaded_at < 300
            ):
                return self._keys
            if not _valid_http_url(self.api_url) or not self.api_key:
                raise RuntimeError("Feedling API URL/API key 未配置")
            response = await self._api_http.get(
                f"{self.api_url}/v1/users/whoami",
                headers={"X-API-Key": self.api_key},
            )
            response.raise_for_status()
            body = response.json()
            user_id = str(body.get("user_id") or "").strip()
            try:
                user_pk = base64.b64decode(
                    str(body.get("public_key") or ""),
                    validate=True,
                )
                enclave_pk = bytes.fromhex(
                    str(body.get("enclave_content_public_key_hex") or "")
                )
            except (TypeError, ValueError) as exc:
                raise RuntimeError("whoami 返回的加密公钥格式无效") from exc
            if not user_id or len(user_pk) != 32 or len(enclave_pk) != 32:
                raise RuntimeError("whoami 缺少 user_id 或 32-byte 内容公钥")
            self._keys = FeedlingKeys(user_id, user_pk, enclave_pk)
            self._keys_loaded_at = time.monotonic()
            return self._keys

    def _sealed_payload(
        self,
        text: str,
        client_msg_id: str,
        keys: FeedlingKeys,
    ) -> dict[str, Any]:
        return {
            "envelope": build_envelope(
                plaintext=text.encode("utf-8"),
                owner_user_id=keys.user_id,
                user_pk_bytes=keys.user_pk,
                enclave_pk_bytes=keys.enclave_pk,
                visibility="shared",
            ),
            "client_msg_id": client_msg_id,
            "content_type": "text",
        }

    async def _post_chat_payload(self, payload: dict[str, Any]) -> httpx.Response:
        last_error: BaseException | None = None
        for attempt in range(3):
            try:
                return await self._api_http.post(
                    f"{self.api_url}/v1/chat/message",
                    headers={"X-API-Key": self.api_key},
                    json=payload,
                )
            except httpx.TransportError as exc:
                last_error = exc
                if attempt < 2:
                    await asyncio.sleep(0.5 * (2**attempt))
        assert last_error is not None
        raise last_error

    @staticmethod
    def _is_fingerprint_mismatch(response: httpx.Response) -> bool:
        if response.status_code != 409:
            return False
        try:
            body = response.json()
        except Exception:
            return False
        return (
            isinstance(body, dict)
            and body.get("error") == "content_pk_fpr_mismatch"
        )

    async def _send_user_text(self, text: str) -> dict[str, Any]:
        client_msg_id = str(uuid.uuid4())
        keys = await self._fetch_keys()
        payload = self._sealed_payload(text, client_msg_id, keys)
        response = await self._post_chat_payload(payload)
        if self._is_fingerprint_mismatch(response):
            logger.warning(
                "Feedling content key changed; refreshing whoami and re-sealing once"
            )
            keys = await self._fetch_keys(force=True)
            payload = self._sealed_payload(text, client_msg_id, keys)
            response = await self._post_chat_payload(payload)
        response.raise_for_status()
        body = response.json()
        parent_id = str(body.get("id") or "").strip()
        if not parent_id:
            raise RuntimeError("chat/message 成功响应缺少 id")
        async with self._state_lock:
            if parent_id not in self._pending_parents:
                self._pending_parents.append(parent_id)
                self._pending_parents = self._pending_parents[
                    -_MAX_PENDING_PARENTS:
                ]
            await self._persist_state_locked()
        return body

    async def _history(
        self,
        *,
        since: float | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        if not _valid_http_url(self.enclave_url) or not self.api_key:
            raise RuntimeError("Feedling enclave URL/API key 未配置")
        params: dict[str, Any] = {"limit": limit}
        if since is not None:
            params["since"] = max(0.0, since)
        response = await self._enclave_http.get(
            f"{self.enclave_url}/v1/chat/history",
            headers={"X-API-Key": self.api_key},
            params=params,
        )
        response.raise_for_status()
        body = response.json()
        messages = body.get("messages") or body.get("history") or []
        if not isinstance(messages, list):
            raise RuntimeError("enclave history 响应缺少 messages 列表")
        return [item for item in messages if isinstance(item, dict)]

    async def _capture_origin(self, owner: str, umo: str) -> None:
        await self._wait_state()
        need_seed = not self._origins and self._cursor <= 0
        seed = 0.0
        if need_seed:
            history = await self._history(limit=1)
            seed = max((_message_ts(message) for message in history), default=0.0)
        async with self._state_lock:
            if self._cursor <= 0 and seed > 0:
                self._cursor = seed
            self._origins[owner] = umo
            await self._persist_state_locked()

    async def _send_active_text(self, umo: str, text: str) -> None:
        chain = MessageChain().message(text)
        await self.context.send_message(umo, chain)

    async def _mark_processed(
        self,
        message_key: str,
        ts: float,
        *,
        parent: str = "",
    ) -> None:
        async with self._state_lock:
            if message_key not in self._processed_ids:
                self._processed_ids.append(message_key)
                self._processed_ids = self._processed_ids[-_MAX_PROCESSED_IDS:]
            if parent and parent in self._pending_parents:
                self._pending_parents.remove(parent)
            self._cursor = max(self._cursor, ts)
            await self._persist_state_locked()

    async def _deliver_assistant(
        self,
        message: dict[str, Any],
        origins: list[str],
    ) -> None:
        message_key = _message_key(message)
        text = _message_text(message)
        for umo in origins:
            delivery_key = (
                message_key
                + ":"
                + hashlib.sha256(umo.encode("utf-8")).hexdigest()[:16]
            )
            if delivery_key in self._delivery_keys:
                continue
            await self._send_active_text(umo, text)
            async with self._state_lock:
                if delivery_key not in self._delivery_keys:
                    self._delivery_keys.append(delivery_key)
                    self._delivery_keys = self._delivery_keys[
                        -_MAX_DELIVERY_KEYS:
                    ]
                await self._persist_state_locked()

    async def _poll_once(self) -> None:
        await self._wait_state()
        async with self._state_lock:
            cursor = self._cursor
            origins = sorted(set(self._origins.values()))
            processed = set(self._processed_ids)
            pending = set(self._pending_parents)
        if not origins:
            return
        messages = await self._history(since=max(0.0, cursor - 0.001), limit=100)
        messages.sort(key=lambda message: (_message_ts(message), _message_key(message)))
        for message in messages:
            message_key = _message_key(message)
            ts = _message_ts(message)
            if message_key in processed:
                continue
            role = str(message.get("role") or "").strip().lower()
            parent = _reply_parent(message)
            should_forward = role in _ASSISTANT_ROLES
            if should_forward and not self.forward_app_messages:
                should_forward = bool(parent and parent in pending)
            text = _message_text(message)
            if should_forward and text:
                # Do not advance cursor or processed state until every captured
                # owner origin accepted the active message. A transient adapter
                # error therefore retries instead of silently losing the reply.
                await self._deliver_assistant(message, origins)
            await self._mark_processed(message_key, ts, parent=parent)
            processed.add(message_key)
            if parent:
                pending.discard(parent)

    async def _poll_loop(self) -> None:
        await self._load_state()
        while not self._stop.is_set():
            try:
                if not self._config_errors():
                    await self._poll_once()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.warning("Feedling bridge poll failed: %s", exc)
            try:
                await asyncio.wait_for(
                    self._stop.wait(),
                    timeout=self.poll_interval,
                )
            except asyncio.TimeoutError:
                pass

    @staticmethod
    def _is_selftest_text(text: str) -> bool:
        parts = text.strip().lstrip("/").split(maxsplit=1)
        return bool(parts and parts[0] == _SELFTEST_COMMAND)

    @filter.event_message_type(filter.EventMessageType.PRIVATE_MESSAGE)
    async def on_private_message(self, event: AstrMessageEvent):
        sender = str(event.get_sender_id() or "").strip()
        if sender not in self.owners:
            return
        text = str(event.message_str or "").strip()
        if self._is_selftest_text(text):
            # Let the command handler below own this event.
            return

        # Stop AstrBot's normal provider/LLM pipeline before the first await.
        # The bridge must remain a door, never a second brain.
        event.call_llm = False
        event.stop_event()
        if not text:
            await event.send(
                MessageChain().message("Feedling 桥接暂只支持文本消息。")
            )
            return
        try:
            umo = str(event.unified_msg_origin or "").strip()
            if not umo:
                raise RuntimeError("AstrBot 事件缺少 unified_msg_origin")
            await self._capture_origin(sender, umo)
            await self._send_user_text(text)
        except Exception as exc:
            logger.error("Feedling bridge inbound failed: %s", exc)
            await event.send(
                MessageChain().message(
                    "Feedling 桥接失败；请发送 /feedling_selftest 查看具体断点。"
                )
            )

    async def _selftest_report(self) -> str:
        lines = ["Feedling Bridge 自检"]
        errors = self._config_errors()
        if errors:
            lines.append("✗ 配置：" + "；".join(errors))
        else:
            lines.append("✓ 配置：URL、API key、owner_qq 已填写")

        keys: FeedlingKeys | None = None
        try:
            keys = await self._fetch_keys(force=True)
            lines.append("✓ ① API/whoami：可达，内容公钥有效")
        except Exception as exc:
            lines.append(
                "✗ ① API/whoami："
                + str(exc)
                + "；检查 feedling_api_url 与 feedling_api_key"
            )

        try:
            await self._history(limit=1)
            lines.append("✓ ② enclave history：解密入口可达")
        except Exception as exc:
            lines.append(
                "✗ ② enclave history："
                + str(exc)
                + "；检查 feedling_enclave_url、TEE 状态与 API key"
            )

        if keys is None:
            lines.append("✗ ③ 共享信封 dry-run：缺少有效 whoami 公钥")
        else:
            try:
                envelope = build_envelope(
                    plaintext=b"feedling-bridge-selftest",
                    owner_user_id=keys.user_id,
                    user_pk_bytes=keys.user_pk,
                    enclave_pk_bytes=keys.enclave_pk,
                    visibility="shared",
                )
                required = {
                    "body_ct",
                    "nonce",
                    "K_user",
                    "K_enclave",
                    "content_pk_fpr",
                }
                if not required.issubset(envelope):
                    raise RuntimeError("信封字段不完整")
                lines.append("✓ ③ 共享信封 dry-run：加密成功（未写入聊天）")
            except Exception as exc:
                lines.append(
                    "✗ ③ 共享信封 dry-run："
                    + str(exc)
                    + "；重装 requirements.txt 中的 cryptography"
                )

        await self._wait_state()
        if self._origins:
            lines.append("✓ ④ QQ 会话地址：已捕获，可主动发送")
        else:
            lines.append(
                "△ ④ QQ 会话地址：尚未捕获；主人先给机器人发一条普通私聊"
            )
        lines.append("本插件不会调用 AstrBot provider/LLM。")
        return "\n".join(lines)

    @filter.command(_SELFTEST_COMMAND)
    async def feedling_selftest(self, event: AstrMessageEvent):
        sender = str(event.get_sender_id() or "").strip()
        if sender not in self.owners:
            return
        event.call_llm = False
        event.stop_event()
        yield event.plain_result(await self._selftest_report())

    async def terminate(self):
        """Stop the poller and close both HTTP clients on disable/uninstall."""
        self._stop.set()
        if self._poll_task and not self._poll_task.done():
            try:
                # Setting the event wakes the normal interval wait immediately.
                # Give an in-flight HTTP call a short graceful window, then
                # cancel so plugin reload/uninstall can never hang indefinitely.
                await asyncio.wait_for(self._poll_task, timeout=2.0)
            except asyncio.TimeoutError:
                self._poll_task.cancel()
                try:
                    await self._poll_task
                except asyncio.CancelledError:
                    pass
        await self._api_http.aclose()
        await self._enclave_http.aclose()
