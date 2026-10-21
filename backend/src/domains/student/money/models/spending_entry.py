"""
SpendingEntry -- one quick number per day: what the student spent that day.
Kept for a rolling year, then deleted by the scheduler.
"""
from __future__ import annotations

from sqlalchemy.dialects.postgresql import UUID

from src.core.base_model import BaseModel
from src.extensions import db


class SpendingEntry(BaseModel):
    __tablename__ = "spending_entries"
    __table_args__ = (
        db.UniqueConstraint("user_id", "spent_on", name="uq_spending_entries_user_day"),
        db.CheckConstraint("amount_cents >= 0", name="ck_spending_entries_amount"),
        {"schema": "student"},
    )

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("identity.users.id", ondelete="CASCADE"), nullable=False)
    spent_on = db.Column(db.Date, nullable=False)
    amount_cents = db.Column(db.BigInteger, nullable=False)
