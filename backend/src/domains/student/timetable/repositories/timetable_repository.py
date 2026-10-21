"""
All database access for the timetable. Only this feature's services call it, and every query takes the
student's user_id: a row that isn't theirs is simply not found (IDOR rule). Deleting is real.
"""
from __future__ import annotations

import uuid

from sqlalchemy import func

from src.extensions import db

from ..models import TimetableEntry


def for_user(user_id: uuid.UUID) -> list[TimetableEntry]:
    return (TimetableEntry.query.filter_by(user_id=user_id)
            .order_by(TimetableEntry.weekday, TimetableEntry.starts_at, TimetableEntry.module).all())


def one(user_id: uuid.UUID, entry_id: uuid.UUID) -> TimetableEntry | None:
    return TimetableEntry.query.filter_by(user_id=user_id, id=entry_id).first()


def count(user_id: uuid.UUID) -> int:
    return db.session.query(func.count(TimetableEntry.id)).filter(TimetableEntry.user_id == user_id).scalar()


def add(user_id: uuid.UUID, fields: dict) -> TimetableEntry:
    row = TimetableEntry(user_id=user_id, **fields)
    db.session.add(row)
    return row


def delete(row: TimetableEntry) -> None:
    db.session.delete(row)


def erase_all(user_id: uuid.UUID) -> int:
    return TimetableEntry.query.filter_by(user_id=user_id).delete(synchronize_session=False)
