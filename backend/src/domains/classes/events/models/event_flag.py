"""
EventFlag -- a student saying a verified event looks wrong, with one reason
from a fixed list (no free text). One per student per event. Reps see how
many flags and which reasons, never who; kept for 12 months.
"""
from __future__ import annotations

from sqlalchemy.dialects.postgresql import UUID

from src.core.base_model import BaseModel
from src.extensions import db


class EventFlag(BaseModel):
    __tablename__ = "event_flags"
    __table_args__ = (
        db.UniqueConstraint("event_id", "user_id", name="uq_event_flags_event_user"),
        db.CheckConstraint(
            "reason IN ('wrong_date', 'wrong_time', 'wrong_venue', 'not_happening', 'duplicate', 'other')",
            name="ck_event_flags_reason",
        ),
        db.Index("ix_event_flags_user", "user_id"),
        {"schema": "classes"},
    )

    event_id = db.Column(UUID(as_uuid=True), db.ForeignKey("classes.class_events.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("identity.users.id", ondelete="CASCADE"), nullable=False)
    reason = db.Column(db.String(16), nullable=False)
