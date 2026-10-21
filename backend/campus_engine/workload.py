"""Weekly workload score: how heavy each week looks, and why.

Each event gets a base load by type, scaled by its weighting, and counts extra
when it falls close to another event. The week's colour comes from thresholds in
config.yaml, and every week carries a plain-language reason.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from .config import load_config
from .text import join, plural

KIND_ORDER = ["exam", "test", "practical", "assignment", "quiz"]


@dataclass
class AcademicEvent:
    title: str
    kind: str  # quiz | assignment | practical | test | exam
    starts: datetime
    module: str | None = None
    weighting: float | None = None  # share of the module mark in %, if known
    venue: str | None = None
    verified: bool = True
    cancelled: bool = False


@dataclass
class WeekLoad:
    week_start: date
    score: float
    colour: str  # green | amber | red
    reason: str
    events: list[AcademicEvent] = field(default_factory=list)
    clustered: int = 0

    @property
    def has_exam(self) -> bool:
        return any(e.kind == "exam" for e in self.events)


def week_start(d: date) -> date:
    """Monday of the week containing d."""
    return d - timedelta(days=d.weekday())


def clustered_indices(events: list[AcademicEvent], hours: float) -> set[int]:
    """Indices of events that fall within `hours` of another event."""
    window = timedelta(hours=hours)
    flagged: set[int] = set()
    for i, a in enumerate(events):
        if any(i != j and abs(a.starts - b.starts) <= window for j, b in enumerate(events)):
            flagged.add(i)
    return flagged


def event_load(event: AcademicEvent, clustered: bool, cfg: dict) -> float:
    wl = cfg["workload"]
    base = wl["base_load"].get(event.kind, 2)
    weight = 1 + (event.weighting or 0) / 100
    return base * weight * (wl["cluster_multiplier"] if clustered else 1)


def _reason(events: list[AcademicEvent], n_clustered: int, colour: str, hours: float) -> str:
    if not events:
        return "Nothing due this week."
    counts: dict[str, int] = {}
    for e in events:
        counts[e.kind] = counts.get(e.kind, 0) + 1
    kinds = [k for k in KIND_ORDER if k in counts] + sorted(k for k in counts if k not in KIND_ORDER)
    text = join([plural(counts[k], k) for k in kinds])
    if n_clustered:
        text += f", with {n_clustered} within {hours:g} hours of another"
    labels = {"green": "Manageable", "amber": "Busy", "red": "Heavy"}
    return f"{labels[colour]}: {text}."


def weekly_load(
    events: list[AcademicEvent],
    start: date,
    weeks: int = 8,
    cfg: dict | None = None,
) -> list[WeekLoad]:
    """Score `weeks` weeks starting with the week that contains `start`."""
    cfg = cfg or load_config()
    wl = cfg["workload"]
    live = [e for e in events if not e.cancelled]
    flagged = clustered_indices(live, wl["cluster_hours"])
    first = week_start(start)
    out: list[WeekLoad] = []
    for w in range(weeks):
        ws = first + timedelta(weeks=w)
        we = ws + timedelta(days=7)
        idx = [i for i, e in enumerate(live) if ws <= e.starts.date() < we]
        score = round(sum(event_load(live[i], i in flagged, cfg) for i in idx), 1)
        if score >= wl["thresholds"]["red"]:
            colour = "red"
        elif score >= wl["thresholds"]["amber"]:
            colour = "amber"
        else:
            colour = "green"
        week_events = sorted((live[i] for i in idx), key=lambda e: e.starts)
        n_clustered = sum(1 for i in idx if i in flagged)
        out.append(
            WeekLoad(
                week_start=ws,
                score=score,
                colour=colour,
                reason=_reason(week_events, n_clustered, colour, wl["cluster_hours"]),
                events=week_events,
                clustered=n_clustered,
            )
        )
    return out
