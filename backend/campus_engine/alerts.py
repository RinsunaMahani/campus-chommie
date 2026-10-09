"""Warnings that combine workload and money, each ending in something the student can do.

The wording describes the situation. It never labels the student as "at risk".
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .runway import RunwayResult
from .text import day
from .workload import WeekLoad


@dataclass
class Alert:
    kind: str  # combined | heavy_week | money
    title: str
    message: str
    actions: list[str] = field(default_factory=list)


def alerts_for(weeks: list[WeekLoad], runway: RunwayResult, lookahead_weeks: int = 3) -> list[Alert]:
    alerts: list[Alert] = []
    upcoming = weeks[:lookahead_weeks]
    heavy = next((w for w in upcoming if w.colour == "red"), None)
    money_short = runway.short_before_next

    if heavy and money_short:
        alerts.append(
            Alert(
                "combined",
                f"Heavy week from {day(heavy.week_start)}, and money running short",
                f"{heavy.reason} Your money may run out around {day(runway.runs_out_on)}, "
                "before your next payment lands.",
                [
                    "Keep spending to essentials until the payment lands. Your life fund is paused, not gone.",
                    "Find a study partner from your class for the heavy days.",
                    "Ask your campus financial aid office about the payment date.",
                    "If it all feels like too much, campus counselling is there for you.",
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
                    "Start preparing now, beginning with whatever carries the most weight.",
                    "Find a study partner from your class.",
                    "Book a campus tutor session if a module is giving you trouble.",
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
                    "Keep spending to essentials until the payment lands.",
                    "Check the grocery and transport savings for your campus.",
                    "Ask your campus financial aid office about the payment date.",
                ],
            )
        )
    return alerts
