"""
All database access for notifications. Only this feature's services call
this, and every query about someone's alerts takes their user_id: a row
that isn't theirs is simply not found (IDOR rule).
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import func, select, tuple_
from sqlalchemy.dialects.postgresql import insert

from src.extensions import db

from ..models import Notification, NotificationSwitch


def insert_once(values: dict, topic: str | None = None) -> bool:
    """Write one alert in its own transaction, on ONE connection (the
    listener runs on the background queue, after the action's own commit),
    so a job never holds one connection open while it waits on another.
    The same (user_id, dedupe_key) again is ignored, and so is an alert whose
    `topic` the user switched off. True when written."""
    stmt = (
        insert(Notification.__table__)
        .values(id=uuid.uuid4(), created_at=func.now(), updated_at=func.now(), is_deleted=False, **values)
        .on_conflict_do_nothing(index_elements=["user_id", "dedupe_key"])
    )
    with db.engine.begin() as conn:
        if topic is not None:
            switched_off = conn.execute(
                select(NotificationSwitch.id).where(
                    NotificationSwitch.user_id == values["user_id"],
                    NotificationSwitch.topic == topic,
                    NotificationSwitch.enabled.is_(False),
                )
            ).first()
            if switched_off is not None:
                return False
        return conn.execute(stmt).rowcount == 1


def one(user_id: uuid.UUID, notification_id: uuid.UUID) -> Optional[Notification]:
    return Notification.query.filter_by(id=notification_id, user_id=user_id, is_deleted=False).first()


def page(user_id: uuid.UUID, before: Optional[Notification], limit: int) -> list[Notification]:
    """Newest first; `before` is the last row of the previous page."""
    query = Notification.query.filter_by(user_id=user_id, is_deleted=False)
    if before is not None:
        query = query.filter(tuple_(Notification.created_at, Notification.id) < tuple_(before.created_at, before.id))
    return query.order_by(Notification.created_at.desc(), Notification.id.desc()).limit(limit).all()


def unread_count(user_id: uuid.UUID) -> int:
    return (
        db.session.query(func.count(Notification.id))
        .filter(Notification.user_id == user_id, Notification.read_at.is_(None), Notification.is_deleted.is_(False))
        .scalar()
    )


def latest(user_id: uuid.UUID) -> Optional[Notification]:
    return (
        Notification.query.filter_by(user_id=user_id, is_deleted=False)
        .order_by(Notification.created_at.desc(), Notification.id.desc())
        .first()
    )


def mark_all_read(user_id: uuid.UUID, at: datetime) -> int:
    return (
        Notification.query.filter(
            Notification.user_id == user_id, Notification.read_at.is_(None), Notification.is_deleted.is_(False)
        ).update({Notification.read_at: at}, synchronize_session=False)
    )


def delete_before(cutoff: datetime) -> int:
    """Hard delete: old alerts are copies of things kept elsewhere (each
    feature's own records, the audit trail), not a record of their own."""
    return Notification.query.filter(Notification.created_at < cutoff).delete(synchronize_session=False)


def all_for(user_id: uuid.UUID) -> list[Notification]:
    return Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at).all()


def switches_for(user_id: uuid.UUID) -> dict[str, bool]:
    """The topics the student changed, and how: a topic missing here is on."""
    return {s.topic: s.enabled for s in NotificationSwitch.query.filter_by(user_id=user_id)}


def set_switch(user_id: uuid.UUID, topic: str, enabled: bool) -> None:
    row = NotificationSwitch.query.filter_by(user_id=user_id, topic=topic).first()
    if row is None:
        db.session.add(NotificationSwitch(user_id=user_id, topic=topic, enabled=enabled))
    else:
        row.enabled = enabled


def erase_all(user_id: uuid.UUID) -> None:
    Notification.query.filter_by(user_id=user_id).delete(synchronize_session=False)
    NotificationSwitch.query.filter_by(user_id=user_id).delete(synchronize_session=False)
