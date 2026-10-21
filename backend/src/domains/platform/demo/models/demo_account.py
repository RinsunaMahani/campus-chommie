"""
DemoAccount -- which demo account plays which persona, and the day its data
was last re-based. The account itself is identity's (flagged `is_demo`).
"""
from __future__ import annotations

from sqlalchemy.dialects.postgresql import UUID

from src.core.base_model import BaseModel
from src.extensions import db


class DemoAccount(BaseModel):
    __tablename__ = "demo_accounts"
    __table_args__ = (
        db.UniqueConstraint("user_id", name="uq_demo_accounts_user"),
        db.UniqueConstraint("persona", name="uq_demo_accounts_persona"),
        {"schema": "platform"},
    )

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("identity.users.id", ondelete="CASCADE"), nullable=False)
    persona = db.Column(db.String(20), nullable=False)
    rebased_on = db.Column(db.Date, nullable=True)  # None: not built yet
