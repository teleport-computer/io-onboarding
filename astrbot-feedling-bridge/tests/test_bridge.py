from __future__ import annotations

import asyncio
import base64
import json
from pathlib import Path
from unittest.mock import AsyncMock

import httpx
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

import main


class FakeContext:
    def __init__(self):
        self.sent = []

    async def send_message(self, umo, chain):
        self.sent.append((umo, list(chain.parts)))


class FakeEvent:
    def __init__(self, sender="10001", text="你好", umo="aiocqhttp:FriendMessage:10001"):
        self._sender = sender
        self.message_str = text
        self.unified_msg_origin = umo
        self.call_llm = True
        self.stopped = False
        self.sent = []

    def get_sender_id(self):
        return self._sender

    def stop_event(self):
        self.stopped = True

    async def send(self, chain):
        self.sent.append(list(chain.parts))

    def plain_result(self, text):
        return text


class FakeResponse:
    def __init__(self, status_code=200, body=None):
        self.status_code = status_code
        self._body = body or {}

    def json(self):
        return self._body

    def raise_for_status(self):
        if self.status_code >= 400:
            request = httpx.Request("POST", "https://test-api.feedling.app/")
            response = httpx.Response(self.status_code, request=request, json=self._body)
            raise httpx.HTTPStatusError("test error", request=request, response=response)


def _config(**overrides):
    config = {
        "feedling_api_url": "https://test-api.feedling.app",
        "feedling_api_key": "test-key",
        "feedling_enclave_url": "https://enclave.example",
        "owner_qq": ["10001"],
        "poll_interval": 20,
        "forward_app_messages": True,
    }
    config.update(overrides)
    return config


async def _plugin(**overrides):
    plugin = main.FeedlingBridge(FakeContext(), _config(**overrides))
    await plugin._wait_state()
    plugin._stop.set()
    await asyncio.wait_for(plugin._poll_task, timeout=1)
    return plugin


def _public_key() -> bytes:
    return X25519PrivateKey.generate().public_key().public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw,
    )


@pytest.mark.asyncio
async def test_owner_message_stops_astrbot_llm_and_posts_without_waiting():
    plugin = await _plugin()
    try:
        plugin._capture_origin = AsyncMock()
        plugin._send_user_text = AsyncMock(return_value={"id": "m1", "ts": 1})
        event = FakeEvent(text="今晚聊聊")

        await plugin.on_private_message(event)

        assert event.stopped is True
        assert event.call_llm is False
        plugin._capture_origin.assert_awaited_once_with(
            "10001", "aiocqhttp:FriendMessage:10001"
        )
        plugin._send_user_text.assert_awaited_once_with("今晚聊聊")
        assert event.sent == []
    finally:
        await plugin.terminate()


@pytest.mark.asyncio
async def test_non_owner_is_ignored_and_cannot_inject_feedling():
    plugin = await _plugin()
    try:
        plugin._capture_origin = AsyncMock()
        plugin._send_user_text = AsyncMock()
        event = FakeEvent(sender="outsider", text="恶意提示词")

        await plugin.on_private_message(event)

        assert event.stopped is False
        plugin._capture_origin.assert_not_awaited()
        plugin._send_user_text.assert_not_awaited()
    finally:
        await plugin.terminate()


@pytest.mark.asyncio
async def test_owner_non_text_message_is_stopped_with_clear_feedback():
    plugin = await _plugin()
    try:
        plugin._capture_origin = AsyncMock()
        plugin._send_user_text = AsyncMock()
        event = FakeEvent(text="")

        await plugin.on_private_message(event)

        assert event.stopped is True
        assert event.call_llm is False
        assert event.sent == [["Feedling 桥接暂只支持文本消息。"]]
        plugin._capture_origin.assert_not_awaited()
        plugin._send_user_text.assert_not_awaited()
    finally:
        await plugin.terminate()


@pytest.mark.asyncio
async def test_selftest_command_is_not_forwarded_by_general_handler():
    plugin = await _plugin()
    try:
        plugin._send_user_text = AsyncMock()
        event = FakeEvent(text="/feedling_selftest")
        await plugin.on_private_message(event)
        assert event.stopped is False
        plugin._send_user_text.assert_not_awaited()
    finally:
        await plugin.terminate()


@pytest.mark.asyncio
async def test_content_key_mismatch_refetches_and_reseals_same_logical_send():
    plugin = await _plugin()
    try:
        old = main.FeedlingKeys("usr_test", _public_key(), _public_key())
        new = main.FeedlingKeys("usr_test", _public_key(), _public_key())
        plugin._fetch_keys = AsyncMock(side_effect=[old, new])
        posts = []

        async def post(payload):
            posts.append(payload)
            if len(posts) == 1:
                return FakeResponse(
                    409,
                    {"error": "content_pk_fpr_mismatch"},
                )
            return FakeResponse(200, {"id": "parent-1", "ts": 10})

        plugin._post_chat_payload = post
        result = await plugin._send_user_text("key rotated")

        assert result["id"] == "parent-1"
        assert plugin._fetch_keys.await_args_list[1].kwargs == {"force": True}
        assert posts[0]["client_msg_id"] == posts[1]["client_msg_id"]
        assert (
            posts[0]["envelope"]["content_pk_fpr"]
            != posts[1]["envelope"]["content_pk_fpr"]
        )
        assert "parent-1" in plugin._pending_parents
    finally:
        await plugin.terminate()


