"""Looking ahead with money, in plain words, from the student's own numbers only:

  afford(...)        "Can I afford this?": what buying it today does to how long the money lasts, and when it
                     would be fine to buy instead.
  payday_plan(...)   when the next payment lands: what goes to essentials until the payment after it, what goes
                     to the student's goals, and what's free.
  goal_pace(...)     how much to put aside each week to reach a goal by its date.

Nothing here moves money or assumes an allowance amount, a fee amount or a date the student didn't enter (a
university's fee dates come from its data pack; their amounts always come from the student).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from datetime import date, timedelta

from .runway import ExpectedPayment, arrivals, project_runway, safe_to_spend
from .text import long_day, plural, rand


@dataclass
class Afford:
    verdict: str  # yes | tight | not_now
    days_before: int | None  # how many days the money lasts without buying it (None: past the horizon)
    days_after: int | None
    wait_until: date | None  # a payment day it would be fine to buy on, if not now
    lines: list[str] = field(default_factory=list)


def _lasts(days: int | None, horizon: int) -> str:
    return f"more than {horizon} days" if days is None else plural(days, "day")


def afford(
    amount_cents: int,
    balance_cents: int,
    today: date,
    payments: list[ExpectedPayment],
    daily_cents: int,
    essentials_per_day_cents: int,
    reserve_cents: int,
    horizon_days: int = 120,
) -> Afford:
    """Buying it today, compared with not buying it: how long the money lasts either way, and whether the
    extras budget until the next payment covers it."""
    before = project_runway(balance_cents, today, payments, daily_cents, 0, horizon_days)
    after = project_runway(balance_cents - amount_cents, today, payments, daily_cents, 0, horizon_days)
    landing = arrivals(payments, today)
    nxt_on = landing[0][0] if landing else None
    until = f"your next payment on {long_day(nxt_on)}" if nxt_on else "the next 30 days"

    if amount_cents > balance_cents:
        return Afford("not_now", before.days, after.days, None, [
            f"{rand(amount_cents)} is more than your balance of about {rand(balance_cents)}."])

    if after.short_before_next:
        sooner = (before.days - after.days) if before.days is not None and after.days is not None else None
        if before.short_before_next:
            # Already short: the honest answer is to keep to essentials; no "buy it later" tip.
            return Afford("not_now", before.days, after.days, None, [
                f"Your money already runs out before {until}; this would make it {plural(sooner or 0, 'day')} sooner. "
                "Keep to essentials until then."])
        lines = [f"Buying it today, your money would last {_lasts(after.days, horizon_days)} instead of "
                 f"{_lasts(before.days, horizon_days)}: it would run out around {long_day(after.runs_out_on)}, "
                 f"before {until}."]
        wait = None
        if landing:
            # Buy it out of the next payment instead: does the money then last to the payment after it?
            first_on, first = landing[0]
            from_pay = [replace(p, amount_cents=p.amount_cents - amount_cents) if p is first else p for p in payments]
            later = project_runway(balance_cents, today, from_pay, daily_cents, 0, horizon_days)
            # It must last to the payment after that one, or a month past this one if none is expected.
            lasts_to = landing[1][0] if len(landing) > 1 else first_on + timedelta(days=30)
            if not later.short_before_next and (later.runs_out_on is None or later.runs_out_on >= lasts_to):
                wait = first_on
                lines.append(f"If you wait until your payment lands on {long_day(first_on)}, you can buy it then "
                             "and your money still lasts.")
            else:
                lines.append("Even out of your next payment it would leave you short. Putting a little aside each "
                             "week as a goal could get you there.")
        return Afford("not_now", before.days, after.days, wait, lines)

    safe = safe_to_spend(balance_cents, today, payments, essentials_per_day_cents, reserve_cents)
    spare = safe.per_day_cents * safe.days_until_next
    if amount_cents <= spare:
        left = (spare - amount_cents) // max(1, safe.days_until_next)
        return Afford("yes", before.days, after.days, None, [
            f"After it you'd still have about {rand(left)} a day for extras until {until}, with essentials "
            "and your life fund covered."])
    return Afford("tight", before.days, after.days, None, [
        f"You can, but your money still lasts past {until}, but it eats into what you set aside for "
        "essentials or your life fund, so there's less room for surprises."])


@dataclass
class Pot:
    label: str
    cents: int
    why: str


@dataclass
class PaydayPlan:
    lands_on: date
    amount_cents: int
    pots: list[Pot]
    free_cents: int
    lines: list[str]


@dataclass
class Goal:
    label: str
    left_cents: int  # still to put aside
    due_on: date | None = None
    kind: str = "goal"  # goal | family | stokvel | buffer | big_purchase
    stokvel_funded: bool = False
    amount_cents: int = 0

    def __post_init__(self):
        if not self.amount_cents:
            self.amount_cents = self.left_cents


def goal_pace(left_cents: int, due_on: date, today: date) -> tuple[int, str]:
    """How much to put aside each week to have it by the date, in words."""
    if left_cents <= 0:
        return 0, "Done: you've put it all aside."
    weeks = max(1, math.ceil((due_on - today).days / 7))
    per_week = math.ceil(left_cents / weeks)
    if due_on <= today:
        return left_cents, f"Due now: {rand(left_cents)} still to find."
    return per_week, f"About {rand(per_week)} a week for {plural(weeks, 'week')} gets you there by {long_day(due_on)}."


def pot_pace(
    kind: str,
    amount_cents: int,
    saved_cents: int,
    due_on: date | None,
    today: date,
    stokvel_funded: bool = False,
) -> tuple[int | None, str]:
    """How much to put aside each week or month for a pot or goal, in plain words."""
    left_cents = max(0, amount_cents - saved_cents)
    if kind in ("goal", "big_purchase"):
        if due_on is None:
            return None, f"{rand(left_cents)} still to put aside."
        per_week, line = goal_pace(left_cents, due_on, today)
        if kind == "big_purchase" and stokvel_funded:
            if left_cents <= 0:
                line = "Done: you've put it all aside (paying through your stokvel)."
            else:
                line = f"{line} Paying through a stokvel."
        return per_week, line
    if kind == "family":
        if left_cents <= 0:
            return 0, "Done: you've set aside your family support for this month."
        per_week = math.ceil(left_cents / 4)
        if saved_cents > 0:
            return per_week, f"{rand(amount_cents)} monthly support for family: {rand(saved_cents)} aside so far, {rand(left_cents)} still to find."
        return per_week, f"{rand(amount_cents)} a month to support family."
    if kind == "stokvel":
        if left_cents <= 0:
            return 0, "Done: your stokvel contribution for this month is put aside."
        per_week = math.ceil(left_cents / 4)
        if saved_cents > 0:
            return per_week, f"{rand(amount_cents)} monthly stokvel contribution: {rand(saved_cents)} aside so far, {rand(left_cents)} still to find."
        return per_week, f"{rand(amount_cents)} a month for your stokvel contribution."
    if kind == "buffer":
        if left_cents <= 0:
            return 0, "Done: your buffer is fully funded."
        if saved_cents > 0:
            return None, f"{rand(amount_cents)} emergency buffer: {rand(saved_cents)} aside so far, {rand(left_cents)} still to find."
        return None, f"{rand(amount_cents)} emergency buffer to keep aside."
    return None, f"{rand(left_cents)} still to put aside."


def payday_plan(
    payments: list[ExpectedPayment],
    today: date,
    essentials_per_day_cents: int,
    goals: list[Goal],
    fallback_days: int = 30,
    buffer_paydays: int = 1,
) -> PaydayPlan | None:
    """A split for the next payment: essentials until the payment after it, family and stokvel monthly
    contributions first, then emergency buffer, then a fair share for each date-based goal, and what's free.
    None when no payment is expected."""
    landing = arrivals(payments, today)
    if not landing:
        return None
    lands_on, pay = landing[0]
    following = landing[1][0] if len(landing) > 1 else None
    days = (following - lands_on).days if following else fallback_days
    pots = [Pot("Essentials", essentials_per_day_cents * days,
                f"{rand(essentials_per_day_cents)} a day for {plural(days, 'day')}"
                + (f", until your payment on {long_day(following)}" if following else ""))]

    # 1. Family and Stokvel monthly commitments (family first, then stokvel)
    monthly_pots = sorted([g for g in goals if g.kind in ("family", "stokvel")],
                          key=lambda x: (0 if x.kind == "family" else 1, x.label))
    for g in monthly_pots:
        if g.left_cents <= 0:
            continue
        share = g.left_cents
        if g.kind == "family":
            why = (f"{rand(g.amount_cents)} monthly support for family"
                   if share == g.amount_cents
                   else f"{rand(share)} still to find for family ({rand(g.amount_cents)} monthly)")
        else:
            why = (f"{rand(g.amount_cents)} monthly stokvel contribution"
                   if share == g.amount_cents
                   else f"{rand(share)} still to find for stokvel ({rand(g.amount_cents)} monthly)")
        pots.append(Pot(g.label, share, why))

    # 2. Emergency buffer
    for g in [g for g in goals if g.kind == "buffer"]:
        if g.left_cents <= 0:
            continue
        share = math.ceil(g.left_cents / max(1, buffer_paydays))
        if buffer_paydays > 1:
            why = f"{rand(g.left_cents)} still to put aside for your {rand(g.amount_cents)} buffer, over {plural(buffer_paydays, 'payday')}"
        else:
            why = f"{rand(g.left_cents)} to reach your {rand(g.amount_cents)} buffer"
        pots.append(Pot(g.label, share, why))

    # 3. Date-based goals and big purchases
    date_goals = [g for g in goals if g.kind in ("goal", "big_purchase")]
    for g in sorted(date_goals, key=lambda x: x.due_on or date.max):
        if g.left_cents <= 0 or (g.due_on is not None and g.due_on < lands_on):
            continue
        if g.due_on is not None:
            paydays = max(1, math.ceil(((g.due_on - lands_on).days + 1) / max(1, days)))
            share = math.ceil(g.left_cents / paydays)
            stokvel_note = " (paying through stokvel)" if (g.kind == "big_purchase" and g.stokvel_funded) else ""
            pots.append(Pot(g.label, share, f"{rand(g.left_cents)} still to put aside by {long_day(g.due_on)}{stokvel_note}"
                            + (f", over {plural(paydays, 'payday')}" if paydays > 1 else "")))
        else:
            pots.append(Pot(g.label, g.left_cents, f"{rand(g.left_cents)} still to put aside"))

    spoken_for = sum(p.cents for p in pots)
    free = pay.amount_cents - spoken_for
    if free >= 0:
        lines = [f"When {rand(pay.amount_cents)} lands on {long_day(lands_on)}: {rand(spoken_for)} is spoken for, "
                 f"and {rand(free)} is yours to spend freely."]
    else:
        lines = [f"When {rand(pay.amount_cents)} lands on {long_day(lands_on)}, it's {rand(-free)} short of covering "
                 "these. Essentials come first: the goals can wait for a later payday."]
    return PaydayPlan(lands_on, pay.amount_cents, pots, max(0, free), lines)
