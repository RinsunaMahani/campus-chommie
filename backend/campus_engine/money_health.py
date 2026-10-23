"""Money health: five simple checks a student can act on, from their own numbers.

1. Money lasts until the next payment (runway).
2. A buffer pot exists and has something in it (G3).
3. This week's spending is within safe-to-spend.
4. Every big purchase or fee goal has a weekly amount the plan can cover (goal_pace).
5. Checked in this week (G4).

Pure Python: no Flask or SQLAlchemy imports.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .money_plan import Goal, PaydayPlan, goal_pace
from .runway import RunwayResult
from .text import day, plural, rand


STATUS_DONE = "done"
STATUS_NOT_YET = "not yet"
STATUS_CANT_TELL = "can't tell"

CHECK_RUNWAY = "runway"
CHECK_BUFFER = "buffer"
CHECK_SPENDING = "spending"
CHECK_GOALS = "goals"
CHECK_CHECKIN = "checkin"


@dataclass
class HealthCheck:
    """One of five checks on a student's money health."""

    id: str  # runway | buffer | spending | goals | checkin
    title: str
    status: str  # done | not yet | can't tell
    line: str
    action: str | None = None
    target: str | None = None


@dataclass
class MoneyHealth:
    """The five money health checks and the summary."""

    checks: list[HealthCheck]
    done_count: int
    total_count: int
    line: str


def check_money_health(
    today: date,
    runway: RunwayResult | None = None,
    goals: list[Goal] | None = None,
    this_week_spend_cents: int | None = None,
    safe_per_day_cents: int | None = None,
    plan: PaydayPlan | None = None,
    checked_in_this_week: bool | None = None,
    streak_weeks: int = 0,
    min_buffer_cents: int = 1,
) -> MoneyHealth:
    """Evaluate the student's five money health checks using their own numbers."""
    c1 = _check_runway(runway)
    c2 = _check_buffer(goals, min_buffer_cents=min_buffer_cents)
    c3 = _check_spending(this_week_spend_cents, safe_per_day_cents)
    c4 = _check_goals(goals, plan, today)
    c5 = _check_checkin(checked_in_this_week, streak_weeks)

    checks = [c1, c2, c3, c4, c5]
    done_count = sum(1 for c in checks if c.status == STATUS_DONE)
    total_count = len(checks)
    line = f"{done_count} of {total_count} checks done"

    return MoneyHealth(
        checks=checks,
        done_count=done_count,
        total_count=total_count,
        line=line,
    )


def _check_runway(runway: RunwayResult | None) -> HealthCheck:
    if runway is None:
        return HealthCheck(
            id="runway",
            title="Runway to payday",
            status=STATUS_CANT_TELL,
            line="Add your balance and settings to see if your money lasts until payday.",
            action="Set up money",
            target="/money/settings",
        )
    if runway.runs_out_on is None:
        days_text = f"beyond {runway.days} days" if runway.days else "beyond the planning horizon"
        return HealthCheck(
            id="runway",
            title="Runway to payday",
            status=STATUS_DONE,
            line=f"Your money lasts {days_text}, well past your next payment.",
            action=None,
            target="/money",
        )
    if runway.next_payment_on is None:
        return HealthCheck(
            id="runway",
            title="Runway to payday",
            status=STATUS_CANT_TELL,
            line=f"Money lasts about {plural(runway.days or 0, 'day')}, but no upcoming payment is set.",
            action="Add next payment",
            target="/money",
        )
    if runway.short_before_next:
        days_short = max(1, (runway.next_payment_on - runway.runs_out_on).days)
        return HealthCheck(
            id="runway",
            title="Runway to payday",
            status=STATUS_NOT_YET,
            line=f"Money runs out on {day(runway.runs_out_on)}, {plural(days_short, 'day')} before your payment on {day(runway.next_payment_on)}.",
            action="Review runway",
            target="/money",
        )
    return HealthCheck(
        id="runway",
        title="Runway to payday",
        status=STATUS_DONE,
        line=f"Money lasts until {day(runway.runs_out_on)}, past your payment on {day(runway.next_payment_on)}.",
        action=None,
        target="/money",
    )


