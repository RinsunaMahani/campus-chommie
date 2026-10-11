"""
A labelled set of realistic class messages: new events, "moved" and
"cancelled" messages, messages mixing English with other South African
languages, and dates a rep has to look at twice. Each label is what the
engine should read; `check` is the fields it should ask the rep to check.
The brief asks for at least 30; we keep at least 50. Add a message whenever
a real one reads wrong.
"""
from datetime import date, datetime, time

import pytest

from campus_engine.extraction import apply_change, change_line, extract, find_existing, reading
from campus_engine.workload import AcademicEvent

SENT = date(2026, 10, 12)  # a Monday
MODULES = ["ANA201", "PHY121", "BCH111"]

NEW_EVENTS = [
    (
        "ANA201 assignment 3 due 23/10 at 23:59, worth 15%",
        dict(kind="assignment", title="Assignment 3", module="ANA201", on=date(2026, 10, 23), at=time(23, 59), weighting=15),
    ),
    (
        "Reminder: semester test on 4 November 2026, 08h00, venue Hall 3",
        dict(kind="test", title="Semester test", on=date(2026, 11, 4), at=time(8, 0), venue="Hall 3"),
    ),
    ("Practical tomorrow 2pm lab C12", dict(kind="practical", on=date(2026, 10, 13), at=time(14, 0), venue="Lab C12")),
    ("bch 111 quiz on 20 Oct, 10.30am", dict(kind="quiz", module="BCH111", on=date(2026, 10, 20), at=time(10, 30))),
    ("Exam timetable: ANA201 exam 2026-11-09 09:00", dict(kind="exam", module="ANA201", on=date(2026, 11, 9), at=time(9, 0))),
    ("Assignment 1 submission Oct 30", dict(kind="assignment", title="Assignment 1", on=date(2026, 10, 30))),
    (
        "ANA201 assignment 2 due 2 Nov 2026, 17:00",
        dict(title="Assignment 2", on=date(2026, 11, 2), at=time(17, 0), check=[]),
    ),
    ("PHY121 test tonight 18:30", dict(kind="test", on=date(2026, 10, 12), at=time(18, 30))),
    (
        "BCH111 prac 3 on Tues, 13:00, Lab 4",
        dict(title="Practical 3", module="BCH111", on=date(2026, 10, 13), at=time(13, 0), venue="Lab 4"),
    ),
    ("ANA201 assignment counts 10% and is due Oct 30", dict(kind="assignment", weighting=10, on=date(2026, 10, 30))),
    # Lower case, and the number run into the word.
    (
        "phy121 test1 on 21 oct 10am",
        dict(kind="test", title="Test 1", module="PHY121", on=date(2026, 10, 21), at=time(10, 0), check=[]),
    ),
    (
        "PHY121 examination: 12 November 2026 at 09:00, Hall 1",
        dict(kind="exam", title="Exam", on=date(2026, 11, 12), at=time(9, 0), venue="Hall 1"),
    ),
    ("Submit BCH111 report by 30 October 23:59", dict(kind="assignment", on=date(2026, 10, 30), at=time(23, 59))),
    # Only "due" says it's an assignment: the rep checks the type.
    ("ANA201 work due Friday", dict(kind="assignment", on=date(2026, 10, 16), check=["kind"])),
    ("Reminder: BCH111 quiz this Friday", dict(kind="quiz", module="BCH111", on=date(2026, 10, 16))),
    (
        "BCH111 assignment 4: submit on Blackboard by 6 Nov, 23:59",
        dict(title="Assignment 4", on=date(2026, 11, 6), at=time(23, 59), check=[]),
    ),
]

