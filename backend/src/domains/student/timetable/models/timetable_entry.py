"""
TimetableEntry -- one class in a student's week: the module, what kind of class, the weekday, when it
starts and ends, and where (optional). Only what the student typed; nothing about them.
"""
from __future__ import annotations

from sqlalchemy.dialects.postgresql import UUID

from src.core.base_model import BaseModel
from src.extensions import db


class TimetableEntry(BaseModel):
    __tablename__ = "timetable_entries"
    __table_args__ = (
        db.CheckConstraint("weekday BETWEEN 0 AND 6", name="ck_timetable_entries_weekday"),
        db.CheckConstraint("ends_at > starts_at", name="ck_timetable_entries_order"),
        db.CheckConstraint("kind IN ('lecture', 'tutorial', 'practical', 'other')", name="ck_timetable_entries_kind"),
        db.Index("ix_timetable_entries_user", "user_id", "weekday", "starts_at"),
        {"schema": "student"},
    )

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("identity.users.id", ondelete="CASCADE"), nullable=False)
    module = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(80), nullable=True)
    kind = db.Column(db.String(12), nullable=False)
    weekday = db.Column(db.SmallInteger, nullable=False)  # 0 = Monday
    starts_at = db.Column(db.Time, nullable=False)
    ends_at = db.Column(db.Time, nullable=False)
    venue = db.Column(db.String(80), nullable=True)
