"""
All database access for saved funding. Only this feature's services call it, and every query
takes the student's user_id: a row that isn't theirs is simply not found (IDOR rule).

Deleting is real: a student's saved list is theirs to remove (POPIA).
"""
from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import func

from src.extensions import db

from ..models import SavedFunder


def for_user(user_id: uuid.UUID) -> list[SavedFunder]:
    return SavedFunder.query.filter_by(user_id=user_id).order_by(SavedFunder.saved_on.desc(), SavedFunder.funder_id).all()


def one(user_id: uuid.UUID, funder_id: str) -> SavedFunder | None:
    return SavedFunder.query.filter_by(user_id=user_id, funder_id=funder_id).first()


def count(user_id: uuid.UUID) -> int:
    return db.session.query(func.count(SavedFunder.id)).filter(SavedFunder.user_id == user_id).scalar()


def add(user_id: uuid.UUID, funder_id: str, saved_on: date) -> SavedFunder:
    row = SavedFunder(user_id=user_id, funder_id=funder_id, saved_on=saved_on)
    db.session.add(row)
    return row


def delete(row: SavedFunder) -> None:
    db.session.delete(row)


def erase_all(user_id: uuid.UUID) -> int:
    return SavedFunder.query.filter_by(user_id=user_id).delete(synchronize_session=False)
