"""Tests for pure Python money health engine checks."""
from datetime import date

from campus_engine.money_health import (
    CHECK_BUFFER,
    CHECK_CHECKIN,
    CHECK_GOALS,
    CHECK_RUNWAY,
    CHECK_SPENDING,
    STATUS_CANT_TELL,
    STATUS_DONE,
    STATUS_NOT_YET,
    check_money_health,
)
from campus_engine.money_plan import Goal, PaydayPlan, Pot
from campus_engine.runway import ExpectedPayment, RunwayResult


TODAY = date(2026, 10, 12)
NEXT_PAY = date(2026, 11, 1)


def test_missing_data_returns_cant_tell():
    health = check_money_health(today=TODAY)
    assert health.done_count == 0
    assert health.total_count == 5
    assert health.line == "0 of 5 checks done"
    for c in health.checks:
        assert c.status == STATUS_CANT_TELL
        assert c.action is not None
        assert c.target is not None


def test_runway_check_scenarios():
    payment = ExpectedPayment("NSFAS", NEXT_PAY, 150_000)

    # 1. Money lasts indefinitely
    r_indefinite = RunwayResult("on time", 5_000, None, None, payment, NEXT_PAY, 100_000, "Money lasts")
    h1 = check_money_health(today=TODAY, runway=r_indefinite)
    c1 = next(c for c in h1.checks if c.id == CHECK_RUNWAY)
    assert c1.status == STATUS_DONE
    assert "well past your next payment" in c1.line

    # 2. Money lasts past next payment
    r_past = RunwayResult("on time", 5_000, date(2026, 11, 15), 34, payment, NEXT_PAY, 50_000, "Money lasts")
    h2 = check_money_health(today=TODAY, runway=r_past)
    c2 = next(c for c in h2.checks if c.id == CHECK_RUNWAY)
    assert c2.status == STATUS_DONE
    assert "past your payment" in c2.line

    # 3. Money runs out before next payment
    r_short = RunwayResult("on time", 10_000, date(2026, 10, 25), 13, payment, NEXT_PAY, -20_000, "Runs out early")
    h3 = check_money_health(today=TODAY, runway=r_short)
    c3 = next(c for c in h3.checks if c.id == CHECK_RUNWAY)
    assert c3.status == STATUS_NOT_YET
    assert "before your payment" in c3.line
    assert c3.action == "Review runway"
    assert c3.target == "/money"

    # 4. No next payment scheduled
    r_nopay = RunwayResult("on time", 5_000, date(2026, 11, 10), 29, None, None, None, "Runs out")
    h4 = check_money_health(today=TODAY, runway=r_nopay)
    c4 = next(c for c in h4.checks if c.id == CHECK_RUNWAY)
    assert c4.status == STATUS_CANT_TELL
    assert "no upcoming payment is set" in c4.line


def test_buffer_pot_check():
    # 1. No buffer pot at all
    goals_no_buffer = [Goal("Laptop", 50_000, date(2026, 12, 1), kind="big_purchase")]
    h1 = check_money_health(today=TODAY, goals=goals_no_buffer)
    c1 = next(c for c in h1.checks if c.id == CHECK_BUFFER)
    assert c1.status == STATUS_NOT_YET
    assert c1.action == "Add a buffer pot"
    assert c1.target == "/money/goal"

    # 2. Buffer pot with R0 saved
    goals_zero_buffer = [Goal("Emergency", left_cents=50_000, kind="buffer", amount_cents=50_000, saved_cents=0)]
    h2 = check_money_health(today=TODAY, goals=goals_zero_buffer)
    c2 = next(c for c in h2.checks if c.id == CHECK_BUFFER)
    assert c2.status == STATUS_NOT_YET
    assert "R0 put aside so far" in c2.line
    assert c2.action == "Fund your buffer"

    # 3. Buffer pot with money saved
    goals_funded_buffer = [Goal("Emergency", left_cents=30_000, kind="buffer", amount_cents=50_000, saved_cents=20_000)]
    h3 = check_money_health(today=TODAY, goals=goals_funded_buffer)
    c3 = next(c for c in h3.checks if c.id == CHECK_BUFFER)
    assert c3.status == STATUS_DONE
    assert "R200 put aside" in c3.line


