"""
All database access for class events. Queries take the class ids the
signed-in student belongs to (from the classes service), so a candidate or
event in someone else's class is simply not found (IDOR rule).
"""
from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import date, datetime

from sqlalchemy import func

from src.extensions import db

from ..models import Announcement, ClassEvent, EventCandidate, EventChange, EventFlag

# ------------------------------------------------------------ candidates


def candidate(candidate_id: uuid.UUID, class_ids: list[uuid.UUID]) -> EventCandidate | None:
    if not class_ids:
        return None
    return EventCandidate.query.filter(EventCandidate.id == candidate_id, EventCandidate.class_id.in_(class_ids)).first()


def pending_candidates(class_id: uuid.UUID, submitted_by: uuid.UUID | None = None) -> list[EventCandidate]:
    """The class's candidates waiting for a rep, oldest first; only one student's with `submitted_by`."""
    q = EventCandidate.query.join(Announcement, Announcement.id == EventCandidate.announcement_id).filter(
        EventCandidate.class_id == class_id
    )
    if submitted_by is not None:
        q = q.filter(Announcement.submitted_by == submitted_by)
    return q.order_by(EventCandidate.created_at).all()


def count_pending(class_id: uuid.UUID, user_id: uuid.UUID) -> int:
    return (
        db.session.query(func.count(Announcement.id))
        .filter(Announcement.class_id == class_id, Announcement.submitted_by == user_id, Announcement.status == "pending")
        .scalar()
    )


# ---------------------------------------------------------------- events


def event(event_id: uuid.UUID, class_ids: list[uuid.UUID]) -> ClassEvent | None:
    if not class_ids:
        return None
    return ClassEvent.query.filter(ClassEvent.id == event_id, ClassEvent.class_id.in_(class_ids)).first()


def events_between(class_ids: list[uuid.UUID], first: date, last: date, *, live_only: bool = False) -> list[ClassEvent]:
    """Events from `first` to `last`, both included, in date and time order."""
    if not class_ids:
        return []
    q = ClassEvent.query.filter(ClassEvent.class_id.in_(class_ids), ClassEvent.on_date.between(first, last))
    if live_only:
        q = q.filter(ClassEvent.cancelled.is_(False))
    return q.order_by(ClassEvent.on_date, ClassEvent.at_time.asc().nullsfirst(), ClassEvent.title).all()


def live_events_since(class_id: uuid.UUID, first: date) -> list[ClassEvent]:
    return (
        ClassEvent.query.filter(
            ClassEvent.class_id == class_id, ClassEvent.cancelled.is_(False), ClassEvent.on_date >= first
        )
        .order_by(ClassEvent.on_date)
        .all()
    )


def changes_for(event_ids: list[uuid.UUID]) -> dict[uuid.UUID, list[EventChange]]:
    out: dict[uuid.UUID, list[EventChange]] = defaultdict(list)
    if event_ids:
        for row in EventChange.query.filter(EventChange.event_id.in_(event_ids)).order_by(EventChange.created_at):
            out[row.event_id].append(row)
    return out


# ----------------------------------------------------------------- flags


def flag(event_id: uuid.UUID, user_id: uuid.UUID) -> EventFlag | None:
    return EventFlag.query.filter_by(event_id=event_id, user_id=user_id).first()


def my_flags(user_id: uuid.UUID, event_ids: list[uuid.UUID]) -> dict[uuid.UUID, str]:
    if not event_ids:
        return {}
    rows = EventFlag.query.filter(EventFlag.user_id == user_id, EventFlag.event_id.in_(event_ids))
    return {row.event_id: row.reason for row in rows}


def flag_counts(event_ids: list[uuid.UUID]) -> dict[uuid.UUID, dict[str, int]]:
    """How many flags each event has, by reason: numbers only, never who."""
    out: dict[uuid.UUID, dict[str, int]] = defaultdict(dict)
    if event_ids:
        rows = (
            db.session.query(EventFlag.event_id, EventFlag.reason, func.count(EventFlag.id))
            .filter(EventFlag.event_id.in_(event_ids))
            .group_by(EventFlag.event_id, EventFlag.reason)
        )
        for event_id, reason, n in rows:
            out[event_id][reason] = n
    return out


# ------------------------------------------------------------- retention


def forget_text_decided_before(cutoff: datetime) -> int:
    """The text of announcements a rep decided on before `cutoff`."""
    return (
        Announcement.query.filter(
            Announcement.status != "pending", Announcement.decided_at < cutoff, Announcement.raw_text.isnot(None)
        ).update({Announcement.raw_text: None}, synchronize_session=False)
    )


def delete_pending_before(cutoff: datetime) -> int:
    """Announcements still waiting for a rep since before `cutoff` (their candidates go with them)."""
    return Announcement.query.filter(
        Announcement.status == "pending", Announcement.created_at < cutoff
    ).delete(synchronize_session=False)


def delete_flags_before(cutoff: datetime) -> int:
    return EventFlag.query.filter(EventFlag.updated_at < cutoff).delete(synchronize_session=False)


def add(row) -> None:
    db.session.add(row)


def delete(row) -> None:
    db.session.delete(row)


def erase_all(user_id: uuid.UUID) -> None:
    """A student's announcements (their candidates go with them) and flags."""
    Announcement.query.filter_by(submitted_by=user_id).delete(synchronize_session=False)
    EventFlag.query.filter_by(user_id=user_id).delete(synchronize_session=False)
