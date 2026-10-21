"""
ExamEntry -- one exam paper a student keeps: the module, its name and paper as the exam list prints them, the
date, the start time, how long it runs (if the list says) and where (optional). Only what the student chose
from their university's list or typed; nothing about them.
"""
from __future__ import annotations

from sqlalchemy.dialects.postgresql import UUID

from src.core.base_model import BaseModel
from src.extensions import db


class ExamEntry(BaseModel):
    __tablename__ = "exam_entries"
    __table_args__ = (
        db.CheckConstraint("minutes IS NULL OR minutes BETWEEN 1 AND 480", name="ck_exam_entries_minutes"),
        db.Index("ix_exam_entries_user", "user_id", "exam_on", "starts_at"),
        {"schema": "student"},
    )

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("identity.users.id", ondelete="CASCADE"), nullable=False)
    module = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(80), nullable=True)
    paper = db.Column(db.String(80), nullable=True)
    exam_on = db.Column(db.Date, nullable=False)
    starts_at = db.Column(db.Time, nullable=False)
    minutes = db.Column(db.SmallInteger, nullable=True)
    venue = db.Column(db.String(80), nullable=True)
