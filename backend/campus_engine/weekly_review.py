"""Your week in review: at the end of a student's week (the one their money check-in uses), what's behind them, what's
coming in the next few days, how their marks moved and how their spending compares with their usual.

Everything is worked out from what the app already holds; nothing new is asked or kept. Marks are compared before and
after the ones the student entered or changed during the week, so no history of marks is stored. A week still under
way compares spending so far with the student's usual for the same number of days, never a whole week.

Wording follows the alerts' rules: it describes the week, never labels the student, never diagnoses; a mark that
went down, or a target out of reach, always points to campus support.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from .text import day, in_days, join, num, plural, rand

#: What a dated item is: a class event's kind, an exam the student keeps, a saved funder closing, a goal's date.
KINDS = ("quiz", "assignment", "practical", "test", "exam", "funding", "goal")


@dataclass(frozen=True)
class Item:
    kind: str
    label: str  # "STK110 Test 2", "NSFAS closes", "Laptop"
    on: date
    at: str | None = None  # "09:00"; None for a deadline without a time


@dataclass(frozen=True)
class MarkEntered:
    module: str
    name: str
    mark: float


@dataclass(frozen=True)
class ModuleMarks:
    """A module's average (on the marks written so far) before the week's marks and after them."""

    code: str
    target: float
    before: float | None
    after: float | None
    out_of_reach: bool = False  # after the week's marks, even 100% on the rest wouldn't reach the target


@dataclass(frozen=True)
class Facts:
    week_start: date
    week_end: date
    today: date
    behind: list[Item] = field(default_factory=list)  # dated in the week, up to today
    coming: list[Item] = field(default_factory=list)  # dated in the next `coming_days`
    marks: list[MarkEntered] = field(default_factory=list)
    modules: list[ModuleMarks] = field(default_factory=list)
    checked_in: bool = False
    streak_weeks: int = 0
    spent_cents: int | None = None  # this week (so far); None: nothing logged
    earlier_weeks_cents: list[int | None] = field(default_factory=list)  # the weeks before, newest first


@dataclass(frozen=True)
class Line:
    text: str
    kind: str


@dataclass(frozen=True)
class Move:
    code: str
    before: float | None
    after: float | None
    direction: str  # up | down | same | first
    text: str


@dataclass(frozen=True)
class Spending:
    spent_cents: int | None
    usual_cents: int | None  # the usual for the same number of days
    days: int  # days of the week so far (7 once it's over)
    weeks_compared: int
    direction: str  # less | same | more | unknown
    text: str
    weeks: list[int | None]  # oldest first, this week last: for a small bar chart


@dataclass(frozen=True)
class Review:
    week_start: date
    week_end: date
    finished: bool  # the week is over (or today is its last day)
    headline: str
    done: list[Line]
    coming: list[Line]
    marks: list[Move]
    spending: Spending
    support: bool  # a mark went down or a target is out of reach: point to campus support


def _week_word(f: Facts) -> str:
    """'this week' while it's the current one (its last day included), 'that week' once it's past."""
    return "that week" if f.today > f.week_end else "this week"


def _item(i: Item, today: date, *, ahead: bool) -> Line:
    when = f"{day(i.on)}" + (f" at {i.at}" if i.at else "")
    if i.kind == "funding":
        text = f"{i.label} closes {in_days((i.on - today).days)} ({when})" if ahead else f"{i.label} closed ({when})"
    elif i.kind == "goal":
        text = f"Your goal \"{i.label}\" is due {in_days((i.on - today).days)} ({when})" if ahead else f"Your goal \"{i.label}\" was due ({when})"
    else:
        text = f"{i.label}, {in_days((i.on - today).days)} ({when})" if ahead else f"{i.label} ({when})"
    return Line(text, i.kind)


def _done(f: Facts, cfg: dict) -> list[Line]:
    out = [_item(i, f.today, ahead=False) for i in sorted(f.behind, key=lambda i: (i.on, i.at or ""))][: cfg["max_items"]]
    if f.marks:
        named = [f"{m.module} {m.name} ({num(round(m.mark, 1))}%)" for m in f.marks[:3]]
        if len(f.marks) > 3:
            named.append(f"{len(f.marks) - 3} more")
        out.append(Line(f"You entered {plural(len(f.marks), 'mark')}: {join(named)}.", "marks"))
    if f.checked_in:
        streak = f" ({plural(f.streak_weeks, 'week')} in a row)" if f.streak_weeks > 1 else ""
        out.append(Line(f"You checked in on your money{streak}.", "checkin"))
    return out


def _coming(f: Facts, cfg: dict) -> list[Line]:
    items = sorted(f.coming, key=lambda i: (i.on, i.at or ""))
    out = [_item(i, f.today, ahead=True) for i in items[: cfg["max_items"]]]
    if len(items) > cfg["max_items"]:
        out.append(Line(f"And {len(items) - cfg['max_items']} more: see your week.", "more"))
    return out


def _moves(f: Facts) -> list[Move]:
    week = _week_word(f)
    out = []
    for m in sorted(f.modules, key=lambda m: m.code):
        if m.after is None:
            continue
        after = round(m.after, 1)
        if m.before is None:
            out.append(Move(m.code, None, after, "first", f"{m.code}: your first marks are in, averaging {num(after)}%."))
            continue
        before = round(m.before, 1)
        if after > before:
            direction, how = "up", f"went up from {num(before)}% to {num(after)}%"
        elif after < before:
            direction, how = "down", f"moved from {num(before)}% to {num(after)}%"
        else:
            direction, how = "same", f"stayed at {num(after)}%"
        out.append(Move(m.code, before, after, direction, f"{m.code}: your average {how} with {week}'s marks."))
    return out


def _spending(f: Facts, cfg: dict) -> Spending:
    days = min(7, (min(f.today, f.week_end) - f.week_start).days + 1)
    earlier = [w for w in f.earlier_weeks_cents[: cfg["compare_weeks"]] if w is not None]
    bars = list(reversed(f.earlier_weeks_cents[: cfg["compare_weeks"]])) + [f.spent_cents]
    so_far = _week_word(f) if days == 7 else f"so far this week ({days} of 7 days)"
    if f.spent_cents is None:
        return Spending(None, None, days, len(earlier), "unknown",
                        f"No spending logged {so_far}. A money check-in takes a minute and fills in the week.", bars)
    if not earlier:
        return Spending(f.spent_cents, None, days, 0, "unknown",
                        f"You spent {rand(f.spent_cents)} {so_far}. Keep logging: from next week you'll see how it compares.",
                        bars)
    usual = round(sum(earlier) / len(earlier) * days / 7)
    weeks = plural(len(earlier), "week")
    usual_words = f"your usual of about {rand(usual)}" + ("" if days == 7 else f" for {plural(days, 'day')}")
    gap = f.spent_cents - usual
    if usual == 0 or abs(gap) <= usual * cfg["same_band"]:
        direction, how = "same", f"about the same as {usual_words}"
    elif gap < 0:
        direction, how = "less", f"{rand(-gap)} less than {usual_words}"
    else:
        direction, how = "more", f"{rand(gap)} more than {usual_words}"
    return Spending(f.spent_cents, usual, days, len(earlier), direction,
                    f"You spent {rand(f.spent_cents)} {so_far}, {how} (from the last {weeks}).", bars)


def _headline(f: Facts, cfg: dict) -> str:
    """Counts only: things behind the student (each dated item, the marks entered, the check-in) and dates ahead."""
    behind = len(f.behind) + (1 if f.marks else 0) + (1 if f.checked_in else 0)
    ahead = len(f.coming)
    if not behind and not ahead:
        return "A quiet week. Add your classes, marks and money to see more here."
    parts = []
    if behind:
        parts.append(f"{plural(behind, 'thing')} done")
    if ahead:
        parts.append(f"{plural(ahead, 'date')} in the next {plural(cfg['coming_days'], 'day')}")
    text = join(parts)
    return text[0].upper() + text[1:] + "."


def weekly_review(f: Facts, cfg: dict) -> Review:
    done, coming = _done(f, cfg), _coming(f, cfg)
    moves = _moves(f)
    support = any(m.direction == "down" for m in moves) or any(m.out_of_reach for m in f.modules)
    return Review(
        week_start=f.week_start,
        week_end=f.week_end,
        finished=f.today >= f.week_end,
        headline=_headline(f, cfg),
        done=done,
        coming=coming,
        marks=moves,
        spending=_spending(f, cfg),
        support=support,
    )
