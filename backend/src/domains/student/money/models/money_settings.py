"""
MoneySettings -- one row per student: the balance they last entered (and
the day it was true), what they spend on essentials each day, and the
reserve they keep for their life fund. All integer cents.
"""
from __future__ import annotations

from sqlalchemy.dialects.postgresql import UUID

from src.core.base_model import BaseModel
from src.extensions import db


class MoneySettings(BaseModel):
    __tablename__ = "money_settings"
    __table_args__ = (
        db.CheckConstraint("balance_cents >= 0", name="ck_money_settings_balance"),
        db.CheckConstraint("essentials_per_day_cents >= 0", name="ck_money_settings_essentials"),
        db.CheckConstraint("life_fund_reserve_cents >= 0", name="ck_money_settings_reserve"),
        {"schema": "student"},
    )

    user_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("identity.users.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    balance_cents = db.Column(db.BigInteger, nullable=False)
    balance_on = db.Column(db.Date, nullable=False)
    essentials_per_day_cents = db.Column(db.BigInteger, nullable=False)
    life_fund_reserve_cents = db.Column(db.BigInteger, nullable=False, default=0)
