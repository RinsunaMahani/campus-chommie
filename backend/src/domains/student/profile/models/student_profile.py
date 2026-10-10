"""
StudentProfile -- one row per student: which university and campus they're
at. The university and campus are data-pack ids, checked against the packs
when they're saved.
"""
from __future__ import annotations

from sqlalchemy.dialects.postgresql import UUID

from src.core.base_model import BaseModel
from src.extensions import db


class StudentProfile(BaseModel):
    __tablename__ = "profiles"
    __table_args__ = ({"schema": "student"},)

    user_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("identity.users.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    university = db.Column(db.String(40), nullable=False)
    campus = db.Column(db.String(40), nullable=True)
