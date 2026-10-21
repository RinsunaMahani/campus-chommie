"""A timetable read back in plain words: clashes found and said, and the week added up."""
from __future__ import annotations

from datetime import time

from campus_engine.timetable import Slot, clashes, summary


def slot(i, module, kind, day, start, end):
    return Slot(str(i), module, kind, day, time(*start), time(*end))


def test_overlapping_classes_on_the_same_day_clash_and_say_when():
    found = clashes([
        slot(1, "ANA201", "lecture", 0, (8, 0), (10, 0)),
        slot(2, "PHY121", "practical", 0, (9, 0), (12, 0)),
        slot(3, "BCH111", "lecture", 1, (9, 0), (10, 0)),  # another day: no clash
        slot(4, "BCH111", "tutorial", 0, (10, 0), (11, 0)),  # starts as ANA201 ends: no clash with it
    ])
    assert [c.line for c in found] == [
        "ANA201 lecture and PHY121 practical overlap on Monday, 09:00 to 10:00.",
        "PHY121 practical and BCH111 tutorial overlap on Monday, 10:00 to 11:00.",
    ]


def test_the_week_in_words():
    lines = summary([
        slot(1, "ANA201", "lecture", 0, (8, 0), (9, 40)),
        slot(2, "PHY121", "practical", 2, (14, 0), (16, 40)),
        slot(3, "BCH111", "tutorial", 2, (9, 0), (9, 50)),
    ])
    assert lines == [
        "3 classes a week, 5 hours 10 minutes in all, on Monday and Wednesday.",
        "Your longest day is Wednesday: 3 hours 30 minutes of classes.",
    ]


def test_an_empty_timetable_says_what_to_do():
    assert summary([]) == ["Your timetable is empty. Add your classes to see your week."]


def test_clashes_are_added_to_the_summary():
    lines = summary([slot(1, "A1", "lecture", 4, (8, 0), (9, 0)), slot(2, "B2", "other", 4, (8, 30), (9, 30))])
    assert lines[-1] == "1 clash to sort out: A1 lecture and B2 class overlap on Friday, 08:30 to 09:00."
