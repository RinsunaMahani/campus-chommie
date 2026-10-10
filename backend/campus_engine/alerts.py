"""Warnings that combine workload and money, each ending in something the student can do.

The wording describes the situation. It never labels the student as "at risk", never
diagnoses, and the heavier alerts always point to campus support. Every action names
where it leads (`target`), so the app can open the right screen or the campus's own
support service.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .runway import RunwayResult
from .text import day, num
from .workload import WeekLoad

#: Where an action leads: a screen of the app, or a kind of campus support from the data pack.
TARGETS = ("week", "money", "cheap_things", "marks", "support")


@dataclass
class Action:
    text: str
    target: str  # one of TARGETS
    support_kind: str | None = None  # with target "support": counselling, financial_aid, tutoring, ...


@dataclass
class Alert:
    kind: str  # combined | heavy_week | money | module
    title: str
    message: str
    actions: list[Action] = field(default_factory=list)


COUNSELLING = Action("If it all feels like too much, campus counselling is there for you.", "support", "counselling")
FINANCIAL_AID = Action("Ask your campus financial aid office about the payment date.", "support", "financial_aid")


def alerts_for(weeks: list[WeekLoad], runway: RunwayResult | None, lookahead_weeks: int = 3) -> list[Alert]:
    """A heavy week in the next `lookahead_weeks`, money running out before the next payment, or both
    together. `runway` is None before the student has entered their money."""
    alerts: list[Alert] = []
    heavy = next((w for w in weeks[:lookahead_weeks] if w.colour == "red"), None)
    money_short = runway is not None and runway.short_before_next

    if heavy and money_short:
        alerts.append(
            Alert(
                "combined",
                f"Heavy week from {day(heavy.week_start)}, and money running short",
                f"{heavy.reason} Your money may run out around {day(runway.runs_out_on)}, "
                "before your next payment lands.",
                [
                    Action("Keep spending to essentials until the payment lands. Your life fund is paused, not gone.", "money"),
                    Action("Plan the heavy days now, starting with whatever carries the most weight.", "week"),
                    FINANCIAL_AID,
                    COUNSELLING,
                ],
            )
        )
        return alerts

    if heavy:
        alerts.append(
            Alert(
                "heavy_week",
                f"Heavy week from {day(heavy.week_start)}",
                heavy.reason,
                [
                    Action("Start preparing now, beginning with whatever carries the most weight.", "week"),
                    Action("Book a campus tutor session if a module is giving you trouble.", "support", "tutoring"),
                    Action("If the pressure builds, campus counselling is there for you.", "support", "counselling"),
                ],
            )
        )
    if money_short:
        alerts.append(
            Alert(
                "money",
                "Money may run out before your next payment",
                runway.explanation,
                [
                    Action("Keep spending to essentials until the payment lands.", "money"),
                    Action("See what's free or cheap near your campus.", "cheap_things"),
                    FINANCIAL_AID,
                ],
            )
        )
    return alerts


def module_alert(code: str, target: float, standing_message: str) -> Alert:
    """A module where even full marks on what's left wouldn't reach the student's own target."""
    return Alert(
        "module",
        f"{code}: your {num(target)}% target is out of reach",
        standing_message,
        [
            Action("Talk to your lecturer or a campus tutor about what's left and your options.", "support", "tutoring"),
            Action("See where you stand in each module.", "marks"),
            Action("If it's weighing on you, campus counselling is there for you.", "support", "counselling"),
        ],
    )
