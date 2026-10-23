"""
WeeklyCheckin -- the student's weekly check-in record.
Stores either the week's total spending or a skip record, and which days it filled in for the student (`filled`:
{"YYYY-MM-DD": cents}). A check-in fills only days up to today that the student hadn't logged themselves, with what
the total leaves after their own logs; sending the week again replaces only its own figures, never theirs.
Old check-ins are forgotten alongside daily spending after the rolling retention period.
"""
from __future__ import annotations

from sqlalchemy.dialects.postgresql import JSONB, UUID

from src.core.base_model import BaseModel
from src.extensions import db


class WeeklyCheckin(BaseModel):
    __tablename__ = "weekly_checkins"
    __table_args__ = (
        db.UniqueConstraint("user_id", "week_end", name="uq_weekly_checkins_user_week"),
        db.CheckConstraint(
            "((skipped = TRUE AND amount_cents IS NULL) OR (skipped = FALSE AND amount_cents IS NOT NULL AND amount_cents >= 0))",
            name="ck_weekly_checkins_state",
        ),
        {"schema": "student"},
    )

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("identity.users.id", ondelete="CASCADE"), nullable=False)
    week_end = db.Column(db.Date, nullable=False)
    amount_cents = db.Column(db.BigInteger, nullable=True)
    skipped = db.Column(db.Boolean, nullable=False, default=False)
    filled = db.Column(JSONB, nullable=False, default=dict)