CHANGES = [
    (
        "Test 2 moved to Thursday 10:00, Room B4",
        dict(kind="test", title="Test 2", on=date(2026, 10, 15), at=time(10, 0), venue="Room B4", change="moved"),
    ),
    ("PHY121 quiz cancelled", dict(kind="quiz", module="PHY121", change="cancelled", on=None)),
    (
        "Hi all, the PHY121 practical has been postponed to Wednesday 21 Oct, same time 14:00",
        dict(kind="practical", module="PHY121", on=date(2026, 10, 21), at=time(14, 0), change="moved", check=[]),
    ),
    (
        "ANA201 Test 2 is now on 27/10 at 10h30 in Hall 3",
        dict(title="Test 2", on=date(2026, 10, 27), at=time(10, 30), venue="Hall 3", change="moved"),
    ),
    (
        "BCH111 quiz 4 rescheduled: Mon 26 Oct, 08:00",
        dict(title="Quiz 4", module="BCH111", on=date(2026, 10, 26), at=time(8, 0), change="moved"),
    ),
    # Only the venue moves: no date in the message, so the rep checks it.
    (
        "Venue change: the ANA201 semester test moves to LT 5",
        dict(title="Semester test", venue="LT 5", on=None, change="moved", check=["on"]),
    ),
    ("PHY121 test brought forward to Thursday 15 Oct!", dict(kind="test", on=date(2026, 10, 15), change="moved")),
    (
        "New date for BCH111 assignment 2 submission: 6 November",
        dict(title="Assignment 2", on=date(2026, 11, 6), change="moved"),
    ),
    # WhatsApp bold and an emoji.
    ("*ANA201 TEST 2* 📢 moved to *Fri 30 Oct*", dict(title="Test 2", module="ANA201", on=date(2026, 10, 30), change="moved")),
    ("No PHY121 prac this Friday, it's been cancelled", dict(kind="practical", on=date(2026, 10, 16), change="cancelled")),
    ("ANA201 quiz 3 won't take place tomorrow", dict(title="Quiz 3", on=date(2026, 10, 13), change="cancelled")),
    # A cancellation needs no date.
    ("BCH111 class test called off due to the strike", dict(title="Class test", on=None, change="cancelled", check=[])),
    # From one date to another: the new one, after "to", and the rep checks.
    (
        "ANA201 Test 2 moved from 20 Oct to 22 Oct",
        dict(title="Test 2", on=date(2026, 10, 22), change="moved", check=["on"]),
    ),
    (
        "Test 2 moved from Tue 20 Oct to Thursday 22 Oct at 10:00",
        dict(title="Test 2", on=date(2026, 10, 22), at=time(10, 0), change="moved"),
    ),
    # Only one date is written out ("20" has no month), and it's the new one.
    ("ANA201 Test 2 moved from 20 to 22 Oct", dict(on=date(2026, 10, 22), change="moved", check=[])),
    # "Tomorrow" is the old day; "Thursday" the new one.
    ("ANA201: no test tomorrow, it has been moved to Thursday", dict(on=date(2026, 10, 15), change="moved", check=["on"])),
    # Moved, but not to a date yet.
    ("ANA201 test 2 postponed until further notice", dict(title="Test 2", on=None, change="moved", check=["on"])),
]

