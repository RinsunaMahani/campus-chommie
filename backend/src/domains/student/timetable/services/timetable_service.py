"""
The student's timetable: the classes they entered, read back with what the week adds up to and any
clashes (campus_engine.timetable).

  mine(user)                    every class, Monday first, with the week in words
  add(user, fields)             at most MAX_ENTRIES classes
  change(user, id, fields)      a class that isn't theirs is a 404, the same as one that doesn't exist
  remove(user, id)
  export_for / erase_all_for    POPIA's export, and the demo's daily reset

Every call acts on the signed-in student only.
"""
from __future__ import annotations

import uuid

from campus_engine import timetable as engine
from src.core.exceptions import NotFoundError, ValidationError
from src.extensions import db

from ..constants import MAX_ENTRIES
from ..models import TimetableEntry
from ..repositories import timetable_repository as repo


def _slot(row: TimetableEntry) -> engine.Slot:
    return engine.Slot(str(row.id), row.module, row.kind, row.weekday, row.starts_at, row.ends_at)


def _entry(row: TimetableEntry, clashing: set[str]) -> dict:
    return {
        "id": str(row.id),
        "module": row.module,
        "title": row.title,
        "kind": row.kind,
        "weekday": row.weekday,
        "day": engine.DAYS[row.weekday],
        "starts": engine.hhmm(row.starts_at),
        "ends": engine.hhmm(row.ends_at),
        "venue": row.venue,
        "clashes": str(row.id) in clashing,
    }


def mine(user) -> dict:
    rows = repo.for_user(user.id)
    slots = [_slot(r) for r in rows]
    clashing = {s.id for c in engine.clashes(slots) for s in (c.a, c.b)}
    return {"entries": [_entry(r, clashing) for r in rows], "lines": engine.summary(slots)}


def _row(user, entry_id: str) -> TimetableEntry:
    try:
        key = uuid.UUID(entry_id)
    except ValueError:
        key = None
    row = repo.one(user.id, key) if key else None
    if row is None:
        raise NotFoundError("That class isn't in your timetable.", code="TIMETABLE_ENTRY_NOT_FOUND")
    return row


def _clean(fields: dict) -> dict:
    out = dict(fields)
    if "module" in out:
        out["module"] = " ".join(out["module"].upper().split())
    for key in ("title", "venue"):
        if key in out and out[key] is not None:
            out[key] = " ".join(out[key].split()) or None
    if "starts" in out:
        out["starts_at"] = out.pop("starts")
    if "ends" in out:
        out["ends_at"] = out.pop("ends")
    return out


def add(user, fields: dict) -> dict:
    if repo.count(user.id) >= MAX_ENTRIES:
        raise ValidationError("Please check the highlighted fields.",
                              errors=[{"timetable": [f"You can add up to {MAX_ENTRIES} classes."]}])
    row = repo.add(user.id, _clean(fields))
    db.session.commit()
    return {"entry": _entry(row, set()), **mine(user)}


def change(user, entry_id: str, fields: dict) -> dict:
    row = _row(user, entry_id)
    for key, value in _clean(fields).items():
        setattr(row, key, value)
    if row.ends_at <= row.starts_at:
        db.session.rollback()
        raise ValidationError("Please check the highlighted fields.", errors=[{"ends": ["The class must end after it starts."]}])
    db.session.commit()
    return {"entry": _entry(row, set()), **mine(user)}


def remove(user, entry_id: str) -> dict:
    repo.delete(_row(user, entry_id))
    db.session.commit()
    return mine(user)


def export_for(user) -> dict:
    """POPIA export: every class in the student's timetable."""
    return {"classes": [{k: v for k, v in _entry(r, set()).items() if k not in ("id", "clashes")} for r in repo.for_user(user.id)]}


def erase_all_for(user) -> None:
    """Every class of this student, deleted for real: the demo's daily reset."""
    repo.erase_all(user.id)
    db.session.commit()
