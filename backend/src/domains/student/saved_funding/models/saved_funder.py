"""
SavedFunder -- one funder a student saved: the funder's id in the funding pack and the day they
saved it (an alert says when a funder opened after that day). Nothing else about the student.
"""
from __future__ import annotations

from sqlalchemy.dialects.postgresql import UUID

from src.core.base_model import BaseModel
from src.extensions import db


class SavedFunder(BaseModel):
    __tablename__ = "saved_funders"
    __table_args__ = (
        db.UniqueConstraint("user_id", "funder_id", name="uq_saved_funders_user_funder"),
        db.CheckConstraint("funder_id ~ '^[a-z0-9_]{1,40}$'", name="ck_saved_funders_funder_id"),
        {"schema": "student"},
    )

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("identity.users.id", ondelete="CASCADE"), nullable=False)
    funder_id = db.Column(db.String(40), nullable=False)
    saved_on = db.Column(db.Date, nullable=False)
