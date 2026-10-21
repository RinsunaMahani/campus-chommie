"""Do this next: the few things that matter most for a student right now, worked out from everything the app
already knows about them, each as one line, why in plain words with its numbers, and one place to go.

Signals, most urgent first when they compete:
  money runs out before payday (and sooner still if a heavy week falls before it: the two are named together),
  a test or deadline in the next few days, an exam this week, a heavy week coming, a saved bursary closing,
  a goal falling due, and what's not set up yet (classes, money).

Each step's urgency is a number so the ranking is explainable; at most `max_steps` (config.yaml) are shown.
Wording follows the alerts' rules: it describes the situation, never labels the student, never diagnoses.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from .runway import RunwayResult
from .text import day, in_days, plural, rand
from .workload import WeekLoad

#: Where a step leads: a screen of the app.
TARGETS = ("money", "week", "timetable", "funding", "support")


@dataclass(frozen=True)
class Due:
    """A test, quiz, assignment or exam the student has coming."""

    module: str
    what: str  # "Test 2", "Assignment 3", "exam"
    on: date
    at: str | None  # "09:00"; None for a deadline without a time
    weighting: float | None = None
    exam: bool = False


@dataclass(frozen=True)
class Closing:
    """A bursary the student saved, and when applications close."""

    name: str
    closes: date


@dataclass(frozen=True)
class GoalDue:
    label: str
    due: date
    left_cents: int
    per_week_cents: int


@dataclass
class Step:
    kind: str
    line: str
    why: str
    action: str
    target: str
    urgency: int
    tone: str = "normal"  # normal | attention


@dataclass
class Facts:
    today: date
    runway: RunwayResult | None = None  # None: money not set up
    weeks: list[WeekLoad] = field(default_factory=list)
    due: list[Due] = field(default_factory=list)
    closing: list[Closing] = field(default_factory=list)
    goals: list[GoalDue] = field(default_factory=list)
    classes: int = 0


def _when(d: Due, today: date) -> str:
    n = (d.on - today).days
    words = in_days(n)
    return f"{words} at {d.at}" if d.at and d.at != "23:59" else words


def next_steps(f: Facts, cfg: dict) -> list[Step]:
    """The ranked steps, at most cfg['max_steps']."""
    steps: list[Step] = []
    today = f.today
    heavy = next((w for w in f.weeks[: cfg["heavy_weeks_ahead"]] if w.colour == "red"), None)
    r = f.runway

    if r is not None and r.short_before_next and r.runs_out_on is not None:
        days_left = (r.runs_out_on - today).days
        gap = (r.next_payment_on - r.runs_out_on).days if r.next_payment_on else None
        before = f", {plural(gap, 'day')} before your next payment" if gap and gap > 0 else ""
        if heavy and heavy.week_start <= (r.next_payment_on or r.runs_out_on):
            steps.append(Step(
                "money_and_week",
                "Money runs short before payday, in a heavy week. Plan essentials now.",
                f"At your pace your money lasts about {plural(max(days_left, 0), 'day')}, to around "
                f"{day(r.runs_out_on)}{before}, and the week of {day(heavy.week_start)} is heavy: {heavy.reason}",
                "Plan essentials", "money", 100 - max(days_left, 0), "attention"))
        else:
            steps.append(Step(
                "money",
                f"Money runs out around {day(r.runs_out_on)}{before}. Keep to essentials.",
                r.explanation,
                "Plan essentials", "money", 95 - max(days_left, 0), "attention"))

    upcoming = [d for d in f.due if 0 <= (d.on - today).days <= 7]

    def also(d: Due) -> str:
        """What else is due in the same 7 days, so the line beneath says something new."""
        others = [o for o in upcoming if o is not d]
        if not others:
            return "Nothing else is due in the next 7 days."
        nxt = others[0]
        return (f"{plural(len(others), 'other thing')} due in the next 7 days, the next being "
                f"{nxt.module} {nxt.what} on {day(nxt.on)}.")

    for d in sorted(f.due, key=lambda d: (d.on, d.at or "23:59")):
        n = (d.on - today).days
        if n < 0:
            continue
        if d.exam and n <= cfg["exam_days"]:
            steps.append(Step(
                "exam", f"{d.module} exam {_when(d, today)}. Make a revision plan.",
                also(d),
                "See my week", "week", 85 - n * 3, "attention" if n <= 2 else "normal"))
        elif not d.exam and n <= cfg["due_days"]:
            weight = f", worth {d.weighting:g}% of the module" if d.weighting else ""
            steps.append(Step(
                "due", f"{d.module} {d.what} {_when(d, today)}{weight}.",
                also(d),
                "See my week", "week", 80 - n * 5 + int(d.weighting or 0) // 5, "attention" if n <= 1 else "normal"))

    if heavy and not any(s.kind == "money_and_week" for s in steps):
        steps.append(Step(
            "heavy_week", f"Heavy week from {day(heavy.week_start)}. Start on the biggest piece now.",
            heavy.reason, "Plan my week", "week", 60))

    for c in sorted(f.closing, key=lambda c: c.closes):
        n = (c.closes - today).days
        if 0 <= n <= cfg["funding_days"]:
            steps.append(Step(
                "funding", f"{c.name} closes {in_days(n)}. Finish your application.",
                f"Applications for {c.name}, which you saved, close on {day(c.closes)}.",
                "Open funding", "funding", 75 - n * 2, "attention" if n <= 3 else "normal"))

    for g in sorted(f.goals, key=lambda g: g.due):
        n = (g.due - today).days
        if g.left_cents > 0 and 0 <= n <= cfg["goal_days"]:
            steps.append(Step(
                "goal", f"Put {rand(g.per_week_cents)} aside this week for {g.label}.",
                f"{rand(g.left_cents)} still to put aside by {day(g.due)}.",
                "See my goals", "money", 50 - n // 3))

    if f.classes == 0:
        steps.append(Step(
            "setup_classes", "Add your classes, or import your timetable PDF.",
            "With your classes in, the app can plan your week and find free time.",
            "Add my classes", "timetable", 20))
    if r is None:
        steps.append(Step(
            "setup_money", "Add your balance to see how long your money lasts.",
            "One number and your next payment are enough to start.",
            "Set up money", "money", 15))

    steps.sort(key=lambda s: -s.urgency)
    return steps[: cfg["max_steps"]]
