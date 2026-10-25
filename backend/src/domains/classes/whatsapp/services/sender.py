"""
Sends the bot's replies through Meta's WhatsApp Cloud API: plain text, or text with up to three reply buttons.
Nothing about a reply is logged (not the number, not the words, not the token): a failure logs Meta's status code
only. Tests keep replies in OUTBOX instead (WHATSAPP_FAKE_SEND).
"""
from __future__ import annotations

import logging

import requests
from flask import current_app

from ..constants import BUTTON_BODY_MAX, SEND_TIMEOUT_SECONDS, TEXT_MAX

logger = logging.getLogger("campus_chommie.whatsapp")

#: Tests read what the bot "sent" here: (to, payload) pairs.
OUTBOX: list[tuple[str, dict]] = []


def _cut(text: str, n: int) -> str:
    return text if len(text) <= n else text[: n - 1] + "…"


def text(to: str, body: str) -> None:
    _send(to, {"type": "text", "text": {"preview_url": False, "body": _cut(body, TEXT_MAX)}})


def buttons(to: str, body: str, choices: list[tuple[str, str]]) -> None:
    """choices: (id, title) pairs, at most 3; a title is at most 20 characters."""
    _send(to, {
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": _cut(body, BUTTON_BODY_MAX)},
            "action": {"buttons": [{"type": "reply", "reply": {"id": i, "title": t[:20]}} for i, t in choices[:3]]},
        },
    })


def _send(to: str, message: dict) -> None:
    payload = {"messaging_product": "whatsapp", "recipient_type": "individual", "to": to} | message
    cfg = current_app.config
    if cfg.get("WHATSAPP_FAKE_SEND"):
        OUTBOX.append((to, payload))
        return
    url = f"https://graph.facebook.com/{cfg['WHATSAPP_GRAPH_VERSION']}/{cfg['WHATSAPP_PHONE_NUMBER_ID']}/messages"
    try:
        r = requests.post(url, json=payload, timeout=SEND_TIMEOUT_SECONDS,
                          headers={"Authorization": f"Bearer {cfg['WHATSAPP_ACCESS_TOKEN']}"})
        if r.status_code >= 300:
            logger.warning("WhatsApp reply not sent: Meta answered %s", r.status_code)
    except requests.RequestException as e:
        logger.warning("WhatsApp reply not sent: %s", type(e).__name__)
