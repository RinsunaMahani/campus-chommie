"""
The student's exams: the papers they keep, read back with how many, the next one and any two at the same time
(campus_engine.timetable).

  mine(user)                        every exam, soonest first, with the exams in words
  add(user, fields)                 at most MAX_EXAMS exams
  add_many(user, exams, replace)    exams checked after an import, all or none; replace clears them first
  remove(user, id)                  an exam that isn't theirs is a 404, the same as one that doesn't exist
  export_for / erase_all_for        POPIA's export, and the demo's daily reset

Every call acts on the signed-in student only.
"""
from __future__ import annotations

import uuid

from campus_engine import timetable as engine
from campus_engine.text import long_day
from src.core.exceptions import NotFoundError, ValidationError
from src.extensions import db
from src.shared.clock.clock import today_sast

from ..constants import MAX_EXAMS
from ..models import ExamEntry
from ..repositories import exam_repository as repo


def _exam(row: ExamEntry, clashing: set[str]) -> dict:
    return {
        "id": str(row.id),
        "module": row.module,
        "title": row.title,
        "paper": row.paper,
        "on": row.exam_on.isoformat(),
        "day": long_day(row.exam_on),
        "starts": engine.hhmm(row.starts_at),
        "minutes": row.minutes,
        "venue": row.venue,
        "clashes": str(row.id) in clashing,
    }


def _plain(row: ExamEntry) -> engine.Exam:
    return engine.Exam(str(row.id), row.module, row.exam_on, row.starts_at, row.minutes)


def mine(user) -> dict:
    rows = repo.for_user(user.id)
    exams = [_plain(r) for r in rows]
    clashing = {e.id for pair in engine.exam_clashes(exams) for e in pair}
    return {"exams": [_exam(r, clashing) for r in rows], "lines": engine.exam_summary(exams, today_sast())}


def _clean(fields: dict) -> dict:
    out = dict(fields)
    out["module"] = " ".join(out["module"].upper().split())
    for key in ("title", "paper", "venue"):
        if out.get(key) is not None:
            out[key] = " ".join(out[key].split()) or None
    out["exam_on"] = out.pop("on")
    out["starts_at"] = out.pop("starts")
    return out


def _too_many() -> ValidationError:
    return ValidationError("Please check the highlighted fields.", errors=[{"exams": [f"You can keep up to {MAX_EXAMS} exams."]}])


def add(user, fields: dict) -> dict:
    if repo.count(user.id) >= MAX_EXAMS:
        raise _too_many()
    row = repo.add(user.id, _clean(fields))
    db.session.commit()
    return {"exam": _exam(row, set()), **mine(user)}


def add_many(user, exams: list[dict], replace: bool) -> dict:
    if replace:
        repo.erase_all(user.id)
    if (0 if replace else repo.count(user.id)) + len(exams) > MAX_EXAMS:
        db.session.rollback()
        raise _too_many()
    for fields in exams:
        repo.add(user.id, _clean(fields))
    db.session.commit()
    return mine(user)


def remove(user, exam_id: str) -> dict:
    try:
        key = uuid.UUID(exam_id)
    except ValueError:
        key = None
    row = repo.one(user.id, key) if key else None
    if row is None:
        raise NotFoundError("That exam isn't in your list.", code="EXAM_NOT_FOUND")
    repo.delete(row)
    db.session.commit()
    return mine(user)


def export_for(user) -> list[dict]:
    """POPIA export: every exam the student keeps."""
    return [{k: v for k, v in _exam(r, set()).items() if k not in ("id", "clashes")} for r in repo.for_user(user.id)]


def erase_all_for(user) -> None:
    """Every exam of this student, deleted for real: the demo's daily reset."""
    repo.erase_all(user.id)
    db.session.commit()
