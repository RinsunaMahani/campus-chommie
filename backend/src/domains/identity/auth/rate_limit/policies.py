"""
Auth rate limits. Starting numbers, to tune with real traffic.
Storage is in-memory for development; production must use Redis
(RATELIMIT_STORAGE_URI), or each server process counts separately.

Two layers work together:
  * these limits slow down any one source (per IP, or IP + email)
  * the account lockout (auth_service) protects one account from ANY
    source: 5 wrong passwords lock it, wherever they came from
"""
from __future__ import annotations

from flask import request

from src.shared.audit.event_types.auth import AuthAuditEvent
from src.shared.net.client_ip import client_ip_key

LOGIN = "5 per minute"
#: Demo accounts can't be locked by wrong passwords (anyone could lock the
#: judges out), so each IP gets fewer WRONG tries on them instead. Right ones
#: don't count: judges sharing one office network can sign in as often as
#: they need (Rinsuna, 21 Oct 2026). LOGIN's 5 a minute doesn't apply to them.
DEMO_LOGIN = "20 per hour"
#: Every demo sign-in, right or wrong: each right one writes a session row.
DEMO_SIGN_INS = "60 per minute"
REGISTER = "5 per hour"
VERIFY_EMAIL = "10 per 15 minutes"
VERIFY_SIGN_IN = "10 per 15 minutes"  # each code also dies after 5 wrong tries
RESEND_CODE = "3 per 15 minutes"
REFRESH = "30 per minute"
FORGOT_PASSWORD = "3 per hour"
RESET_PASSWORD = "5 per hour"
CHANGE_PASSWORD = "5 per hour"
GOOGLE = "10 per minute"
GOOGLE_LINK = "5 per minute"
CLOSE_ACCOUNT = "3 per hour"
DELETE_ACCOUNT = "3 per hour"
EXPORT_DATA = "5 per hour"
# Signed-in routes still get a limit (every route does: brief section 10),
# counted per user and generous enough that a real person never meets it.
SESSIONS = "60 per minute"
LOGOUT = "30 per minute"
LOGOUT_OTHERS = "10 per minute"


def login_key_func() -> str:
    """IP + the email being tried, not IP alone.

    Students in one residence or on one campus Wi-Fi share
    an IP: keyed on IP alone they'd lock each other out. Keyed on IP +
    email, each person gets their own allowance, while repeated tries on
    ONE account from ONE place are still capped. Guessing across many
    accounts is the account lockout's job, not this one's.
    """
    payload = request.get_json(silent=True) or {}
    email = payload.get("email")
    email = email.strip().lower() if isinstance(email, str) else ""
    return f"{client_ip_key()}:{email}" if email else client_ip_key()


def not_a_demo_login() -> bool:
    """DEMO_LOGIN's exemption: true unless the email being tried is a demo account's."""
    from src.domains.identity.accounts.services import account_service

    payload = request.get_json(silent=True) or {}
    email = payload.get("email")
    user = account_service.find_by_email(email) if isinstance(email, str) and email.strip() else None
    return user is None or not user.is_demo


def a_demo_login() -> bool:
    """LOGIN's exemption: demo emails have their own two limits."""
    return not not_a_demo_login()


def wrong_password(response) -> bool:
    """DEMO_LOGIN counts a try only when it was refused."""
    return response.status_code == 401


# Which audit event a tripped limit records. Keys are Flask endpoint names
# ("api.<view function>": the routes live on the api blueprint).
RATE_LIMIT_AUDIT_EVENTS = {
    "api.login": AuthAuditEvent.LOGIN_RATE_LIMITED,
    "api.register": AuthAuditEvent.REGISTER_RATE_LIMITED,
    "api.verify_email": AuthAuditEvent.OTP_VERIFY_RATE_LIMITED,
    "api.resend_code": AuthAuditEvent.OTP_REQUEST_RATE_LIMITED,
    "api.verify_sign_in": AuthAuditEvent.OTP_VERIFY_RATE_LIMITED,
    "api.resend_sign_in_code": AuthAuditEvent.OTP_REQUEST_RATE_LIMITED,
    "api.refresh": AuthAuditEvent.REFRESH_RATE_LIMITED,
    "api.forgot_password": AuthAuditEvent.PASSWORD_RESET_REQUEST_RATE_LIMITED,
    "api.reset_password": AuthAuditEvent.PASSWORD_RESET_RATE_LIMITED,
    "api.change_password": AuthAuditEvent.PASSWORD_RESET_RATE_LIMITED,
    "api.google_sign_in": AuthAuditEvent.LOGIN_RATE_LIMITED,
    "api.link_google": AuthAuditEvent.LOGIN_RATE_LIMITED,
}
