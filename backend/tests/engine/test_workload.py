from datetime import date, datetime

import pytest

from campus_engine.workload import AcademicEvent, clustered_indices, week_start, weekly_load


@pytest.fixture
def heavy_week():
    return [
        AcademicEvent("Test 2", "test", datetime(2026, 10, 20, 8, 0), "ANA201", 20),
        AcademicEvent("Assignment 3", "assignment", datetime(2026, 10, 21, 23, 59), "PHY121", 15),
        AcademicEvent("Quiz 4", "quiz", datetime(2026, 10, 22, 10, 0), "BCH111", 10),
    ]


def test_week_starts_on_monday():
    assert week_start(date(2026, 10, 15)) == date(2026, 10, 12)
    assert week_start(date(2026, 10, 12)) == date(2026, 10, 12)


def test_clustered_events_are_found(heavy_week):
    assert clustered_indices(heavy_week, 48) == {0, 1, 2}


def test_heavy_week_score_colour_and_reason(heavy_week):
    weeks = weekly_load(heavy_week, date(2026, 10, 12), weeks=3)
    assert weeks[0].colour == "green" and weeks[0].reason == "Nothing due this week."
    busy = weeks[1]
    # 3*1.2*1.5 + 2*1.15*1.5 + 1*1.1*1.5 = 5.4 + 3.45 + 1.65
    assert busy.score == pytest.approx(10.5)
    assert busy.colour == "red"
    assert busy.reason == "Heavy: 1 test, 1 assignment and 1 quiz, with 3 within 48 hours of another."


def test_single_quiz_is_manageable():
    weeks = weekly_load([AcademicEvent("Quiz 1", "quiz", datetime(2026, 10, 13, 9, 0))], date(2026, 10, 12), weeks=1)
    assert weeks[0].colour == "green"
    assert weeks[0].reason == "Manageable: 1 quiz."


def test_cancelled_events_do_not_count(heavy_week):
    heavy_week[0].cancelled = True
    busy = weekly_load(heavy_week, date(2026, 10, 19), weeks=1)[0]
    assert len(busy.events) == 2
    assert busy.score < 10.5


def test_exam_week_is_detected():
    exams = [
        AcademicEvent("ANA201 exam", "exam", datetime(2026, 11, 9, 9, 0), "ANA201", 50),
        AcademicEvent("PHY121 exam", "exam", datetime(2026, 11, 12, 9, 0), "PHY121", 40),
    ]
    week = weekly_load(exams, date(2026, 11, 9), weeks=1)[0]
    assert week.has_exam
    assert week.colour == "red"  # 4*1.5 + 4*1.4 = 11.6
