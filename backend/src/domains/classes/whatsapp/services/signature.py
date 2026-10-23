"""
The bot's secrets at work: whether it's switched on, Meta's webhook handshake, the signature on every message, and
the keyed hashes numbers, codes and message ids are stored as. Every comparison is constant-time.
"""
from __future__ import annotations

import hashlib
import hmac
import re

from flask import current_app

_SECRETS = ("WHATSAPP_VERIFY_TOKEN", "WHATSAPP_APP_SECRET", "WHATSAPP_ACCESS_TOKEN", "WHATSAPP_PHONE_NUMBER_ID",
            "WHATSAPP_PHONE_KEY")
_SIGNATURE = re.compile(r"^sha256=([0-9a-f]{64})$")


def available() -> bool:
    """All five secrets set: the bot is on."""
    return all(current_app.config.get(name) for name in _SECRETS)


def handshake_ok(mode: str, token: str) -> bool:
    """Meta's subscribe check: the verify token we gave Meta, sent back."""
    expected = current_app.config["WHATSAPP_VERIFY_TOKEN"].encode()
    return mode == "subscribe" and hmac.compare_digest(token.encode(), expected)


def signed(raw_body: bytes, header: str | None) -> bool:
    """X-Hub-Signature-256: HMAC-SHA256 of the raw body with the app secret, as `sha256=<hex>`."""
    m = _SIGNATURE.match(header or "")
    if m is None:
        return False
    key = current_app.config["WHATSAPP_APP_SECRET"].encode()
    expected = hmac.new(key, raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(m.group(1), expected)


def _keyed(kind: str, value: str) -> str:
    key = current_app.config["WHATSAPP_PHONE_KEY"].encode()
    return hmac.new(key, f"{kind}:{value}".encode(), hashlib.sha256).hexdigest()


def phone_hash(digits: str) -> str:
    return _keyed("phone", digits)


def code_hash(code: str) -> str:
    return _keyed("code", code)


def message_hash(message_id: str) -> str:
    return _keyed("message", message_id)
