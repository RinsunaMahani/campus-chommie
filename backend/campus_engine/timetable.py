"""A student's weekly timetable, in plain words: the classes they entered (each module's lectures,
tutorials and practicals on a weekday, from a start to an end time), which ones clash, and what the
week adds up to. Nothing here decides anything about the student; it only reads back what they typed.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import time

from .text import join, plural

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
