from datetime import date, timedelta

import pytest

from campus_engine.forecast import forecast_runway, project_module_mark, spending_pace
from campus_engine.runway import ExpectedPayment
from campus_engine.standing import Assessment

TODAY = date(2026, 10, 12)


def history(values):
    start = TODAY - timedelta(days=len(values))
    return [(start + timedelta(days=i), v) for i, v in enumerate(values)]


def test_too_little_history_returns_none():
    assert spending_pace(history([4_000, 5_000, 6_000])) is None


def test_ewma_weights_recent_days_more():
    pace = spending_pace(history([1_000, 2_000, 3_000, 4_000, 5_000]))
    # 1000 -> 1300 -> 1810 -> 2467 -> 3226.9 with alpha 0.3
    assert pace.daily_cents == 3_227
    assert pace.low_cents < pace.daily_cents < pace.high_cents


def test_steady_spending_has_no_spread():
    pace = spending_pace(history([4_500] * 14))
    assert (pace.low_cents, pace.daily_cents, pace.high_cents) == (4_500, 4_500, 4_500)


def test_forecast_range_is_ordered():
    pace = spending_pace(history([3_000, 6_500, 2_000, 5_500, 4_000, 7_000, 3_500, 4_500, 5_000, 2_500, 6_000, 4_000]))
    fc = forecast_runway(61_000, TODAY, [ExpectedPayment("Allowance", date(2026, 10, 30), 150_000)], pace)
    assert fc.earliest.runs_out_on <= fc.likely.runs_out_on <= fc.latest.runs_out_on
    assert "likely runs out around" in fc.explanation
    assert "before your next payment" in fc.explanation


def test_mark_projection_with_a_range():
    module = [Assessment("Test 1", 20, 64), Assessment("Assignment 1", 10, 71), Assessment("Test 2", 20), Assessment("Exam", 50)]
    p = project_module_mark(module, target=60)
    assert p.projected == pytest.approx(1990 / 30)
    assert p.low == pytest.approx((1990 + (1990 / 30 - 3.5) * 70) / 100)
    assert p.high == pytest.approx((1990 + (1990 / 30 + 3.5) * 70) / 100)
    assert not p.below_target
    assert "likely" in p.explanation


def test_mark_projection_with_one_result_is_flagged_as_rough():
    p = project_module_mark([Assessment("Test 1", 25, 48), Assessment("Exam", 75)], target=50)
    assert p.low == p.high == p.projected == pytest.approx(48)
    assert p.below_target
    assert "rough guide" in p.explanation


def test_no_marks_no_projection():
    assert project_module_mark([Assessment("Exam", 100)]) is None