def test_spending_within_safe_limit_check():
    # Safe per day: R40 -> Weekly safe: R280 (28_000 cents)
    safe_daily = 4_000

    # 1. Within safe limit (R150 spent)
    h1 = check_money_health(today=TODAY, this_week_spend_cents=15_000, safe_per_day_cents=safe_daily)
    c1 = next(c for c in h1.checks if c.id == CHECK_SPENDING)
    assert c1.status == STATUS_DONE
    assert "within your R280 weekly safe limit" in c1.line

    # 2. Over safe limit (R350 spent)
    h2 = check_money_health(today=TODAY, this_week_spend_cents=35_000, safe_per_day_cents=safe_daily)
    c2 = next(c for c in h2.checks if c.id == CHECK_SPENDING)
    assert c2.status == STATUS_NOT_YET
    assert "R70 over your R280 safe limit" in c2.line
    assert c2.action == "Review spending"
    assert c2.target == "/money"


def test_goals_covered_by_plan_check():
    # 1. No dated goals
    goals_none = [Goal("Family", 30_000, kind="family")]
    h1 = check_money_health(today=TODAY, goals=goals_none)
    c1 = next(c for c in h1.checks if c.id == CHECK_GOALS)
    assert c1.status == STATUS_DONE
    assert "No upcoming big purchase or fee deadlines" in c1.line

    # 2. Dated goal and plan covers it
    goal = Goal("Laptop", left_cents=30_000, due_on=date(2026, 11, 30), kind="big_purchase", amount_cents=90_000, saved_cents=60_000)
    plan_covered = PaydayPlan(NEXT_PAY, 150_000, [Pot("Essentials", 80_000, "why"), Pot("Laptop", 10_000, "why")], 60_000, ["lines"])
    h2 = check_money_health(today=TODAY, goals=[goal], plan=plan_covered)
    c2 = next(c for c in h2.checks if c.id == CHECK_GOALS)
    assert c2.status == STATUS_DONE
    assert "covered by your plan" in c2.line

    # 3. Dated goal and plan is short
    plan_short = PaydayPlan(NEXT_PAY, 50_000, [Pot("Essentials", 80_000, "why")], -1, ["short"])
    h3 = check_money_health(today=TODAY, goals=[goal], plan=plan_short)
    c3 = next(c for c in h3.checks if c.id == CHECK_GOALS)
    assert c3.status == STATUS_NOT_YET
    assert "short of covering" in c3.line
    assert c3.action == "Review goals"


def test_weekly_checkin_check():
    # 1. Not checked in
    h1 = check_money_health(today=TODAY, checked_in_this_week=False)
    c1 = next(c for c in h1.checks if c.id == CHECK_CHECKIN)
    assert c1.status == STATUS_NOT_YET
    assert c1.action == "Check in now"
    assert c1.target == "/money/checkin"

    # 2. Checked in, 1 week
    h2 = check_money_health(today=TODAY, checked_in_this_week=True, streak_weeks=1)
    c2 = next(c for c in h2.checks if c.id == CHECK_CHECKIN)
    assert c2.status == STATUS_DONE
    assert c2.line == "Checked in for this week."

    # 3. Checked in, 4 weeks in a row
    h3 = check_money_health(today=TODAY, checked_in_this_week=True, streak_weeks=4)
    c3 = next(c for c in h3.checks if c.id == CHECK_CHECKIN)
    assert c3.status == STATUS_DONE
    assert "4 weeks in a row" in c3.line


def test_all_five_checks_done():
    payment = ExpectedPayment("NSFAS", NEXT_PAY, 150_000)
    runway = RunwayResult("on time", 4_000, date(2026, 11, 20), 39, payment, NEXT_PAY, 50_000, "Good")
    goals = [
        Goal("Buffer", left_cents=25_000, kind="buffer", amount_cents=50_000, saved_cents=25_000),
        Goal("Fees", left_cents=30_000, due_on=date(2026, 12, 1), kind="goal", amount_cents=40_000, saved_cents=10_000),
    ]
    plan = PaydayPlan(NEXT_PAY, 150_000, [Pot("Essentials", 80_000, "why"), Pot("Fees", 10_000, "why")], 40_000, ["lines"])

    health = check_money_health(
        today=TODAY,
        runway=runway,
        goals=goals,
        this_week_spend_cents=12_000,
        safe_per_day_cents=3_000,
        plan=plan,
        checked_in_this_week=True,
        streak_weeks=3,
    )

    assert health.done_count == 5
    assert health.total_count == 5
    assert health.line == "5 of 5 checks done"
    for c in health.checks:
        assert c.status == STATUS_DONE
