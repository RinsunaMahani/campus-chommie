"""Money runway: how long the money lasts, and what is safe to spend.

Amounts are always the student's own entries. The engine never assumes an
allowance amount or date.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from .text import day, rand


@dataclass
class ExpectedPayment:
    label: str
    expected_on: date
    amount_cents: int
    received: bool = False


@dataclass
class RunwayResult:
    scenario: str
    daily_spend_cents: int
    runs_out_on: date | None  # None: lasts beyond the horizon
    days: int | None
    next_payment: ExpectedPayment | None
    next_payment_on: date | None  # when it is assumed to land in this scenario
    balance_before_next_cents: int | None  # projected balance the day before it lands
    explanation: str

    @property
    def short_before_next(self) -> bool:
        """True when the money runs out before the next payment lands."""
        if self.runs_out_on is None:
            return False
        return self.next_payment_on is None or self.runs_out_on < self.next_payment_on


def pending_payments(payments: list[ExpectedPayment]) -> list[ExpectedPayment]:
    return sorted((p for p in payments if not p.received), key=lambda p: p.expected_on)


def arrivals(payments: list[ExpectedPayment], today: date, late_days: int = 0) -> list[tuple[date, ExpectedPayment]]:
    """When each pending payment is assumed to land.

    On-time scenario: a payment lands on its expected date, or tomorrow if it is already overdue.
    Late scenario: the next pending payment lands `late_days` after its expected date (or after today, if overdue).
    """
    out = []
    for i, p in enumerate(pending_payments(payments)):
        if i == 0 and late_days:
            lands = max(p.expected_on, today) + timedelta(days=late_days)
        elif p.expected_on < today:
            lands = today + timedelta(days=1)
        else:
            lands = p.expected_on
        out.append((lands, p))
    return out


def project_runway(
    balance_cents: int,
    today: date,
    payments: list[ExpectedPayment],
    daily_spend_cents: int,
    late_days: int = 0,
    horizon_days: int = 120,
) -> RunwayResult:
    """Simulate day by day: payments land first, then the day's spending goes out."""
    landing = arrivals(payments, today, late_days)
    nxt_on, nxt = (landing[0] if landing else (None, None))
    balance = balance_cents
    before_next = balance_cents if nxt_on is not None and nxt_on <= today else None
    runs_out = None
    for d in range(horizon_days + 1):
        current = today + timedelta(days=d)
        balance += sum(p.amount_cents for when, p in landing if when == current)
        balance -= daily_spend_cents
        if nxt_on is not None and current == nxt_on - timedelta(days=1):
            before_next = balance
        if runs_out is None and balance < 0:
            runs_out = current

    scenario = f"{late_days} days late" if late_days else "on time"
    pace = f"At about {rand(daily_spend_cents)} a day"
    if runs_out is None:
        text = f"{pace}, your money lasts beyond the next {horizon_days} days."
    else:
        text = f"{pace}, your money runs out around {day(runs_out)}"
        if nxt_on is not None and runs_out < nxt_on:
            text += f", before your next payment on {day(nxt_on)}."
        else:
            text += "."
    days = (runs_out - today).days if runs_out else None
    return RunwayResult(scenario, daily_spend_cents, runs_out, days, nxt, nxt_on, before_next, text)


@dataclass
class SafeToSpend:
    per_day_cents: int
    days_until_next: int
    next_payment_on: date | None
    essentials_cents: int
    reserve_cents: int
    explanation: str


def safe_to_spend(
    balance_cents: int,
    today: date,
    payments: list[ExpectedPayment],
    essentials_per_day_cents: int,
    reserve_cents: int = 0,
    fallback_days: int = 30,
    late_days: int = 0,
) -> SafeToSpend:
    """What can go on extras each day until the next payment, after essentials and the life fund."""
    landing = arrivals(payments, today, late_days)
    if landing:
        nxt_on = landing[0][0]
        days = max(1, (nxt_on - today).days)
    else:
        nxt_on, days = None, fallback_days
    essentials = essentials_per_day_cents * days
    spare = balance_cents - essentials - reserve_cents
    per_day = max(0, spare // days)
    until = f"until {day(nxt_on)}" if nxt_on else f"for the next {days} days"
    if per_day > 0:
        text = (
            f"After {rand(essentials)} for essentials {until} and {rand(reserve_cents)} kept for your life fund, "
            f"you can spend about {rand(per_day)} a day on extras."
        )
    else:
        text = f"Your money only covers essentials {until}, so keep extras to zero for now."
    return SafeToSpend(per_day, days, nxt_on, essentials, reserve_cents, text)
