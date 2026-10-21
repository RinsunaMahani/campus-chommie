"""
A student's own activities in their week (groceries, the gym, a shift, seeing friends), and "Find a time": free
stretches around their classes, exams and other plans (campus_engine.timetable.find_time).

  mine(user)                        weekly ones and one-offs from a month back, each flagged if it clashes
  add / change / remove             at most MAX_ACTIVITIES; another student's is a 404
  find_time(user, minutes, ...)     the earliest free stretches over the next days
  export_for / erase_all_for        POPIA's export, and the demo's daily reset

Every call acts on the signed-in student only.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from campus_engine import timetable as engine
from campus_engine.config import load_config
from campus_engine.text import long_day
from src.core.exceptions import NotFoundError, ValidationError
from src.domains.classes.events.services import week_service
from src.extensions import db

from ..constants import ACTIVITY_DAYS_AHEAD, ACTIVITY_DAYS_BACK, MAX_ACTIVITIES
from ..models import Activity
from ..repositories import activity_repository as repo
from ..repositories import exam_repository as exams
from ..repositories import timetable_repository as classes

TIMEZONE = "Africa/Johannesburg"


def _now() -> datetime:
    return datetime.now(ZoneInfo(TIMEZONE))


def _today() -> date:
    return _now().date()


def _overlap(a0: time, a1: time, b0: time, b1: time) -> bool:
    return a0 < b1 and b0 < a1


def _weekday_of(row: Activity) -> int:
    return row.weekday if row.weekday is not None else row.on_date.weekday()


def _clashing(user_id: uuid.UUID, rows: list[Activity]) -> set[str]:
    """Activities that overlap a class on the same weekday, or another activity on the same day."""
    week = classes.for_user(user_id)
    out: set[str] = set()
    for i, a in enumerate(rows):
        day = _weekday_of(a)
        if any(c.weekday == day and _overlap(a.starts_at, a.ends_at, c.starts_at, c.ends_at) for c in week):
            out.add(str(a.id))
        for b in rows[i + 1:]:
            same_day = (a.on_date == b.on_date) if (a.on_date and b.on_date) else _weekday_of(b) == day
            if same_day and _overlap(a.starts_at, a.ends_at, b.starts_at, b.ends_at):
                out |= {str(a.id), str(b.id)}
    return out


def _activity(row: Activity, clashing: set[str]) -> dict:
    return {
        "id": str(row.id),
        "title": row.title,
        "kind": row.kind,
        "weekday": row.weekday,
        "on": row.on_date.isoformat() if row.on_date else None,
        "day": engine.DAYS[row.weekday] if row.weekday is not None else long_day(row.on_date),
        "starts": engine.hhmm(row.starts_at),
        "ends": engine.hhmm(row.ends_at),
        "place": row.place,
        "clashes": str(row.id) in clashing,
    }


def mine(user) -> dict:
    rows = repo.for_user(user.id, _today() - timedelta(days=ACTIVITY_DAYS_BACK))
    clashing = _clashing(user.id, rows)
    weekly = sum(1 for r in rows if r.weekday is not None)
    if rows:
        lines = [f"{weekly} every week, {len(rows) - weekly} one-off."]
    else:
        lines = ["Nothing of your own yet: add groceries, the gym, a shift or time with friends."]
    if clashing:
        lines.append("Some of your plans clash with a class or another plan: they're marked.")
    return {"activities": [_activity(r, clashing) for r in rows], "lines": lines}


def _row(user, activity_id: str) -> Activity:
    try:
        key = uuid.UUID(activity_id)
    except ValueError:
        key = None
    row = repo.one(user.id, key) if key else None
    if row is None:
        raise NotFoundError("That plan isn't one of yours.", code="ACTIVITY_NOT_FOUND")
    return row


def _clean(fields: dict) -> dict:
    out = dict(fields)
    for key in ("title", "place"):
        if out.get(key) is not None:
            out[key] = " ".join(out[key].split()) or None
    if "on" in out:
        out["on_date"] = out.pop("on")
    if "starts" in out:
        out["starts_at"] = out.pop("starts")
    if "ends" in out:
        out["ends_at"] = out.pop("ends")
    return out


def _check_date(on: date | None) -> None:
    today = _today()
    if on is not None and not today - timedelta(days=ACTIVITY_DAYS_BACK) <= on <= today + timedelta(days=ACTIVITY_DAYS_AHEAD):
        raise ValidationError("Please check the highlighted fields.", errors=[{"on": ["Choose a date within the next year."]}])


def add(user, fields: dict) -> dict:
    _check_date(fields.get("on"))
    if repo.count(user.id) >= MAX_ACTIVITIES:
        raise ValidationError("Please check the highlighted fields.",
                              errors=[{"activities": [f"You can keep up to {MAX_ACTIVITIES} plans."]}])
    row = repo.add(user.id, _clean(fields))
    db.session.commit()
    return {"activity": _activity(row, set()), **mine(user)}


def change(user, activity_id: str, fields: dict) -> dict:
    row = _row(user, activity_id)
    _check_date(fields.get("on"))
    for key, value in _clean(fields).items():
        setattr(row, key, value)
    problem = None
    if (row.weekday is None) == (row.on_date is None):
        problem = {"weekday": ["Choose a day of the week, or one date: not both."]}
    elif row.ends_at <= row.starts_at:
        problem = {"ends": ["It must end after it starts."]}
    if problem:
        db.session.rollback()
        raise ValidationError("Please check the highlighted fields.", errors=[problem])
    db.session.commit()
    return {"activity": _activity(row, set()), **mine(user)}


def remove(user, activity_id: str) -> dict:
    repo.delete(_row(user, activity_id))
    db.session.commit()
    return mine(user)


def find_time(user, minutes: int, start: date | None, days: int) -> dict:
    """Free stretches of `minutes` over `days` days from `start` (today by default), around the student's classes,
    their classes' tests, exams and plans. Times already past today are skipped."""
    now = _now()
    first = start or now.date()
    span = [first + timedelta(days=i) for i in range(days)]
    week = classes.for_user(user.id)
    plans = repo.for_user(user.id, first)
    papers = exams.for_user(user.id)
    # Tests and quizzes from the student's classes (the classes feature's own service). Their length isn't known,
    # so each blocks an hour; deadlines without a time block nothing.
    tests: dict[date, list[time]] = {}
    for wk in week_service.week(user, 3, first)["weeks"]:
        for e in wk["events"]:
            if e.get("at") and not e.get("cancelled"):
                tests.setdefault(date.fromisoformat(e["on"]), []).append(time.fromisoformat(e["at"]))
    busy: dict[date, list[engine.Busy]] = {}
    for d in span:
        items = [engine.Busy(c.starts_at, c.ends_at) for c in week if c.weekday == d.weekday()]
        items += [engine.Busy(a.starts_at, a.ends_at) for a in plans
                  if a.on_date == d or (a.weekday is not None and a.weekday == d.weekday())]
        for e in papers:
            if e.exam_on == d:
                end = min(24 * 60 - 1, e.starts_at.hour * 60 + e.starts_at.minute + (e.minutes or 180))
                items.append(engine.Busy(e.starts_at, time(end // 60, end % 60)))
        items += [engine.Busy(t, time(min(23, t.hour + 1), t.minute if t.hour < 23 else 59))
                  for t in tests.get(d, [])]
        busy[d] = items
    slots = engine.find_time(busy, span, minutes, load_config()["timetable"], (now.date(), now.hour * 60 + now.minute))
    return {
        "minutes": minutes,
        "slots": [{"on": s.on.isoformat(), "weekday": s.on.weekday(), "day": long_day(s.on),
                   "starts": engine.hhmm(s.starts), "ends": engine.hhmm(s.ends)} for s in slots],
        "lines": engine.find_time_lines(slots, minutes),
    }


def export_for(user) -> list[dict]:
    """POPIA export: every activity the student added."""
    return [{k: v for k, v in _activity(r, set()).items() if k not in ("id", "clashes")} for r in repo.every_one(user.id)]


def erase_all_for(user) -> None:
    repo.erase_all(user.id)
    db.session.commit()
