"""
Writes audit rows on a SEPARATE connection from the request's session:
the row survives even if the request's own transaction rolls back, and
inserting it never commits the request's unfinished work.
"""
from __future__ import annotations

import uuid
from typing import Optional

from src.extensions import db

from ..models import AuditEventRecord


def insert(values: dict) -> None:
    table = AuditEventRecord.__table__
    with db.engine.begin() as conn:  # own transaction, committed immediately
        conn.execute(table.insert().values(id=uuid.uuid4(), **values))


def recent(user_id: Optional[uuid.UUID] = None, event_name: Optional[str] = None, limit: int = 100) -> list[AuditEventRecord]:
    q = AuditEventRecord.query
    if user_id is not None:
        q = q.filter_by(user_id=user_id)
    if event_name is not None:
        q = q.filter_by(event_name=event_name)
    return q.order_by(AuditEventRecord.timestamp.desc()).limit(limit).all()


def failures_between(since, until) -> tuple[dict[str, int], int]:
    """Failed events from `since` up to `until`, counted by name, and how many different addresses sent them.
    Counts only: nothing here names a person or an address."""
    from sqlalchemy import func

    window = (AuditEventRecord.timestamp >= since, AuditEventRecord.timestamp < until, AuditEventRecord.status == "failure")
    rows = (
        db.session.query(AuditEventRecord.event_name, func.count())
        .filter(*window)
        .group_by(AuditEventRecord.event_name)
        .all()
    )
    sources = (
        db.session.query(func.count(func.distinct(AuditEventRecord.ip_address)))
        .filter(*window)
        .scalar()
    )
    return {name: n for name, n in rows}, int(sources or 0)
