"""
Announcement -- a message a member pasted for their class. Its text may hold
personal data, so it's deleted 30 days after a rep confirms or discards it
(the row stays, so the event's history still points somewhere), and the whole
row goes if no rep decides within 60 days or the student deletes their account.
"""
from __future__ import annotations

from sqlalchemy.dialects.postgresql import UUID

from src.core.base_model import BaseModel
from src.extensions import db


class Announcement(BaseModel):
    __tablename__ = "announcements"
    __table_args__ = (
        db.CheckConstraint("status IN ('pending', 'confirmed', 'discarded')", name="ck_announcements_status"),
        db.Index("ix_announcements_class_status", "class_id", "status"),
        db.Index("ix_announcements_submitted_by", "submitted_by"),
        {"schema": "classes"},
    )

    class_id = db.Column(UUID(as_uuid=True), db.ForeignKey("classes.classes.id", ondelete="CASCADE"), nullable=False)
    submitted_by = db.Column(
        UUID(as_uuid=True), db.ForeignKey("identity.users.id", ondelete="CASCADE"), nullable=False
    )
    raw_text = db.Column(db.Text, nullable=True)  # None once it's been forgotten
    sent_on = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(10), nullable=False, default="pending")
    decided_at = db.Column(db.DateTime(timezone=True), nullable=True)
