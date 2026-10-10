"""
IncomeSource -- money a student expects: an allowance, a family transfer, a
wage. Either monthly on a day of the month, or once on a date. The amount and
how reliable it is are the student's own entries.
"""
from __future__ import annotations

from sqlalchemy.dialects.postgresql import UUID

from src.core.base_model import BaseModel
from src.extensions import db

from ..constants import LABEL_MAX, RELIABILITY


class IncomeSource(BaseModel):
    __tablename__ = "income_sources"
    __table_args__ = (
        db.CheckConstraint("amount_cents > 0", name="ck_income_sources_amount"),
        db.CheckConstraint("(day_of_month IS NULL) <> (expected_on IS NULL)", name="ck_income_sources_one_schedule"),
        db.CheckConstraint("day_of_month IS NULL OR day_of_month BETWEEN 1 AND 31", name="ck_income_sources_day"),
        db.CheckConstraint(
            "reliability IN (" + ", ".join(f"'{r}'" for r in RELIABILITY) + ")", name="ck_income_sources_reliability"
        ),
        db.Index("ix_income_sources_user", "user_id"),
        {"schema": "student"},
    )

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("identity.users.id", ondelete="CASCADE"), nullable=False)
    label = db.Column(db.String(LABEL_MAX), nullable=False)
    amount_cents = db.Column(db.BigInteger, nullable=False)
    day_of_month = db.Column(db.SmallInteger, nullable=True)  # monthly
    expected_on = db.Column(db.Date, nullable=True)  # once
    reliability = db.Column(db.String(20), nullable=False, default="not_sure")
