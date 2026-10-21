"""
The week strip: the coming weeks scored Manageable, Busy or Heavy from the
student's verified class events (the engine's workload score, with a
one-line reason), and their university's own calendar beside each week (test
weeks, exams, recess, deadlines) for their campus. The calendar is context:
it never adds to the score, which comes only from verified events.

My money asks `this_week()` for the life fund.
"""
from __future__ import annotations

import math
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from campus_engine.config import load_config
from campus_engine.schemas import CalendarEntry, University
from campus_engine.workload import WeekLoad, week_start, weekly_load
from src.core.exceptions import ValidationError
from src.domains.catalogue.universities.services import university_service as catalogue
from src.domains.classes.classes.services import class_service as classes
from src.domains.student.profile.services import profile_service as profile

from ..constants import LOAD_LABELS, RANGE_MAX_DAYS, TIMEZONE
from ..models import ClassEvent
from ..repositories import events_repository as repo
from . import events_service

NO_CLASSES = "Join your classes to see their tests and deadlines here: your class rep has the invite code."
NO_UNIVERSITY = "Choose your university in your profile to see its calendar here."


def _today() -> date:
    """Today in South Africa: every student's day."""
    return datetime.now(ZoneInfo(TIMEZONE)).date()


def _scored(class_ids: list, first: date, weeks: int) -> tuple[list[WeekLoad], dict[int, ClassEvent]]:
    """The engine's weeks, and which row each of its events came from. Events just outside the
    range are passed too, so a test on Sunday still counts as close to one on Monday."""
    cfg = load_config()
    pad = timedelta(days=math.ceil(cfg["workload"]["cluster_hours"] / 24))
    rows = repo.events_between(class_ids, first - pad, first + timedelta(weeks=weeks) + pad, live_only=True)
    pairs = [(row, events_service.academic(row)) for row in rows]
    loads = weekly_load([ev for _, ev in pairs], first, weeks, cfg)
    return loads, {id(ev): row for row, ev in pairs}


def loads(user, today: date, weeks: int) -> list[WeekLoad]:
    """The engine's weeks from this one, for the alerts; empty for a student in no classes yet."""
    class_ids = [m.class_id for m in classes.memberships(user)]
    if not class_ids:
        return []
    return _scored(class_ids, week_start(today), weeks)[0]


def this_week(user, today: date) -> WeekLoad | None:
    """This week's load, for the life fund; None for a student in no classes yet."""
    weeks = loads(user, today, 1)
    return weeks[0] if weeks else None


def week(user, weeks: int, start: date | None) -> dict:
    today = _today()
    start = start or today
    if abs((start - today).days) > RANGE_MAX_DAYS:
        raise ValidationError("Please check the highlighted fields.", errors=[{"from": ["Choose a week within a year of today."]}])
    mine = classes.memberships(user)
    loads, rows = _scored([m.class_id for m in mine], week_start(start), weeks)
    flags = events_service.my_flags(user, [row.id for row in rows.values()])

    university, campus = profile.place_of(user)
    uni = catalogue.packs().get(university) if university else None
    entries = _calendar(uni, campus)
    urls = {s.id: s.url for s in uni.sources} if uni else {}

    out = []
    for wl in loads:
        last = wl.week_start + timedelta(days=6)
        out.append({
            "week_start": wl.week_start.isoformat(),
            "week_end": last.isoformat(),
            "this_week": wl.week_start <= today <= last,
            "load": LOAD_LABELS[wl.colour],
            "colour": wl.colour,
            "score": wl.score,
            "reason": wl.reason,
            "events": [events_service.brief(rows[id(ev)], flags.get(rows[id(ev)].id)) for ev in wl.events],
            "calendar": [_entry(e, urls) for e in entries if e.start <= last and e.last_day >= wl.week_start],
        })
    notes = []
    if not mine:
        notes.append(NO_CLASSES)
    if uni is None:
        notes.append(NO_UNIVERSITY)
    return {
        "today": today.isoformat(),
        "weeks": out,
        "classes": len(mine),
        "university": {"id": uni.university, "name": uni.name, **catalogue.confirmation(uni)} if uni else None,
        "notes": notes,
    }


def _calendar(uni: University | None, campus: str | None) -> list[CalendarEntry]:
    """The university's calendar for the student's campus (an entry with no campuses is for all)."""
    if uni is None:
        return []
    return sorted((e for e in uni.calendar if not e.campuses or campus in e.campuses), key=lambda e: (e.start, e.name))


def _entry(e: CalendarEntry, urls: dict[str, str]) -> dict:
    return {
        "period": e.period,
        "name": e.name,
        "start": e.start.isoformat(),
        "end": e.end.isoformat() if e.end else None,
        "who": e.who,
        "note": e.note,
        "source_url": urls.get(e.source),
    }
