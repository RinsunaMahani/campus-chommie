"""Browsing the catalogue without marks: every programme by name, university and faculty, and what
closes soon across universities and funders.

The course finder's tabs read this. Nothing here takes a learner's marks or anything about them: a
programme's minimum points are shown as the university publishes them, and "you meet this" is only ever
worked out from marks the learner sends to the course finder.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .applications import CLOSING_SOON, LATE_OPEN, OPEN, WindowStatus, university_windows
from .colleges import name_matches
from .config import load_config
from .funding import Card as FundingCard
from .funding import OPEN_NOW, headline
from .schemas import University
from .text import in_days, plural


@dataclass
class ProgrammeRow:
    university: str
    university_name: str
    programme: str
    name: str
    faculty: str | None
    fields: list[str]
    min_points: float | None
    selective: bool
    verified: bool  # False while the pack holds no checked requirements for it


def programmes(packs: dict[str, University], *, query: str | None = None, university: str | None = None) -> list[ProgrammeRow]:
    """Programmes by university (A to Z), then faculty, then name; narrowed to one university and/or a
    search that matches the programme's name or its faculty's name word by word."""
    rows: list[ProgrammeRow] = []
    for uni in sorted(packs.values(), key=lambda u: u.name):
        if university and uni.university != university:
            continue
        for p in uni.programmes:
            if query and not (name_matches(p.name, query) or (p.faculty and name_matches(p.faculty, query))):
                continue
            rows.append(ProgrammeRow(
                uni.university, uni.name, p.id, p.name, p.faculty, list(p.fields),
                p.requirements.min_points if p.requirements else None, p.selective, p.requirements is not None,
            ))
    rows.sort(key=lambda r: (r.university_name, r.faculty is None, (r.faculty or "").lower(), r.name.lower()))
    return rows


def application_headline(uni: University, today: date, cfg: dict | None = None) -> WindowStatus | None:
    """The intake that matters most today for a university as a whole (open first), or None when the
    pack has no verified application dates."""
    windows = university_windows(uni, today, cfg)
    return headline(windows) if windows else None


@dataclass
class Deadline:
    kind: str  # "university" or "funding"
    id: str
    name: str
    status: str
    label: str
    closes: date
    days: int
    line: str


_OPEN_UNIVERSITY = {OPEN, CLOSING_SOON, LATE_OPEN}


def deadlines(packs: dict[str, University], funders: list[FundingCard], today: date, cfg: dict | None = None) -> list[Deadline]:
    """What's open now and closes soonest: each university's applications and each funder's, nearest
    closing date first, at most the configured number."""
    cfg = cfg or load_config()
    found: list[Deadline] = []
    for uni in packs.values():
        for w in university_windows(uni, today, cfg):
            closes = w.late_closes if w.status == LATE_OPEN else w.closes
            if w.status in _OPEN_UNIVERSITY and closes and closes >= today:
                days = (closes - today).days
                found.append(Deadline("university", uni.university, uni.name, w.status, w.label, closes, days,
                                      f"Applications for {w.intake} close {in_days(days)}."))
                break
    for c in funders:
        w = c.window
        if c.status in OPEN_NOW and w and w.closes and w.closes >= today:
            days = (w.closes - today).days
            found.append(Deadline("funding", c.funder.id, c.funder.short_name or c.funder.name, c.status, c.label,
                                  w.closes, days, f"Applications close {in_days(days)}."))
    found.sort(key=lambda d: (d.closes, d.name))
    return found[: cfg["browse"]["deadlines"]]


def summary(rows: list[ProgrammeRow]) -> str:
    unis = len({r.university for r in rows})
    if not rows:
        return "No programmes match."
    return f"{plural(len(rows), 'programme')} at {plural(unis, 'university')}."
