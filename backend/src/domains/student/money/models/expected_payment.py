"""
ExpectedPayment -- one expected arrival of an income source. `scheduled_on`
is the occurrence it stands for (unique per source, so making the upcoming
list again never doubles it); `expected_on` is when the student now expects
it, which they can move; `received_on` is set by their "received?" tap.
"""
from __future__ import annotations

from sqlalchemy.dialects.postgresql import UUID

from src.core.base_model import BaseModel
from src.extensions import db

from .income_source import IncomeSource


class ExpectedPayment(BaseModel):
    __tablename__ = "expected_payments"
    __table_args__ = (
        db.UniqueConstraint("income_source_id", "scheduled_on", name="uq_expected_payments_source_day"),
        db.CheckConstraint("amount_cents > 0", name="ck_expected_payments_amount"),
        db.Index("ix_expected_payments_user_expected", "user_id", "expected_on"),
        {"schema": "student"},
    )

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("identity.users.id", ondelete="CASCADE"), nullable=False)
    income_source_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("student.income_sources.id", ondelete="CASCADE"), nullable=False
    )
    scheduled_on = db.Column(db.Date, nullable=False)
    expected_on = db.Column(db.Date, nullable=False)
    amount_cents = db.Column(db.BigInteger, nullable=False)
    received_on = db.Column(db.Date, nullable=True)

    source = db.relationship(IncomeSource, lazy="joined")
