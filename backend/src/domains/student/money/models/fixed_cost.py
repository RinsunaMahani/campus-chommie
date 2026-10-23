"""
FixedCost -- recurring fixed costs paid on a set day each month (rent, transport, data, phone).
Counted on their calendar day in runway, safe to spend, and payday planning.
"""
from __future__ import annotations

from sqlalchemy.dialects.postgresql import UUID

from src.core.base_model import BaseModel
from src.extensions import db

from ..constants import FIXED_COST_LABEL_MAX


class FixedCost(BaseModel):
    __tablename__ = "fixed_costs"
    __table_args__ = (
        db.CheckConstraint("amount_cents > 0", name="ck_fixed_costs_amount"),
        db.CheckConstraint("day_of_month BETWEEN 1 AND 31", name="ck_fixed_costs_day"),
        db.Index("ix_fixed_costs_user", "user_id"),
        {"schema": "student"},
    )

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("identity.users.id", ondelete="CASCADE"), nullable=False)
    label = db.Column(db.String(FIXED_COST_LABEL_MAX), nullable=False)
    amount_cents = db.Column(db.BigInteger, nullable=False)
    day_of_month = db.Column(db.SmallInteger, nullable=False)

