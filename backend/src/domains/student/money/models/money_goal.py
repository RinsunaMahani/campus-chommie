"""
MoneyGoal -- something the student is putting money aside for: their own goal ("a laptop"), or a pot for family,
stokvel, an emergency buffer, or a fee date from their university's page ("First tuition instalment due") with the
amount from their own statement. How much is already aside is theirs to update. Only what they typed; nothing about them.
"""
from __future__ import annotations

from sqlalchemy.dialects.postgresql import UUID

from src.core.base_model import BaseModel
from src.extensions import db

from ..constants import GOAL_LABEL_MAX


class MoneyGoal(BaseModel):
    __tablename__ = "money_goals"
    __table_args__ = (
        db.CheckConstraint("amount_cents > 0", name="ck_money_goals_amount"),
        db.CheckConstraint("saved_cents >= 0", name="ck_money_goals_saved"),
        db.CheckConstraint(
            "kind IN ('goal', 'family', 'stokvel', 'buffer', 'big_purchase')",
            name="ck_money_goals_kind",
        ),
        db.CheckConstraint(
            "(kind IN ('goal', 'big_purchase') AND due_on IS NOT NULL) OR "
            "(kind IN ('family', 'stokvel', 'buffer') AND due_on IS NULL)",
            name="ck_money_goals_due_on",
        ),
        db.Index("ix_money_goals_user", "user_id", "due_on"),
        {"schema": "student"},
    )

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("identity.users.id", ondelete="CASCADE"), nullable=False)
    label = db.Column(db.String(GOAL_LABEL_MAX), nullable=False)
    #: goal (default), family, stokvel, buffer, big_purchase
    kind = db.Column(db.String(16), nullable=False, default="goal")
    amount_cents = db.Column(db.BigInteger, nullable=False)
    saved_cents = db.Column(db.BigInteger, nullable=False, default=0)
    due_on = db.Column(db.Date, nullable=True)
    #: True when the date came from the student's university's page (its fee dates); the amount never does.
    from_university = db.Column(db.Boolean, nullable=False, default=False)
    #: A yes/no record for big purchases: paying through a stokvel.
    stokvel_funded = db.Column(db.Boolean, nullable=False, default=False)
