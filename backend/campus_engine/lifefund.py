"""Life fund signal: green to go out, amber to go easy, paused when money or exams say so."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .runway import RunwayResult
from .text import join
from .workload import WeekLoad


@dataclass
class LifeFundSignal:
    state: str  # green | amber | paused
    reason: str
    resume_hint: str | None = None


def life_fund_signal(
    runway: RunwayResult,
    week: WeekLoad | None,
    today: date,
    buffer_days: int = 3,
) -> LifeFundSignal:
    overdue = runway.next_payment is not None and runway.next_payment.expected_on < today
    short = runway.short_before_next
    exam_crunch = week is not None and week.colour == "red" and week.has_exam

    if short or overdue or exam_crunch:
        reasons = []
        if short:
            reasons.append("your money may run out before the next payment")
        if overdue:
            reasons.append("a payment is overdue")
        if exam_crunch:
            reasons.append("it's a heavy exam week")
        resume = "Resumes when your next payment lands." if (short or overdue) else "Resumes after the exam week."
        return LifeFundSignal("paused", "Paused because " + join(reasons) + ".", resume)

    if runway.next_payment_on is None or runway.balance_before_next_cents is None:
        money_ok = runway.runs_out_on is None
    else:
        money_ok = runway.balance_before_next_cents >= runway.daily_spend_cents * buffer_days
    week_ok = week is None or week.colour != "red"

    if money_ok and week_ok:
        return LifeFundSignal("green", "Good week to go out: your essentials are covered and the week is manageable.")
    reasons = []
    if not money_ok:
        reasons.append("money is tight just before your next payment")
    if not week_ok:
        reasons.append("it's a heavy week")
    return LifeFundSignal("amber", "Go easy: " + join(reasons) + ".")
