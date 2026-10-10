"""
All database access for classes. A class is reached through the signed-in
student's own membership: `membership(user_id, class_id)` is None both for a
class that doesn't exist and for one they're not in (IDOR rule).
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import func

from src.extensions import db

from ..models import ClassMember, ModuleClass, RepInvite


def membership(user_id: uuid.UUID, class_id: uuid.UUID) -> ClassMember | None:
    return ClassMember.query.filter_by(user_id=user_id, class_id=class_id).first()


def memberships(user_id: uuid.UUID) -> list[ClassMember]:
    return (
        ClassMember.query.filter_by(user_id=user_id)
        .join(ModuleClass, ModuleClass.id == ClassMember.class_id)
        .order_by(ModuleClass.year.desc(), ModuleClass.module_code)
        .all()
    )


def count_memberships(user_id: uuid.UUID) -> int:
    return db.session.query(func.count(ClassMember.id)).filter(ClassMember.user_id == user_id).scalar()


def class_by_invite(code: str) -> ModuleClass | None:
    return ModuleClass.query.filter_by(invite_code=code).first()


def invite_code_taken(code: str) -> bool:
    return db.session.query(ModuleClass.id).filter_by(invite_code=code).first() is not None


def lock_class(class_id: uuid.UUID) -> ModuleClass | None:
    """The class row, locked until commit: rep changes on one class happen one at a time."""
    return ModuleClass.query.filter_by(id=class_id).with_for_update().first()


def counts(class_ids: list[uuid.UUID]) -> dict[uuid.UUID, tuple[int, int]]:
    """(members, reps) per class: numbers only, never who."""
    if not class_ids:
        return {}
    rows = (
        db.session.query(
            ClassMember.class_id,
            func.count(ClassMember.id),
            func.count(ClassMember.id).filter(ClassMember.role == "rep"),
        )
        .filter(ClassMember.class_id.in_(class_ids))
        .group_by(ClassMember.class_id)
        .all()
    )
    return {class_id: (members, reps) for class_id, members, reps in rows}


def count_reps(class_id: uuid.UUID) -> int:
    return (
        db.session.query(func.count(ClassMember.id))
        .filter(ClassMember.class_id == class_id, ClassMember.role == "rep")
        .scalar()
    )


def rep_invite(code_hash: str) -> RepInvite | None:
    return RepInvite.query.filter_by(code_hash=code_hash).first()


def count_open_rep_invites(class_id: uuid.UUID, now: datetime) -> int:
    return (
        db.session.query(func.count(RepInvite.id))
        .filter(RepInvite.class_id == class_id, RepInvite.expires_at > now)
        .scalar()
    )


def delete_expired_rep_invites(now: datetime) -> int:
    return RepInvite.query.filter(RepInvite.expires_at <= now).delete(synchronize_session=False)


def delete_classes_before(year: int) -> int:
    """Classes from academic years before `year`; members, rep codes and events go with them."""
    return ModuleClass.query.filter(ModuleClass.year < year).delete(synchronize_session=False)


def add(row) -> None:
    db.session.add(row)


def delete(row) -> None:
    db.session.delete(row)


def delete_empty(class_ids: list[uuid.UUID]) -> int:
    """Of these classes, delete the ones with no members left."""
    if not class_ids:
        return 0
    occupied = db.session.query(ClassMember.class_id).filter(ClassMember.class_id.in_(class_ids))
    return (
        ModuleClass.query.filter(ModuleClass.id.in_(class_ids), ModuleClass.id.notin_(occupied))
        .delete(synchronize_session=False)
    )
