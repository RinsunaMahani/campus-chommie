"""
Rate-limit keys for routes that count PER USER, not per IP.

Students on one campus Wi-Fi, or a residence behind one router, share an
IP; keyed on the IP they'd use up each other's allowance. The limiter
checks before @auth_required runs, so the key reads the signed-in user
from the token itself; a missing or bad token falls back to the IP (that
request is refused by @auth_required anyway).

    @limiter.limit("120 per minute", key_func=per_user)
"""
from __future__ import annotations

from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from src.shared.net.client_ip import client_ip_key


def per_user() -> str:
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
    except Exception:  # noqa: BLE001 -- expired or broken token: count by IP
        identity = None
    return f"user:{identity}" if identity else f"ip:{client_ip_key()}"
