#!/usr/bin/env python3
"""Real test-environment envelope round trip with hard account cleanup.

Creates one throwaway account on test-api.feedling.app, seals and sends one
shared chat message, reads its plaintext back through enclave history, then
hard-deletes the account in ``finally``.

Run from the plugin directory:
    python tests/real_roundtrip.py
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
import uuid
from pathlib import Path
from urllib.parse import urlparse

import httpx
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

PLUGIN_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN_DIR))

from content_encryption import build_envelope


DEFAULT_API = "https://test-api.feedling.app"
DEFAULT_ENCLAVE = (
    "https://173c7f49aeb54acb424676b17b17f78e5e2b2938-5003s."
    "dstack-pha-prod9.phala.network"
)
_ALLOWED_API_HOSTS = {"test-api.feedling.app"}
_ORPHAN_DIR = Path.home() / ".feedling-e2e-orphans"


def _refuse_non_test(api_url: str) -> None:
    host = (urlparse(api_url).hostname or "").lower()
    if host not in _ALLOWED_API_HOSTS:
        raise RuntimeError(
            f"real_roundtrip only permits the Feedling test API, got {api_url}"
        )


def _write_orphan_manifest(user_id: str, api_key: str, api_url: str) -> Path:
    """Leave 0600 cleanup credentials if the process dies before finally."""
    _ORPHAN_DIR.mkdir(parents=True, exist_ok=True)
    path = _ORPHAN_DIR / f"astrbot-bridge-{user_id}.json"
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "w") as handle:
            json.dump(
                {"api_url": api_url, "user_id": user_id, "api_key": api_key},
                handle,
            )
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise
    return path


def _public_bytes(private_key: X25519PrivateKey) -> bytes:
    return private_key.public_key().public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw,
    )


def run(api_url: str, enclave_url: str, timeout: float) -> None:
    _refuse_non_test(api_url)
    api_url = api_url.rstrip("/")
    enclave_url = enclave_url.rstrip("/")
    private_key = X25519PrivateKey.generate()
    public_key = _public_bytes(private_key)
    api_key = ""
    user_id = ""
    manifest: Path | None = None

    with httpx.Client(timeout=30.0) as api:
        try:
            register = api.post(
                f"{api_url}/v1/users/register",
                json={
                    "public_key": base64.b64encode(public_key).decode("ascii"),
                    "archive_language": "zh-Hans",
                    "label": "e2e-astrbot-feedling-bridge",
                },
            )
            register.raise_for_status()
            registration = register.json()
            user_id = str(registration["user_id"])
            api_key = str(registration["api_key"])
            manifest = _write_orphan_manifest(user_id, api_key, api_url)
            headers = {"X-API-Key": api_key}

            whoami = api.get(f"{api_url}/v1/users/whoami", headers=headers)
            whoami.raise_for_status()
            who = whoami.json()
            enclave_pk = bytes.fromhex(
                str(who.get("enclave_content_public_key_hex") or "")
            )
            if len(enclave_pk) != 32:
                raise RuntimeError("whoami returned an invalid enclave content key")

            marker = f"astrbot-bridge-roundtrip-{uuid.uuid4()}"
            envelope = build_envelope(
                plaintext=marker.encode("utf-8"),
                owner_user_id=user_id,
                user_pk_bytes=public_key,
                enclave_pk_bytes=enclave_pk,
                visibility="shared",
            )
            logical_id = str(uuid.uuid4())
            sent = api.post(
                f"{api_url}/v1/chat/message",
                headers=headers,
                json={
                    "envelope": envelope,
                    "client_msg_id": logical_id,
                    "content_type": "text",
                },
            )
            sent.raise_for_status()
            sent_body = sent.json()
            message_id = str(sent_body["id"])
            sent_ts = float(sent_body["ts"])

            deadline = time.monotonic() + timeout
            found = None
            # verify=False is intentionally scoped to the dstack enclave only.
            with httpx.Client(timeout=20.0, verify=False) as enclave:
                while time.monotonic() < deadline:
                    history = enclave.get(
                        f"{enclave_url}/v1/chat/history",
                        headers=headers,
                        params={"since": max(0.0, sent_ts - 1), "limit": 50},
                    )
                    history.raise_for_status()
                    for message in history.json().get("messages") or []:
                        if str(message.get("id") or "") == message_id:
                            found = message
                            break
                    if found is not None:
                        break
                    time.sleep(2)

            if found is None:
                raise RuntimeError(
                    f"message {message_id} was not returned by enclave within {timeout}s"
                )
            if str(found.get("content") or "") != marker:
                raise RuntimeError("enclave returned the message but plaintext mismatched")
            print(
                "PASS shared-envelope send -> enclave history decrypt "
                f"(user={user_id}, message={message_id})"
            )
        finally:
            if api_key:
                cleanup = api.post(
                    f"{api_url}/v1/account/reset",
                    headers={"X-API-Key": api_key},
                    json={"confirm": "delete-all-data"},
                )
                cleanup.raise_for_status()
                if manifest is not None:
                    manifest.unlink(missing_ok=True)
                print(f"PASS test-account cleanup (user={user_id})")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--api-url",
        default=os.environ.get("FEEDLING_TEST_API_URL", DEFAULT_API),
    )
    parser.add_argument(
        "--enclave-url",
        default=os.environ.get("FEEDLING_TEST_ENCLAVE_URL", DEFAULT_ENCLAVE),
    )
    parser.add_argument("--timeout", type=float, default=45.0)
    args = parser.parse_args()
    run(args.api_url, args.enclave_url, args.timeout)


if __name__ == "__main__":
    main()
