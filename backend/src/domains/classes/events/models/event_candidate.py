"""
EventCandidate -- what the engine read from one announcement, with a
confidence per field, waiting for a rep. Deleted when a rep confirms or
discards it (the brief keeps candidates only until then). For a "moved" or
"cancelled" message, `event_id` is the verified event it most likely changes.
"""
from __future__ import annotations

from sqlalchemy.dialects.postgresql import JSONB, UUID

from src.core.base_model import BaseModel
from src.extensions import db

from ..constants import MODULE_MAX, TITLE_MAX, VENUE_MAX
from .announcement import Announcement
from .class_event import ClassEvent


class EventCandidate(BaseModel):
    __tablename__ = "event_candidates"
    __table_args__ = (
        db.UniqueConstraint("announcement_id", name="uq_event_candidates_announcement"),
        db.CheckConstraint("change IS NULL OR change IN ('moved', 'cancelled')", name="ck_event_candidates_change"),
        db.Index("ix_event_candidates_class", "class_id"),
        {"schema": "classes"},
    )

    announcement_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("classes.announcements.id", ondelete="CASCADE"), nullable=False
    )
    class_id = db.Column(UUID(as_uuid=True), db.ForeignKey("classes.classes.id", ondelete="CASCADE"), nullable=False)
    from_rep = db.Column(db.Boolean, nullable=False)
    kind = db.Column(db.String(12), nullable=True)
    title = db.Column(db.String(TITLE_MAX), nullable=True)
    module = db.Column(db.String(MODULE_MAX), nullable=True)
    on_date = db.Column(db.Date, nullable=True)
    at_time = db.Column(db.Time, nullable=True)
    venue = db.Column(db.String(VENUE_MAX), nullable=True)
    weighting = db.Column(db.Float, nullable=True)
    change = db.Column(db.String(10), nullable=True)
    event_id = db.Column(UUID(as_uuid=True), db.ForeignKey("classes.class_events.id", ondelete="SET NULL"), nullable=True)
    confidence = db.Column(JSONB, nullable=False, default=dict)
    notes = db.Column(JSONB, nullable=False, default=list)

    announcement = db.relationship(Announcement, lazy="joined")
    event = db.relationship(ClassEvent, lazy="joined")