@pytest.mark.asyncio
async def test_capture_origin_seeds_cursor_before_enabling_delivery():
    plugin = await _plugin()
    try:
        plugin._history = AsyncMock(
            return_value=[{"id": "old", "role": "agent", "ts": 88.0, "content": "old"}]
        )
        await plugin._capture_origin("10001", "qq:private:10001")
        assert plugin._cursor == 88.0
        assert plugin._origins == {"10001": "qq:private:10001"}
    finally:
        await plugin.terminate()


@pytest.mark.asyncio
async def test_poll_forwards_only_assistant_roles_and_advances_all_rows():
    plugin = await _plugin()
    try:
        plugin._origins = {"10001": "qq:private:10001"}
        plugin._history = AsyncMock(
            return_value=[
                {"id": "u1", "role": "user", "ts": 1, "content": "echo"},
                {"id": "a1", "role": "agent", "ts": 2, "content": "在的"},
                {"id": "s1", "role": "system", "ts": 3, "content": "notice"},
            ]
        )
        plugin._send_active_text = AsyncMock()

        await plugin._poll_once()

        plugin._send_active_text.assert_awaited_once_with("qq:private:10001", "在的")
        assert plugin._cursor == 3
        assert set(plugin._processed_ids) == {"u1", "a1", "s1"}
    finally:
        await plugin.terminate()


@pytest.mark.asyncio
async def test_forward_app_messages_false_requires_bridged_parent():
    plugin = await _plugin(forward_app_messages=False)
    try:
        plugin._origins = {"10001": "qq:private:10001"}
        plugin._pending_parents = ["qq-parent"]
        plugin._history = AsyncMock(
            return_value=[
                {
                    "id": "app-reply",
                    "role": "agent",
                    "ts": 1,
                    "content": "app",
                    "reply_to_message_id": "app-parent",
                },
                {
                    "id": "qq-reply",
                    "role": "agent",
                    "ts": 2,
                    "content": "qq",
                    "reply_to_message_id": "qq-parent",
                },
            ]
        )
        plugin._send_active_text = AsyncMock()

        await plugin._poll_once()

        plugin._send_active_text.assert_awaited_once_with("qq:private:10001", "qq")
        assert "qq-parent" not in plugin._pending_parents
        assert plugin._cursor == 2
    finally:
        await plugin.terminate()


@pytest.mark.asyncio
async def test_active_send_failure_keeps_cursor_and_message_retryable():
    plugin = await _plugin()
    try:
        plugin._origins = {"10001": "qq:private:10001"}
        plugin._cursor = 5
        plugin._history = AsyncMock(
            return_value=[{"id": "a1", "role": "agent", "ts": 6, "content": "reply"}]
        )
        plugin._send_active_text = AsyncMock(side_effect=RuntimeError("QQ down"))

        with pytest.raises(RuntimeError, match="QQ down"):
            await plugin._poll_once()

        assert plugin._cursor == 5
        assert "a1" not in plugin._processed_ids
    finally:
        await plugin.terminate()


@pytest.mark.asyncio
async def test_delivery_ledger_avoids_duplicate_to_first_of_multiple_owners():
    plugin = await _plugin(owner_qq=["10001", "10002"])
    try:
        plugin._origins = {
            "10001": "qq:private:10001",
            "10002": "qq:private:10002",
        }
        calls = []

        async def flaky(umo, _text):
            calls.append(umo)
            if umo.endswith("10002") and calls.count(umo) == 1:
                raise RuntimeError("second owner offline")

        plugin._send_active_text = flaky
        message = {"id": "a1", "role": "agent", "ts": 2, "content": "reply"}
        with pytest.raises(RuntimeError):
            await plugin._deliver_assistant(message, sorted(plugin._origins.values()))
        await plugin._deliver_assistant(message, sorted(plugin._origins.values()))

        assert calls == [
            "qq:private:10001",
            "qq:private:10002",
            "qq:private:10002",
        ]
    finally:
        await plugin.terminate()


@pytest.mark.asyncio
async def test_selftest_reports_api_enclave_envelope_and_missing_origin():
    plugin = await _plugin()
    try:
        keys = main.FeedlingKeys("usr_test", _public_key(), _public_key())
        plugin._fetch_keys = AsyncMock(return_value=keys)
        plugin._history = AsyncMock(return_value=[])

        report = await plugin._selftest_report()

        assert "✓ ① API/whoami" in report
        assert "✓ ② enclave history" in report
        assert "✓ ③ 共享信封 dry-run" in report
        assert "△ ④ QQ 会话地址" in report
        assert "不会调用 AstrBot provider/LLM" in report
    finally:
        await plugin.terminate()


@pytest.mark.asyncio
async def test_poll_interval_has_ten_second_floor_and_string_owner_support():
    plugin = await _plugin(owner_qq="10001, 10002", poll_interval=1)
    try:
        assert plugin.owners == {"10001", "10002"}
        assert plugin.poll_interval == 10
    finally:
        await plugin.terminate()


def test_schema_and_metadata_declare_required_contract():
    root = Path(main.__file__).resolve().parent
    schema = json.loads((root / "_conf_schema.json").read_text())
    assert set(schema) == {
        "feedling_api_url",
        "feedling_api_key",
        "feedling_enclave_url",
        "owner_qq",
        "poll_interval",
        "forward_app_messages",
    }
    metadata = (root / "metadata.yaml").read_text()
    assert 'astrbot_version: ">=4.9.2,<5"' in metadata
    assert "cryptography" in (root / "requirements.txt").read_text()
