"""A labelled set of realistic rep messages. Grow it to about 50 before the event."""
from datetime import date, datetime, time

import pytest

from campus_engine.extraction import apply_change, extract, find_existing
from campus_engine.workload import AcademicEvent

SENT = date(2026, 10, 12)  # a Monday
MODULES = ["ANA201", "PHY121", "BCH111"]

CASES = [
    (
        "Test 2 moved to Thursday 10:00, Room B4",
        dict(kind="test", title="Test 2", on=date(2026, 10, 15), at=time(10, 0), venue="Room B4", change="moved"),
    ),
    (
        "ANA201 assignment 3 due 23/10 at 23:59, worth 15%",
        dict(kind="assignment", title="Assignment 3", module="ANA201", on=date(2026, 10, 23), at=time(23, 59), weighting=15),
    ),
    ("PHY121 quiz cancelled", dict(kind="quiz", module="PHY121", change="cancelled", on=None)),
    (
        "Reminder: semester test on 4 November 2026, 08h00, venue Hall 3",
        dict(kind="test", title="Semester test", on=date(2026, 11, 4), at=time(8, 0), venue="Hall 3"),
    ),
    ("Practical tomorrow 2pm lab C12", dict(kind="practical", on=date(2026, 10, 13), at=time(14, 0), venue="Lab C12")),
    ("bch 111 quiz on 20 Oct, 10.30am", dict(kind="quiz", module="BCH111", on=date(2026, 10, 20), at=time(10, 30))),
    ("Exam timetable: ANA201 exam 2026-11-09 09:00", dict(kind="exam", module="ANA201", on=date(2026, 11, 9), at=time(9, 0))),
    ("Assignment 1 submission Oct 30", dict(kind="assignment", title="Assignment 1", on=date(2026, 10, 30))),
]


@pytest.mark.parametrize("message,expected", CASES, ids=[c[0][:30] for c in CASES])
def test_labelled_messages(message, expected):
    c = extract(message, SENT, MODULES)
    for name, value in expected.items():
        assert getattr(c, name) == value, f"{name}: got {getattr(c, name)!r}"


def test_percentages_are_not_read_as_dates():
    c = extract("Quiz worth 7.5% of the mark", SENT, MODULES)
    assert c.weighting == 7.5
    assert c.on is None


def test_missing_module_and_date_are_flagged():
    c = extract("Test 2 next week", SENT, MODULES)
    assert set(c.needs_check()) >= {"module", "on"}


def test_next_weekday_is_ambiguous_and_flagged():
    c = extract("ANA201 test next Thursday", SENT, MODULES)
    assert c.on == date(2026, 10, 22)
    assert "on" in c.needs_check()


def test_past_dates_are_flagged():
    c = extract("ANA201 test on 5 Oct", SENT, MODULES)
    assert "on" in c.needs_check()
    assert c.notes


def test_year_rolls_over_for_early_next_year_dates():
    c = extract("ANA201 test on 15 Jan", date(2026, 12, 10), MODULES)
    assert c.on == date(2027, 1, 15)


def test_impossible_dates_are_dropped():
    c = extract("ANA201 test 31/02", SENT, MODULES)
    assert c.on is None


def test_unknown_module_code_is_low_confidence():
    c = extract("XYZ301 test on 20 Oct", SENT, MODULES)
    assert c.module == "XYZ301"
    assert "module" in c.needs_check()


def test_change_updates_the_matching_event():
    events = [
        AcademicEvent("Test 2", "test", datetime(2026, 10, 14, 9, 0), "ANA201", venue="Room A1"),
        AcademicEvent("Quiz 1", "quiz", datetime(2026, 10, 16, 9, 0), "PHY121"),
    ]
    c = extract("ANA201 Test 2 moved to Thursday 10:00, Room B4", SENT, MODULES)
    target = find_existing(c, events)
    assert target is events[0]
    changes = apply_change(c, target)
    assert target.starts == datetime(2026, 10, 15, 10, 0)
    assert target.venue == "Room B4"
    assert len(changes) == 3


def test_cancellation_marks_the_event():
    events = [AcademicEvent("Quiz", "quiz", datetime(2026, 10, 16, 9, 0), "PHY121")]
    c = extract("PHY121 quiz cancelled", SENT, MODULES)
    apply_change(c, find_existing(c, events))
    assert events[0].cancelled


def test_to_event_needs_kind_and_date():
    with pytest.raises(ValueError):
        extract("Reminder about class", SENT, MODULES).to_event()
    event = extract("ANA201 test on 20 Oct", SENT, MODULES).to_event()
    assert event.verified is False and event.module == "ANA201"
