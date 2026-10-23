"""Weekly money check-in and streak tracking.

The student can check in once a week (entering the week's total spending or skipping).
The streak counts consecutive weeks checked in.
Wording is always encouraging and welcoming, never shaming: "3 weeks in a row",
"Welcome back". Never "you broke your streak".
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

WEEKDAY_MAP = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


@dataclass
class CheckinStreak:
    weeks: int
    line: str


def week_ending_date(d: date, checkin_day: str = "sunday") -> date:
    """The end date (inclusive) of the 7-day check-in period containing `d`."""
    target_wd = WEEKDAY_MAP.get(checkin_day.lower(), 6)
    delta = (target_wd - d.weekday()) % 7
    return d + timedelta(days=delta)


def checkin_window(end_date: date) -> tuple[date, date]:
    """The 7-day date range [start_date, end_date] for a given week end."""
    return end_date - timedelta(days=6), end_date


def is_checkin_day(today: date, checkin_day: str = "sunday") -> bool:
    """True if today is the student's designated check-in day of the week."""
    target_wd = WEEKDAY_MAP.get(checkin_day.lower(), 6)
    return today.weekday() == target_wd


def checkin_streak(
    checked_in_weeks: list[date],
    today: date,
    checkin_day: str = "sunday",
) -> CheckinStreak:
    """Calculate the consecutive weekly check-in streak.

    Encouraging, welcoming wording: "3 weeks in a row", "Welcome back".
    Never shames or says "you broke your streak".
    """
    checked_set = set(checked_in_weeks)
    curr_week_end = week_ending_date(today, checkin_day)

    if curr_week_end in checked_set:
        check_date = curr_week_end
    else:
        # Not checked in yet this week; check previous week
        check_date = curr_week_end - timedelta(days=7)

    streak = 0
    while check_date in checked_set:
        streak += 1
        check_date -= timedelta(days=7)

    if streak == 0:
        line = "Welcome back: check in once a week to keep your runway accurate."
    elif streak == 1:
        line = "Welcome back: 1 week in a row."
    else:
        line = f"{streak} weeks in a row."

    return CheckinStreak(weeks=streak, line=line)

