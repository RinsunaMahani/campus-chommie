"""
All database access for My marks. Only this feature's services call it, and
every query takes the student's own user_id: a row that isn't theirs is
simply not found (IDOR rule). Deletes are real, as for money: marks are the
student's to remove.
"""
from __future__ import annotations

import uuid

from sqlalchemy import func

from src.extensions import db

from ..models import Assessment, Module


def modules_for(user_id: uuid.UUID) -> list[Module]:
    return Module.query.filter_by(user_id=user_id).order_by(Module.code).all()


def module(user_id: uuid.UUID, module_id: uuid.UUID) -> Module | None:
    return Module.query.filter_by(id=module_id, user_id=user_id).first()


def module_by_code(user_id: uuid.UUID, code: str) -> Module | None:
    return Module.query.filter_by(user_id=user_id, code=code).first()


def count_modules(user_id: uuid.UUID) -> int:
    return db.session.query(func.count(Module.id)).filter(Module.user_id == user_id).scalar()


def assessment(user_id: uuid.UUID, module_id: uuid.UUID, assessment_id: uuid.UUID) -> Assessment | None:
    return Assessment.query.filter_by(id=assessment_id, module_id=module_id, user_id=user_id).first()


def add(row) -> None:
    db.session.add(row)


def delete(row) -> None:
    db.session.delete(row)
