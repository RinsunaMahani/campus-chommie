"""Predictions from the student's own data: spending pace and module marks.

The models are deliberately simple so every prediction can be explained in one
sentence: an exponentially weighted average for spending, and "if the rest goes
like your results so far" for marks.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import sqrt

from .config import load_config
from .runway import ExpectedPayment, FixedCost, RunwayResult, project_runway
from .standing import Assessment
from .text import day, num, rand


@dataclass
class SpendingPace:
    daily_cents: int
    low_cents: int
    high_cents: int
    days_of_history: int
    explanation: str


def spending_pace(history: list[tuple[date, int]], cfg: dict | None = None) -> SpendingPace | None:
    """Daily spending pace from logged daily totals, with a likely range.

    Returns None when there are too few logged days to say anything useful.
    """
    cfg = cfg or load_config()
    fc = cfg["forecast"]
    if len(history) < fc["min_days_of_history"]:
        return None
    values = [cents for _, cents in sorted(history)]
    alpha = fc["ewma_alpha"]
    level = float(values[0])
    for v in values[1:]:
        level = alpha * v + (1 - alpha) * level
    window = values[-fc["spread_window"]:]
    mean = sum(window) / len(window)
    sd = sqrt(sum((v - mean) ** 2 for v in window) / len(window))
    weekly_spread = sd / sqrt(7)  # how much a week's average typically moves
    low = max(0.0, level - weekly_spread)
    high = level + weekly_spread
    text = (
        f"Based on {len(values)} days you logged, recent days counting most, "
        f"you spend about {rand(round(level))} a day (usually {rand(round(low))} to {rand(round(high))})."
    )
    return SpendingPace(round(level), round(low), round(high), len(values), text)


@dataclass
class RunwayForecast:
    likely: RunwayResult
    earliest: RunwayResult  # at the high end of the spending range
    latest: RunwayResult  # at the low end
    pace: SpendingPace
    explanation: str


def forecast_runway(
    balance_cents: int,
    today: date,
    payments: list[ExpectedPayment],
    pace: SpendingPace,
    late_days: int = 0,
    horizon_days: int = 120,
    fixed_costs: list[FixedCost] | None = None,
) -> RunwayForecast:
    def run(spend: int) -> RunwayResult:
        return project_runway(balance_cents, today, payments, spend, late_days, horizon_days, fixed_costs=fixed_costs)

    likely, earliest, latest = run(pace.daily_cents), run(pace.high_cents), run(pace.low_cents)
    if likely.runs_out_on is None:
        text = f"At your recent pace, your money lasts beyond the next {horizon_days} days."
    else:
        text = f"At your recent pace, your money likely runs out around {day(likely.runs_out_on)}"
        if earliest.runs_out_on and latest.runs_out_on and earliest.runs_out_on != latest.runs_out_on:
            text += f" (between {day(earliest.runs_out_on)} and {day(latest.runs_out_on)})"
        elif earliest.runs_out_on and latest.runs_out_on is None:
            text += f" (or as early as {day(earliest.runs_out_on)})"
        text += "."
        if likely.short_before_next and likely.next_payment_on:
            text += f" That's before your next payment on {day(likely.next_payment_on)}."
    return RunwayForecast(likely, earliest, latest, pace, text)


@dataclass
class MarkProjection:
    projected: float
    low: float
    high: float
    based_on: int
    target: float | None
    below_target: bool
    explanation: str


def project_module_mark(assessments: list[Assessment], target: float | None = None) -> MarkProjection | None:
    """Project the final module mark if the rest goes like the results so far."""
    done = [a for a in assessments if a.mark is not None]
    if not done:
        return None
    total = sum(a.weight for a in assessments)
    done_weight = sum(a.weight for a in done)
    earned = sum(a.weight * a.mark for a in done)
    average = earned / done_weight
    remaining = total - done_weight
    if len(done) >= 2:
        mean = sum(a.mark for a in done) / len(done)
        sd = sqrt(sum((a.mark - mean) ** 2 for a in done) / len(done))
    else:
        sd = 0.0

    def final(rest_average: float) -> float:
        return (earned + min(100.0, max(0.0, rest_average)) * remaining) / total

    projected, low, high = final(average), final(average - sd), final(average + sd)
    below = target is not None and projected < target

    if remaining <= 0:
        text = f"This module is complete: {projected:.1f}%."
    else:
        text = f"If the rest goes like your results so far, you'd finish around {projected:.0f}%"
        if len(done) >= 2 and high - low >= 1:
            text += f" (likely {low:.0f}% to {high:.0f}%)."
        else:
            text += ". That's based on one result, so treat it as a rough guide."
    if target is not None and remaining > 0:
        if below:
            text += f" That's under your {num(target)}% target, so the standing calculator shows what you'd need."
        else:
            text += f" On track for your {num(target)}% target."
    return MarkProjection(projected, low, high, len(done), target, below, text)