MIXED_LANGUAGES = [
    (
        "Sanibonani! ANA201 test is on 22 Oct at 9am, LT 2. Ngiyabonga",
        dict(kind="test", on=date(2026, 10, 22), at=time(9, 0), venue="LT 2", check=[]),
    ),
    (
        "Molweni, BCH111 quiz 2 on 19 Oct, 08:00 in Lab C3. Enkosi",
        dict(title="Quiz 2", on=date(2026, 10, 19), at=time(8, 0), venue="Lab C3"),
    ),
    (
        "Avuxeni, ANA201 semester test on Thursday 29 October at 14:00. Inkomu",
        dict(title="Semester test", on=date(2026, 10, 29), at=time(14, 0)),
    ),
    (
        "Dumelang! PHY121 assignment 1 due 30/10 at 23:59. Ke a leboga",
        dict(title="Assignment 1", module="PHY121", on=date(2026, 10, 30), at=time(23, 59)),
    ),
    (
        "Sanibonani, reminder: PHY121 exam 2026-11-12 09:00, venue: Sports Hall",
        dict(kind="exam", on=date(2026, 11, 12), at=time(9, 0), venue="Sports Hall"),
    ),
    # Afrikaans: "Môre" here is "good morning", and the date is the one in the message.
    (
        "Môre almal! ANA201 toets 2 is verskuif na Donderdag 22 Okt om 10:00",
        dict(kind="test", title="Test 2", on=date(2026, 10, 22), at=time(10, 0), change="moved", check=[]),
    ),
    ("PHY121 eksamen: 12 November om 09:00", dict(kind="exam", on=date(2026, 11, 12), at=time(9, 0))),
    ("BCH111 vasvra is gekanselleer", dict(kind="quiz", module="BCH111", change="cancelled", check=[])),
    (
        "ANA201 werkopdrag 3 moet Vrydag ingehandig word",
        dict(kind="assignment", title="Assignment 3", on=date(2026, 10, 16), check=[]),
    ),
    ("Herinnering: BCH111 toets 3 op 5 Mrt 2027 om 08h00", dict(title="Test 3", on=date(2027, 3, 5), at=time(8, 0))),
    ("PHY121 opdrag uitgestel na 2 Des", dict(kind="assignment", on=date(2026, 12, 2), change="moved")),
    # "Na" is "to": the new date.
    ("ANA201 toets 2 verskuif van 20 Okt na 23 Okt", dict(title="Test 2", on=date(2026, 10, 23), change="moved", check=["on"])),
]

DATES_TO_CHECK = [
    # Day first, as South Africans write it: 3 November, not 11 March.
    ("ANA201 test on 03/11", dict(on=date(2026, 11, 3))),
    ("BCH111 test on 11/12", dict(on=date(2026, 12, 11))),
    ("Quiz 1 for BCH111 on 15/10/26", dict(title="Quiz 1", on=date(2026, 10, 15))),
    # "Next Friday" could be this week's or the one after: read as the one after, and flagged.
    ("PHY121 assignment due next Friday", dict(on=date(2026, 10, 23), check=["on"])),
    # Sent on a Monday, "Monday" means a week away: flagged.
    ("BCH111 quiz on Monday", dict(on=date(2026, 10, 19), check=["on"])),
    # No month: left for the rep rather than guessed.
    ("ANA201 test 2 on the 20th", dict(title="Test 2", on=None, check=["on"])),
    # Before the message was sent: flagged.
    ("ANA201 test was on 1 Oct", dict(on=date(2026, 10, 1), check=["on"])),
    # A range: its first day, flagged.
    ("PHY121 practical 4 on 20-22 Oct, book one slot", dict(title="Practical 4", on=date(2026, 10, 20), check=["on"])),
    ("PHY121 exam: 12 - 13 November, two sessions", dict(kind="exam", on=date(2026, 11, 12), check=["on"])),
    # Two possible days, not a change: the first, flagged.
    ("ANA201 test on 20 Oct or 21 Oct, the lecturer will confirm", dict(on=date(2026, 10, 20), check=["on"])),
    # An hour with no minutes: a time, flagged (it could be a length).
    ("BCH111 test at 14h on 3 Nov", dict(on=date(2026, 11, 3), at=time(14, 0), check=["at"])),
    # Which week is week 9 depends on the university's calendar: not guessed.
    ("STK test in week 9", dict(kind="test", on=None, check=["module", "on"])),
]

CASES = NEW_EVENTS + CHANGES + MIXED_LANGUAGES + DATES_TO_CHECK


def test_the_labelled_set_is_big_enough():
    assert len(CASES) >= 50  # the brief's M4 bar is 30


@pytest.mark.parametrize("message,expected", CASES, ids=[c[0][:30] for c in CASES])
def test_labelled_messages(message, expected):
    c = extract(message, SENT, MODULES)
    for name, value in expected.items():
        got = c.needs_check() if name == "check" else getattr(c, name)
        assert got == value, f"{name}: got {got!r}"


def test_more_is_never_read_as_tomorrow():
    c = extract("Môre almal, ANA201 toets Vrydag", SENT, MODULES)
    assert c.on == date(2026, 10, 16)  # Friday, not Tuesday the 13th


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


