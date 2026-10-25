"""
Verifies a Google ID token on OUR server. The app never tells us who the
user is; Google's signed token does, and we check it ourselves:

  * signature, against Google's published keys (fetched with a short
    timeout and kept as long as Google says they stay fresh, up to an hour:
    google-auth itself would fetch them on every sign-in and wait up to
    two minutes for a slow answer)
  * issuer is Google, and the token hasn't expired
  * audience is one of OUR client IDs (a token minted for another app is
    refused)
  * Google has verified the email

Tests replace `verify` with a fake; nothing else in the code talks to Google.
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass
from typing import Optional

from flask import current_app

from src.core.exceptions import AppError

GOOGLE_ISSUERS = {"accounts.google.com", "https://accounts.google.com"}
KEYS_TIMEOUT_SECONDS = 5
KEYS_FRESH_MAX_SECONDS = 3600
_MAX_AGE = re.compile(r"max-age=(\d+)")


@dataclass(frozen=True)
class GoogleClaims:
    sub: str  # Google's stable user id
    email: str
    name: Optional[str]


class GoogleNotConfigured(AppError):
    status_code = 503
    code = "GOOGLE_NOT_CONFIGURED"


class InvalidGoogleToken(AppError):
    status_code = 401
    code = "INVALID_GOOGLE_TOKEN"


class GoogleUnreachable(AppError):
    status_code = 503
    code = "GOOGLE_UNREACHABLE"


class _KeysRequest:
    """google-auth's HTTP request, with a short timeout and Google's keys kept while fresh. While Google is slow, a
    few sign-ins could otherwise hold every server thread for two minutes each."""

    def __init__(self, inner=None):
        self._inner = inner
        self._kept: dict[str, tuple[float, object]] = {}

    def __call__(self, url, method="GET", **kwargs):
        kept = self._kept.get(url)
        if method == "GET" and kept and kept[0] > time.monotonic():
            return kept[1]
        if self._inner is None:
            from google.auth.transport import requests as google_requests

            self._inner = google_requests.Request()
        kwargs["timeout"] = KEYS_TIMEOUT_SECONDS
        response = self._inner(url, method=method, **kwargs)
        if method == "GET" and response.status == 200:
            m = _MAX_AGE.search((getattr(response, "headers", None) or {}).get("cache-control", ""))
            fresh = min(int(m.group(1)), KEYS_FRESH_MAX_SECONDS) if m else 0
            if fresh:
                self._kept[url] = (time.monotonic() + fresh, response)
        return response


_keys = _KeysRequest()


def verify(id_token_value: str) -> GoogleClaims:
    client_ids = current_app.config.get("GOOGLE_CLIENT_IDS") or []
    if not client_ids:
        raise GoogleNotConfigured("Google sign-in isn't available yet.")

    from google.auth.exceptions import TransportError
    from google.oauth2 import id_token

    try:
        # audience=None here, then checked against ALL our client IDs below
        # (Android and web tokens carry different ones).
        claims = id_token.verify_oauth2_token(id_token_value, _keys, audience=None)
    except TransportError:
        # Google's keys out of reach (slow or down): say so, never a 500.
        raise GoogleUnreachable("We can't reach Google right now. Try again in a minute, or sign in with your password.") from None
    except ValueError:
        raise InvalidGoogleToken("Google sign-in failed. Please try again.") from None

    if claims.get("iss") not in GOOGLE_ISSUERS or claims.get("aud") not in client_ids:
        raise InvalidGoogleToken("Google sign-in failed. Please try again.")
    if not claims.get("email") or claims.get("email_verified") is not True:
        raise InvalidGoogleToken("Your Google account's email isn't verified.")
    return GoogleClaims(sub=str(claims["sub"]), email=claims["email"], name=claims.get("name"))
