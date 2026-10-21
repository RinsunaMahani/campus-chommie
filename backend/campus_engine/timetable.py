"""A student's weekly timetable, in plain words: the classes they entered (each module's lectures,
tutorials and practicals on a weekday, from a start to an end time), which ones clash, and what the
week adds up to. Nothing here decides anything about the student; it only reads back what they typed.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time

from .text import in_days, join, long_day, plural, span

DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
KIND_WORDS = {"lecture": "lecture", "tutorial": "tutorial", "practical": "practical", "other": "class"}


@dataclass(frozen=True)
class Slot:
    id: str
    module: str
    kind: str
    weekday: int  # 0 = Monday
    starts: time
    ends: time

    @property
    def minutes(self) -> int:
        return (self.ends.hour * 60 + self.ends.minute) - (self.starts.hour * 60 + self.starts.minute)

    @property
    def label(self) -> str:
        return f"{self.module} {KIND_WORDS.get(self.kind, 'class')}"


def hhmm(t: time) -> str:
    return f"{t.hour:02d}:{t.minute:02d}"


@dataclass(frozen=True)
class Clash:
    a: Slot
    b: Slot
    line: str


def clashes(slots: list[Slot]) -> list[Clash]:
    """Every pair of classes on the same day whose times overlap, in day and time order, said in words."""
    found: list[Clash] = []
    ordered = sorted(slots, key=lambda s: (s.weekday, s.starts, s.ends, s.module))
    for i, a in enumerate(ordered):
        for b in ordered[i + 1:]:
            if b.weekday != a.weekday or b.starts >= a.ends:
                continue
            start, end = max(a.starts, b.starts), min(a.ends, b.ends)
            found.append(Clash(a, b, f"{a.label} and {b.label} overlap on {DAYS[a.weekday]}, "
                                     f"{hhmm(start)} to {hhmm(end)}."))
    return found


def _hours(minutes: int) -> str:
    h, m = divmod(minutes, 60)
    if m == 0:
        return plural(h, "hour")
    return f"{plural(h, 'hour')} {plural(m, 'minute')}" if h else plural(m, "minute")


def summary(slots: list[Slot]) -> list[str]:
    """What the week adds up to: how many classes and hours, the busiest day, and any clashes."""
    if not slots:
        return ["Your timetable is empty. Add your classes to see your week."]
    total = sum(s.minutes for s in slots)
    by_day: dict[int, int] = {}
    for s in slots:
        by_day[s.weekday] = by_day.get(s.weekday, 0) + s.minutes
    busiest = max(sorted(by_day), key=lambda d: by_day[d])
    days = [DAYS[d] for d in sorted(by_day)]
    lines = [
        f"{plural(len(slots), 'class')} a week, {_hours(total)} in all, on {join(days)}.",
        f"Your longest day is {DAYS[busiest]}: {_hours(by_day[busiest])} of classes.",
    ]
    found = clashes(slots)
    if found:
        lines.append(f"{plural(len(found), 'clash')} to sort out: " + " ".join(c.line for c in found))
    return lines


@dataclass(frozen=True)
class Exam:
    id: str
    module: str
    on: date
    starts: time
    minutes: int | None  # None where the exam list doesn't say

    def overlaps(self, other: "Exam") -> bool:
        if self.on != other.on:
            return False
        a0, b0 = self.starts.hour * 60 + self.starts.minute, other.starts.hour * 60 + other.starts.minute
        if self.minutes is None or other.minutes is None:
            return a0 == b0  # without a length, only the same start is surely a clash
        return a0 < b0 + other.minutes and b0 < a0 + self.minutes


def exam_clashes(exams: list[Exam]) -> list[tuple[Exam, Exam]]:
    ordered = sorted(exams, key=lambda e: (e.on, e.starts, e.module))
    return [(a, b) for i, a in enumerate(ordered) for b in ordered[i + 1:] if a.overlaps(b)]


def exam_summary(exams: list[Exam], today: date) -> list[str]:
    """How many exams, over which days, the next one and how soon, and any two at the same time."""
    if not exams:
        return ["No exams yet. Add them from your university's exam list, or one at a time."]
    ordered = sorted(exams, key=lambda e: (e.on, e.starts, e.module))
    first, last = ordered[0].on, ordered[-1].on
    lines = [f"{plural(len(exams), 'exam')}, {long_day(first) if first == last else span(first, last)}."]
    ahead = [e for e in ordered if e.on >= today]
    if ahead:
        n = ahead[0]
        lines.append(f"Next: {n.module} on {long_day(n.on)} at {hhmm(n.starts)}, {in_days((n.on - today).days)}.")
    else:
        lines.append("All your exams are behind you.")
    for a, b in exam_clashes(ordered):
        lines.append(f"{a.module} and {b.module} are both on {long_day(a.on)} at the same time: "
                     "check your exam list or ask your faculty.")
    return lines


@dataclass(frozen=True)
class Busy:
    """Something already in a day: a class, a test, an activity."""

    starts: time
    ends: time


@dataclass(frozen=True)
class FreeSlot:
    on: date
    starts: time
    ends: time

    @property
    def line(self) -> str:
        return f"{long_day(self.on)}, {hhmm(self.starts)} to {hhmm(self.ends)}"


def _mins(t: time) -> int:
    return t.hour * 60 + t.minute


def _clock(m: int) -> time:
    return time(m // 60, m % 60)


def find_time(busy: dict[date, list[Busy]], days: list[date], minutes: int, cfg: dict,
              not_before: tuple[date, int] | None = None) -> list[FreeSlot]:
    """The earliest free stretches long enough for `minutes`, between the day's start and end (config.yaml), with a
    buffer either side of whatever is already there, at most `per_day` a day so the suggestions spread over the
    week. `not_before` (today, minutes now) skips what's already past."""
    start, end = _mins(_parse(cfg["day_starts"])), _mins(_parse(cfg["day_ends"]))
    gap, step = cfg["buffer_minutes"], cfg["step_minutes"]
    found: list[FreeSlot] = []
    for d in days:
        floor = start
        if not_before and d == not_before[0]:
            floor = max(floor, not_before[1])
        elif not_before and d < not_before[0]:
            continue
        taken = sorted((max(0, _mins(b.starts) - gap), min(24 * 60, _mins(b.ends) + gap)) for b in busy.get(d, []))
        cursor, today_count = floor, 0
        for b_start, b_end in [*taken, (end, end)]:
            cursor = -(-cursor // step) * step  # up to the next step: 10:47 -> 11:00
            if b_start - cursor >= minutes and cursor + minutes <= end and today_count < cfg["per_day"]:
                found.append(FreeSlot(d, _clock(cursor), _clock(cursor + minutes)))
                today_count += 1
            cursor = max(cursor, b_end)
            if len(found) >= cfg["suggestions"]:
                return found
    return found


def _parse(hh_mm: str) -> time:
    h, m = hh_mm.split(":")
    return time(int(h), int(m))


def find_time_lines(slots: list[FreeSlot], minutes: int) -> list[str]:
    if not slots:
        return [f"No free {_hours(minutes)} this week between your classes and plans. Try a shorter time or next week."]
    return [f"Free for {_hours(minutes)}: " + "; ".join(s.line for s in slots) + "."]
