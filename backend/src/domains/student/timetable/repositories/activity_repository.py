"""
All database access for a student's own activities. Only this feature's services call it, and every query takes the
student's user_id: a row that isn't theirs is simply not found (IDOR rule). Deleting is real.
"""
from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import func, or_

from src.extensions import db

from ..models import Activity


def for_user(user_id: uuid.UUID, since: date) -> list[Activity]:
    """Weekly ones, and one-offs from `since` on."""
    return (Activity.query.filter(Activity.user_id == user_id,
                                  or_(Activity.weekday.isnot(None), Activity.on_date >= since))
            .order_by(Activity.on_date.nullsfirst(), Activity.weekday, Activity.starts_at).all())


def every_one(user_id: uuid.UUID) -> list[Activity]:
    return Activity.query.filter_by(user_id=user_id).order_by(Activity.created_at).all()


def one(user_id: uuid.UUID, activity_id: uuid.UUID) -> Activity | None:
    return Activity.query.filter_by(user_id=user_id, id=activity_id).first()


def count(user_id: uuid.UUID) -> int:
    return db.session.query(func.count(Activity.id)).filter(Activity.user_id == user_id).scalar()


def add(user_id: uuid.UUID, fields: dict) -> Activity:
    row = Activity(user_id=user_id, **fields)
    db.session.add(row)
    return row


def delete(row: Activity) -> None:
    db.session.delete(row)


def erase_all(user_id: uuid.UUID) -> int:
    return Activity.query.filter_by(user_id=user_id).delete(synchronize_session=False)
