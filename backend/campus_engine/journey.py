"""First steps after acceptance: from accepting an offer to the first lecture.

For the intake a new student is starting (this year's while its first lecture is still ahead, and
next year's): how to accept an offer, when to register, orientation and the first lecture, from
the university's own calendar, and what national funders do at registration. On today's date, in
plain words, with sources. A date nobody has published is said to be not published; last year's
dates are offered as last year's.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from .schemas import CalendarEntry, FundingPack, University
from .text import in_days, join, long_day, span

ACCEPT = "accept"
REGISTER = "register"
ORIENTATION = "orientation"
FIRST_LECTURE = "first_lecture"
TITLES = {ACCEPT: "Accept your offer", REGISTER: "Register", ORIENTATION: "Orientation", FIRST_LECTURE: "First lecture"}
DATED = (REGISTER, ORIENTATION, FIRST_LECTURE)

DONE = "done"
NOW = "now"
AHEAD = "ahead"
WHEN_OFFERED = "when_offered"
NOT_PUBLISHED = "not_published"
NOT_VERIFIED = "not_verified"
STATUS_LABELS = {
    DONE: "Done",
    NOW: "Now",
    AHEAD: "Coming up",
    WHEN_OFFERED: "When your offer comes",
    NOT_PUBLISHED: "Not published yet",
    NOT_VERIFIED: "Not verified yet",
}


@dataclass
class Step:
    key: str
    title: str
    status: str
    starts: date | None = None
    ends: date | None = None
    days: int | None = None  # until it starts, while it's ahead
    lines: list[str] = field(default_factory=list)
    source_urls: list[str] = field(default_factory=list)

    @property
    def label(self) -> str:
        return STATUS_LABELS[self.status]


@dataclass
class FirstSteps:
    university: str
    name: str
    intake: int
    steps: list[Step]
    notes: list[str] = field(default_factory=list)


def _entries(uni: University, year: int, step: str) -> list[CalendarEntry]:
    """A step's calendar entries for one year: first-years' own where the calendar has them."""
    found = [e for e in uni.calendar if e.step == step and e.start.year == year and e.who != "returning"]
    first_years = [e for e in found if e.who == "first_years"]
    return sorted(first_years or found, key=lambda e: e.start)


def intakes(uni: University, today: date) -> list[int]:
    """This year's intake until its last step is over (UP's registration closes after its first
    lecture), and next year's."""
    last_days = [_last_day(e, key) for key in DATED for e in _entries(uni, today.year, key)]
    if any(d >= today for d in last_days):
        return [today.year, today.year + 1]
    return [today.year + 1]


def _last_day(entry: CalendarEntry, key: str) -> date:
    """The first lecture is one day, even when its entry spans the whole term."""
    return entry.start if key == FIRST_LECTURE else entry.last_day


def _url(uni: University, source_id: str) -> str | None:
    source = uni.source(source_id)
    return source.url if source else None


def _where(uni: University, entry: CalendarEntry) -> str:
    names = {c.id: c.name for c in uni.campuses}
    return f" ({join([names.get(c, c) for c in entry.campuses])})" if entry.campuses else ""


def _when(entry: CalendarEntry, key: str) -> str:
    if key == FIRST_LECTURE or entry.end in (None, entry.start):
        return long_day(entry.start)
    return span(entry.start, entry.last_day)


def _describe(uni: University, entry: CalendarEntry, key: str, days: int | None = None) -> str:
    countdown = f" ({in_days(days)})" if days is not None else ""
    if key == FIRST_LECTURE:
        names = {c.id: c.name for c in uni.campuses}
        at = f" at {join([names.get(c, c) for c in entry.campuses])}" if entry.campuses else ""
        return f"Lectures start on {long_day(entry.start)}{at}{countdown}."
    return f"{entry.name}{_where(uni, entry)}: {_when(entry, key)}{countdown}."


def _dated(uni: University, key: str, entries: list[CalendarEntry], today: date) -> Step:
    starts = entries[0].start
    ends = max(_last_day(e, key) for e in entries)
    step = Step(key, TITLES[key], AHEAD, starts=starts, ends=ends)
    if ends < today:
        step.status = DONE
    elif starts <= today:
        step.status = NOW
    else:
        step.days = (starts - today).days
    for i, e in enumerate(entries):
        step.lines.append(_describe(uni, e, key, step.days if i == 0 else None))
        if e.note:
            step.lines.append(e.note)
    step.source_urls = list(dict.fromkeys(u for u in (_url(uni, e.source) for e in entries) if u))
    return step


def _accept(uni: University) -> Step:
    accepting = uni.applications.accepting if uni.applications else None
    if accepting is None:
        return Step(ACCEPT, TITLES[ACCEPT], NOT_VERIFIED, lines=["How to accept an offer: not verified yet."])
    url = _url(uni, accepting.source)
    return Step(ACCEPT, TITLES[ACCEPT], WHEN_OFFERED, lines=[accepting.text], source_urls=[url] if url else [])


def _for_intake(uni: University, year: int, today: date, funding: FundingPack | None) -> FirstSteps:
    out = FirstSteps(uni.university, uni.name, year, [_accept(uni)])
    dated = {key: _entries(uni, year, key) for key in DATED}
    published = any(dated.values())
    if not published:
        out.notes.append(f"{uni.name} hasn't published its {year} dates yet.")
    for key in DATED:
        if dated[key]:
            step = _dated(uni, key, dated[key], today)
        elif published:
            step = Step(key, TITLES[key], NOT_VERIFIED, lines=["Not verified yet."])
        else:
            step = Step(key, TITLES[key], NOT_PUBLISHED, lines=["Not published yet."])
            earlier = _entries(uni, year - 1, key)
            if earlier:
                step.lines += [f"For {year - 1}: {_describe(uni, e, key)}" for e in earlier]
                step.source_urls = list(dict.fromkeys(u for u in (_url(uni, e.source) for e in earlier) if u))
        if key == REGISTER and funding:
            for funder in funding.funders:
                if funder.at_registration:
                    step.lines.append(funder.at_registration.text)
                    source = funding.source(funder.at_registration.source)
                    if source:
                        step.source_urls.append(source.url)
        out.steps.append(step)
    return out


def first_steps(uni: University, today: date, funding: FundingPack | None = None) -> list[FirstSteps]:
    """First steps for each intake a new student could be starting."""
    return [_for_intake(uni, year, today, funding) for year in intakes(uni, today)]
