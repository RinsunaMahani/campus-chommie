"""
"Do this next": every signal ranked into at most three steps, money short in a heavy week named together, nearer
things first, and setup steps only when nothing more urgent is on. Made-up situations.
"""
from __future__ import annotations

from datetime import date, timedelta

from campus_engine.next_steps import Closing, Due, Facts, GoalDue, next_steps
from campus_engine.runway import ExpectedPayment, RunwayResult
from campus_engine.workload import WeekLoad

TODAY = date(2026, 10, 21)  # a Wednesday
CFG = {"max_steps": 3, "due_days": 3, "exam_days": 7, "funding_days": 14, "goal_days": 30, "heavy_weeks_ahead": 2}


def short(days: int, payday_in: int) -> RunwayResult:
    pay = ExpectedPayment("Allowance", TODAY + timedelta(days=payday_in), 150_000)
    return RunwayResult("on time", 4_000, TODAY + timedelta(days=days), days, pay, pay.expected_on, -1,
                        f"At about R40 a day, your money runs out around {(TODAY + timedelta(days=days)):%a %d %b}.")


def heavy(weeks_ahead: int) -> WeekLoad:
    start = TODAY - timedelta(days=TODAY.weekday()) + timedelta(weeks=weeks_ahead)
    return WeekLoad(start, 8.0, "red", "Heavy: 2 tests and 1 assignment.")


def kinds(f: Facts) -> list[str]:
    return [s.kind for s in next_steps(f, CFG)]


def test_money_short_in_a_heavy_week_is_one_step_named_together_and_first():
    steps = next_steps(Facts(TODAY, short(6, 12), [heavy(1)], classes=5), CFG)
    assert steps[0].kind == "money_and_week"
    assert steps[0].line == "Money runs short before payday, in a heavy week. Plan essentials now."
    assert "your money lasts about 6 days, to around Tue 27 Oct, 6 days before your next payment" in steps[0].why
    assert steps[0].target == "money" and steps[0].tone == "attention"
    assert "heavy_week" not in kinds(Facts(TODAY, short(6, 12), [heavy(1)], classes=5))


def test_nearer_deadlines_come_before_further_ones_and_carry_their_weight():
    due = [Due("PHY121", "Test 2", TODAY + timedelta(days=3), "10:00", 20),
           Due("ANA201", "Assignment 3", TODAY + timedelta(days=1), "23:59", 15)]
    steps = next_steps(Facts(TODAY, None, due=due, classes=5), CFG)
    assert [s.line for s in steps[:2]] == [
        "ANA201 Assignment 3 tomorrow, worth 15% of the module.",
        "PHY121 Test 2 in 3 days at 10:00, worth 20% of the module.",
    ]
    # The line beneath adds something new: what else is coming, not the same words again.
    assert steps[0].why == "1 other thing due in the next 7 days, the next being PHY121 Test 2 on Sat 24 Oct."


def test_an_exam_this_week_a_closing_bursary_and_a_goal():
    f = Facts(TODAY, None, due=[Due("MCHM000", "PAPER ONE", TODAY + timedelta(days=5), "14:00", exam=True)],
              closing=[Closing("NSFAS", TODAY + timedelta(days=10))],
              goals=[GoalDue("Registration fee", TODAY + timedelta(days=20), 90_000, 30_000)], classes=5)
    steps = next_steps(f, CFG)
    assert [s.kind for s in steps] == ["exam", "funding", "goal"]
    assert steps[0].line == "MCHM000 exam in 5 days at 14:00. Make a revision plan."
    assert steps[1].line == "NSFAS closes in 10 days. Finish your application."
    assert steps[2].line == "Put R300 aside this week for Registration fee."


def test_far_off_things_and_past_ones_are_left_out():
    f = Facts(TODAY, None, due=[Due("X", "Test", TODAY + timedelta(days=9), "10:00"),
                                Due("Y", "Test", TODAY - timedelta(days=1), "10:00")],
              closing=[Closing("Far", TODAY + timedelta(days=40))], classes=5)
    assert kinds(f) == ["setup_money"]


def test_a_new_student_is_told_what_to_set_up_and_never_more_than_three():
    assert kinds(Facts(TODAY)) == ["setup_classes", "setup_money"]
    busy = Facts(TODAY, short(3, 10), [heavy(0)],
                 due=[Due("A", "Test", TODAY + timedelta(days=d), "09:00") for d in (0, 1, 2)], classes=0)
    assert len(next_steps(busy, CFG)) == 3
    assert "setup_classes" not in kinds(busy)


def test_checkin_due_surfaces_nudge():
    f = Facts(TODAY, checkin_due=True, streak_weeks=3, classes=5)
    steps = next_steps(f, CFG)
    checkin_step = next((s for s in steps if s.kind == "checkin"), None)
    assert checkin_step is not None
    assert checkin_step.line == "Weekly money check-in: log this week's spending."
    assert "3 weeks in a row" in checkin_step.why
    assert checkin_step.target == "money"
    assert checkin_step.action == "Check in"
