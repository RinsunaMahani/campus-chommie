"""Today in South Africa (SAST), or a preview's test date.

CAMPUS_PREVIEW_TODAY=2026-08-01 lets a preview on a developer's machine walk the app as if it were that day, for
example while applications are open. Only DevelopmentConfig reads it: production, and any other environment,
refuses to start with it set (src/config.py), and a plan says when its dates come from a test date.
"""
from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

from flask import current_app, has_app_context

TIMEZONE = "Africa/Johannesburg"


def preview_date() -> date | None:
    """The preview's test date, or None on the real date."""
    return current_app.config.get("PREVIEW_TODAY") if has_app_context() else None


def today_sast() -> date:
    """Today in South Africa, or the preview's test date."""
    return preview_date() or datetime.now(ZoneInfo(TIMEZONE)).date()