def _check_buffer(goals: list[Goal] | None, min_buffer_cents: int = 1) -> HealthCheck:
    if goals is None:
        return HealthCheck(
            id="buffer",
            title="Emergency buffer",
            status=STATUS_CANT_TELL,
            line="Add your pots to see your emergency buffer status.",
            action="Add a pot",
            target="/money/goal",
        )
    buf = next((g for g in goals if g.kind == "buffer"), None)
    if buf is None:
        return HealthCheck(
            id="buffer",
            title="Emergency buffer",
            status=STATUS_NOT_YET,
            line="No emergency buffer pot set up yet to protect against surprise costs.",
            action="Add a buffer pot",
            target="/money/goal",
        )
    saved = getattr(buf, "saved_cents", 0)
    if not saved and buf.amount_cents > buf.left_cents:
        saved = buf.amount_cents - buf.left_cents
    if saved < min_buffer_cents:
        return HealthCheck(
            id="buffer",
            title="Emergency buffer",
            status=STATUS_NOT_YET,
            line=f"Your {rand(buf.amount_cents)} buffer has R0 put aside so far.",
            action="Fund your buffer",
            target="/money/goal",
        )
    return HealthCheck(
        id="buffer",
        title="Emergency buffer",
        status=STATUS_DONE,
        line=f"{rand(saved)} put aside towards your {rand(buf.amount_cents)} emergency buffer.",
        action=None,
        target="/money",
    )


def _check_spending(this_week_spend_cents: int | None, safe_per_day_cents: int | None) -> HealthCheck:
    if safe_per_day_cents is None:
        return HealthCheck(
            id="spending",
            title="Spending within safe limit",
            status=STATUS_CANT_TELL,
            line="Set your balance and daily essentials to see what's safe to spend.",
            action="Set up money",
            target="/money/settings",
        )
    if this_week_spend_cents is None:
        return HealthCheck(
            id="spending",
            title="Spending within safe limit",
            status=STATUS_CANT_TELL,
            line="No spending recorded this week yet.",
            action="Check in spending",
            target="/money/checkin",
        )
    weekly_safe = max(0, safe_per_day_cents * 7)
    if this_week_spend_cents <= weekly_safe:
        return HealthCheck(
            id="spending",
            title="Spending within safe limit",
            status=STATUS_DONE,
            line=f"{rand(this_week_spend_cents)} spent this week, within your {rand(weekly_safe)} weekly safe limit.",
            action=None,
            target="/money",
        )
    over = this_week_spend_cents - weekly_safe
    return HealthCheck(
        id="spending",
        title="Spending within safe limit",
        status=STATUS_NOT_YET,
        line=f"{rand(this_week_spend_cents)} spent this week is {rand(over)} over your {rand(weekly_safe)} safe limit.",
        action="Review spending",
        target="/money",
    )


def _check_goals(goals: list[Goal] | None, plan: PaydayPlan | None, today: date) -> HealthCheck:
    if not goals:
        return HealthCheck(
            id="goals",
            title="Upcoming goals covered",
            status=STATUS_CANT_TELL,
            line="Add your upcoming goals to see if your plan can cover them.",
            action="Add a goal",
            target="/money/goal",
        )
    dated_goals = [
        g for g in goals
        if g.kind in ("big_purchase", "goal") and g.due_on is not None and g.left_cents > 0
    ]
    if not dated_goals:
        return HealthCheck(
            id="goals",
            title="Upcoming goals covered",
            status=STATUS_DONE,
            line="No upcoming big purchase or fee deadlines to fund right now.",
            action=None,
            target="/money",
        )
    if plan is None:
        return HealthCheck(
            id="goals",
            title="Upcoming goals covered",
            status=STATUS_CANT_TELL,
            line=f"{plural(len(dated_goals), 'upcoming goal')} set, but no payday plan is available.",
            action="View payday plan",
            target="/money",
        )
    total_weekly = sum(goal_pace(g.left_cents, g.due_on, today)[0] for g in dated_goals)
    if plan.free_cents >= 0:
        return HealthCheck(
            id="goals",
            title="Upcoming goals covered",
            status=STATUS_DONE,
            line=f"All {plural(len(dated_goals), 'goal')} covered by your plan ({rand(total_weekly)} a week needed).",
            action=None,
            target="/money",
        )
    return HealthCheck(
        id="goals",
        title="Upcoming goals covered",
        status=STATUS_NOT_YET,
        line=f"Your plan is short of covering {rand(total_weekly)} a week needed for {plural(len(dated_goals), 'goal')}.",
        action="Review goals",
        target="/money",
    )


def _check_checkin(checked_in_this_week: bool | None, streak_weeks: int = 0) -> HealthCheck:
    if checked_in_this_week is None:
        return HealthCheck(
            id="checkin",
            title="Weekly check-in",
            status=STATUS_CANT_TELL,
            line="Check-in status not available.",
            action="Check in",
            target="/money/checkin",
        )
    if checked_in_this_week:
        streak_suffix = f" · {streak_weeks} weeks in a row" if streak_weeks > 1 else ""
        return HealthCheck(
            id="checkin",
            title="Weekly check-in",
            status=STATUS_DONE,
            line=f"Checked in for this week{streak_suffix}.",
            action=None,
            target="/money/checkin",
        )
    return HealthCheck(
        id="checkin",
        title="Weekly check-in",
        status=STATUS_NOT_YET,
        line="You haven't checked in your spending for this week yet.",
        action="Check in now",
        target="/money/checkin",
    )
