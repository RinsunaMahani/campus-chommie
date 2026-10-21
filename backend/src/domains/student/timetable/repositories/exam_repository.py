"""
All database access for a student's exams. Only this feature's services call it, and every query takes the
student's user_id: a row that isn't theirs is simply not found (IDOR rule). Deleting is real.
"""
from __future__ import annotations

import uuid

from sqlalchemy import func

from src.extensions import db

from ..models import ExamEntry


def for_user(user_id: uuid.UUID) -> list[ExamEntry]:
    return (ExamEntry.query.filter_by(user_id=user_id)
            .order_by(ExamEntry.exam_on, ExamEntry.starts_at, ExamEntry.module).all())


def one(user_id: uuid.UUID, exam_id: uuid.UUID) -> ExamEntry | None:
    return ExamEntry.query.filter_by(user_id=user_id, id=exam_id).first()


def count(user_id: uuid.UUID) -> int:
    return db.session.query(func.count(ExamEntry.id)).filter(ExamEntry.user_id == user_id).scalar()


def add(user_id: uuid.UUID, fields: dict) -> ExamEntry:
    row = ExamEntry(user_id=user_id, **fields)
    db.session.add(row)
    return row


def delete(row: ExamEntry) -> None:
    db.session.delete(row)


def erase_all(user_id: uuid.UUID) -> int:
    return ExamEntry.query.filter_by(user_id=user_id).delete(synchronize_session=False)
