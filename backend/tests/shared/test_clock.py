"""
Today's date (shared/clock), and the test date a preview can use instead: with CAMPUS_PREVIEW_TODAY a preview on a
developer's machine walks the app as if it were another day, and a plan says so. Production, and any environment
but development, refuses to start with one set, and anything but a plain date stops the start. Tests ignore it.
"""
from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest

from src.config import TestingConfig, _preview_today, get_config
from src.shared.clock.clock import preview_date, today_sast

SAST = ZoneInfo("Africa/Johannesburg")


def test_without_a_test_date_today_is_the_real_day_in_south_africa(app):
    with app.app_context():
        assert preview_date() is None
        assert today_sast() == datetime.now(SAST).date()
    # Outside the app (a job, a script) too.
    assert today_sast() == datetime.now(SAST).date()


def test_a_test_date_is_used_and_can_be_told_apart(app, monkeypatch):
    monkeypatch.setitem(app.config, "PREVIEW_TODAY", date(2026, 8, 1))
    with app.app_context():
        assert preview_date() == date(2026, 8, 1)
        assert today_sast() == date(2026, 8, 1)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("2026-08-01", date(2026, 8, 1)), (" 2026-08-01 ", date(2026, 8, 1)), ("", None), ("   ", None)],
)
def test_the_setting_is_a_plain_date_or_nothing(monkeypatch, raw, expected):
    monkeypatch.setenv("CAMPUS_PREVIEW_TODAY", raw)
    assert _preview_today() == expected


@pytest.mark.parametrize(
    "raw",
    ["yesterday", "2026-13-01", "2026-02-30", "01/08/2026", "2026-08-01T10:00", "2026-08-01; DROP TABLE users", "-1"],
)
def test_anything_but_a_plain_date_stops_the_start(monkeypatch, raw):
    monkeypatch.setenv("CAMPUS_PREVIEW_TODAY", raw)
    with pytest.raises(RuntimeError, match="CAMPUS_PREVIEW_TODAY must be a date"):
        _preview_today()


@pytest.mark.parametrize("env_name", ["production", "staging"])
def test_production_and_unknown_environments_refuse_a_test_date(monkeypatch, env_name):
    monkeypatch.setenv("CAMPUS_PREVIEW_TODAY", "2026-08-01")
    with pytest.raises(RuntimeError, match="CAMPUS_PREVIEW_TODAY is for previews only"):
        get_config(env_name)


def test_tests_ignore_a_test_date(monkeypatch):
    monkeypatch.setenv("CAMPUS_PREVIEW_TODAY", "2026-08-01")
    assert get_config("testing") is TestingConfig
    assert TestingConfig.PREVIEW_TODAY is None
