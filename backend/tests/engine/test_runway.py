from datetime import date

from campus_engine.runway import ExpectedPayment, arrivals, project_runway, safe_to_spend
from campus_engine.text import rand

TODAY = date(2026, 10, 12)
ALLOWANCE = ExpectedPayment("Allowance", date(2026, 10, 30), 150_000)


def test_runs_out_before_next_payment():
    r = project_runway(61_000, TODAY, [ALLOWANCE], 4_500)
    # 61000 - 4500 * 14 < 0 on the 14th day of spending: 25 Oct
    assert r.runs_out_on == date(2026, 10, 25)
    assert r.days == 13
    assert r.short_before_next
    assert r.balance_before_next_cents == 61_000 - 4_500 * 18
    assert "before your next payment" in r.explanation


def test_late_scenario_moves_the_next_payment():
    r = project_runway(61_000, TODAY, [ALLOWANCE], 4_500, late_days=14)
    assert r.next_payment_on == date(2026, 11, 13)
    assert r.scenario == "14 days late"


def test_money_lasts_past_the_payment():
    r = project_runway(300_000, TODAY, [ALLOWANCE], 5_000, horizon_days=120)
    assert not r.short_before_next
    # (300000 + 150000) / 5000 = 90 days of spending, so it runs out on day 90
    assert r.runs_out_on == date(2027, 1, 10)


def test_lasts_beyond_horizon():
    r = project_runway(1_000_000, TODAY, [], 1_000, horizon_days=30)
    assert r.runs_out_on is None and r.days is None
    assert "beyond the next 30 days" in r.explanation


def test_overdue_payment_assumed_tomorrow_and_received_ignored():
    overdue = ExpectedPayment("Late allowance", date(2026, 10, 1), 100_000)
    received = ExpectedPayment("Already in", date(2026, 10, 5), 100_000, received=True)
    landing = arrivals([received, overdue], TODAY)
    assert landing == [(date(2026, 10, 13), overdue)]
    late = arrivals([overdue], TODAY, late_days=14)
    assert late[0][0] == date(2026, 10, 26)


def test_safe_to_spend_when_only_essentials_fit():
    s = safe_to_spend(61_000, TODAY, [ALLOWANCE], essentials_per_day_cents=4_000, reserve_cents=10_000)
    assert s.days_until_next == 18
    assert s.per_day_cents == 0
    assert "keep extras to zero" in s.explanation


def test_safe_to_spend_with_room_for_extras():
    s = safe_to_spend(230_000, TODAY, [ALLOWANCE], essentials_per_day_cents=5_500, reserve_cents=30_000)
    assert s.per_day_cents == (230_000 - 5_500 * 18 - 30_000) // 18
    assert rand(s.per_day_cents) in s.explanation


def test_rand_formatting():
    assert rand(124_000) == "R1 240"
    assert rand(124_050) == "R1 240.50"
    assert rand(-500) == "-R5"
