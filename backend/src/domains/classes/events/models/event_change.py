"""
EventChange -- one field of a verified event changed by a confirmed "moved"
or "cancelled" message: the field, its old and new value (as text), who
confirmed it and when (created_at).
"""
from __future__ import annotations

from sqlalchemy.dialects.postgresql import UUID

from src.core.base_model import BaseModel
from src.extensions import db


class EventChange(BaseModel):
    __tablename__ = "event_changes"
    __table_args__ = (
        db.CheckConstraint("field IN ('on', 'at', 'venue', 'cancelled')", name="ck_event_changes_field"),
        db.Index("ix_event_changes_event", "event_id"),
        {"schema": "classes"},
    )

    event_id = db.Column(UUID(as_uuid=True), db.ForeignKey("classes.class_events.id", ondelete="CASCADE"), nullable=False)
    field = db.Column(db.String(12), nullable=False)
    old = db.Column(db.String(80), nullable=True)
    new = db.Column(db.String(80), nullable=True)
    changed_by = db.Column(UUID(as_uuid=True), db.ForeignKey("identity.users.id", ondelete="SET NULL"), nullable=True)
    announcement_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("classes.announcements.id", ondelete="SET NULL"), nullable=True
    )
