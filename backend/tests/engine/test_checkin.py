"""Unit tests for weekly money check-in and streak tracking.

Streaks must be encouraging and welcoming, never shaming.
"""
from __future__ import annotations

from datetime import date

from campus_engine.checkin import (
    checkin_streak,
    checkin_window,
    is_checkin_day,
    week_ending_date,
)


def test_week_ending_date_sunday_default():
    # 2026-10-18 is a Sunday
    sun = date(2026, 10, 18)
    assert week_ending_date(sun, "sunday") == sun

    # 2026-10-12 is a Monday; ends on Sunday 2026-10-18
    mon = date(2026, 10, 12)
    assert week_ending_date(mon, "sunday") == sun

    # 2026-10-14 is a Wednesday; ends on Sunday 2026-10-18
    wed = date(2026, 10, 14)
    assert week_ending_date(wed, "sunday") == sun


def test_week_ending_date_custom_day():
    # 2026-10-16 is a Friday
    fri = date(2026, 10, 16)
    assert week_ending_date(fri, "friday") == fri

    # 2026-10-17 is a Saturday; next Friday is 2026-10-23
    sat = date(2026, 10, 17)
    assert week_ending_date(sat, "friday") == date(2026, 10, 23)


def test_checkin_window():
    sun = date(2026, 10, 18)
    start, end = checkin_window(sun)
    assert start == date(2026, 10, 12)
    assert end == sun
    assert (end - start).days == 6  # 7 days inclusive


def test_is_checkin_day():
    # 2026-10-18 is Sunday
    sun = date(2026, 10, 18)
    assert is_checkin_day(sun, "sunday") is True
    assert is_checkin_day(sun, "monday") is False

    # 2026-10-19 is Monday
    mon = date(2026, 10, 19)
    assert is_checkin_day(mon, "monday") is True
    assert is_checkin_day(mon, "sunday") is False


def test_streak_zero_welcome_back():
    today = date(2026, 10, 18)
    res = checkin_streak([], today, "sunday")
    assert res.weeks == 0
    assert "Welcome back" in res.line
    assert "broke" not in res.line
    assert "lost" not in res.line


def test_streak_one_week():
    today = date(2026, 10, 18)
    # Checked in this Sunday
    res = checkin_streak([today], today, "sunday")
    assert res.weeks == 1
    assert res.line == "Welcome back: 1 week in a row."


def test_streak_multiple_consecutive_weeks():
    today = date(2026, 10, 18)
    w1 = date(2026, 10, 4)
    w2 = date(2026, 10, 11)
    w3 = date(2026, 10, 18)
    res = checkin_streak([w1, w2, w3], today, "sunday")
    assert res.weeks == 3
    assert res.line == "3 weeks in a row."


def test_streak_preserved_during_current_week_before_checking_in():
    # Today is Wednesday 2026-10-14, week ends Sun 2026-10-18.
    # Student checked in last week (Sun 2026-10-11) and week before (Sun 2026-10-04).
    today = date(2026, 10, 14)
    w1 = date(2026, 10, 4)
    w2 = date(2026, 10, 11)
    res = checkin_streak([w1, w2], today, "sunday")
    assert res.weeks == 2
    assert res.line == "2 weeks in a row."


def test_streak_resets_encouragingly_if_missed_previous_week():
    # Today is Sunday 2026-10-18.
    # Student checked in on 2026-10-04, but missed 2026-10-11 and hasn't checked in today.
    today = date(2026, 10, 18)
    w1 = date(2026, 10, 4)
    res = checkin_streak([w1], today, "sunday")
    assert res.weeks == 0
    assert "Welcome back" in res.line