# ------------------------------------------------- plain words for the rep


def test_reading_a_new_event():
    c = extract("ANA201 Test 2 on 20 Oct at 08:00, LT 3, worth 20%", SENT, MODULES)
    assert reading(c) == ["We read this as: Test 2 for ANA201 on Tue 20 Oct 2026 at 08:00, LT 3, worth 20% of the mark."]


def test_reading_says_what_to_check_and_why():
    c = extract("ANA201 test was on 1 Oct", SENT, MODULES)
    assert reading(c) == [
        "We read this as: Test for ANA201 on Thu 1 Oct 2026.",
        "Check the date before confirming.",
        "This date is before the message was sent.",
    ]
    assert reading(extract("Reminder about class", SENT, MODULES)) == [
        "We couldn't find a test, assignment or date in this message: fill in the event before confirming.",
        "Check the type, module and date before confirming.",
    ]


def test_reading_a_change_names_the_event_it_changes():
    moved = extract("ANA201 Test 2 moved to Thursday 22 Oct, 10:00, Room B4", SENT, MODULES)
    assert reading(moved, "Test 2", date(2026, 10, 20))[0] == (
        "We read this as: Test 2 on Tue 20 Oct 2026 moves to Thu 22 Oct 2026 at 10:00, Room B4.")
    assert reading(moved)[0] == "We read this as a change to an event, but couldn't tell which one: choose it before confirming."
    nowhere = extract("ANA201 test 2 has been moved", SENT, MODULES)
    assert reading(nowhere, "Test 2", date(2026, 10, 20))[0] == "We read this as: Test 2 on Tue 20 Oct 2026 moves, but not where to."
    cancelled = extract("ANA201 test 2 cancelled", SENT, MODULES)
    assert reading(cancelled, "Test 2", date(2026, 10, 20)) == ["We read this as: Test 2 on Tue 20 Oct 2026 is cancelled."]
    assert reading(cancelled)[0] == "We read this as a cancellation, but couldn't tell which event: choose it before confirming."


def test_change_lines():
    assert change_line("on", date(2026, 10, 20), date(2026, 10, 22)) == "Moved from Tue 20 Oct 2026 to Thu 22 Oct 2026."
    assert change_line("at", time(8, 0), None) == "Time changed from 08:00 to no time set."
    assert change_line("venue", None, "Room B4") == "Venue changed from not set to Room B4."
    assert change_line("cancelled", False, True) == "Cancelled."
    assert change_line("cancelled", True, False) == "Back on: no longer cancelled."
    with pytest.raises(ValueError):
        change_line("weighting", 10, 20)


# ------------------------------------------------- dates a rep should check


def test_several_dates_say_which_was_read():
    moved = extract("ANA201 Test 2 moved from 20 Oct to 22 Oct", SENT, MODULES)
    assert moved.notes == ["This message has more than one date: we read the new one. Check it."]
    either = extract("ANA201 test on 20 Oct or 21 Oct", SENT, MODULES)
    assert either.notes == ["This message has more than one date: we read the first. Check which one it's about."]
    same = extract("ANA201 test on Tuesday 20 Oct (Tue 20/10)", SENT, MODULES)
    assert same.on == date(2026, 10, 20) and same.notes == []  # the same day twice is one date


def test_a_range_says_it_read_the_first_day():
    c = extract("PHY121 practical 4 on 20-22 Oct", SENT, MODULES)
    assert c.notes == ["This message gives a range of days: we read the first. Check it."]
    assert reading(c)[-1] == "This message gives a range of days: we read the first. Check it."


def test_a_bare_hour_is_a_time_to_check():
    c = extract("BCH111 test at 14h on 3 Nov", SENT, MODULES)
    assert c.at == time(14, 0) and c.confidence["at"] < 0.7
    assert extract("BCH111 test at 14h30 on 3 Nov", SENT, MODULES).confidence["at"] == 0.9  # with minutes: sure
