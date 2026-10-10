"""
Module -- one module a student takes, with the final mark they're aiming for.
The code is unique per student.
"""
from __future__ import annotations

from sqlalchemy.dialects.postgresql import UUID

from src.core.base_model import BaseModel
from src.extensions import db

from ..constants import CODE_MAX, NAME_MAX


class Module(BaseModel):
    __tablename__ = "modules"
    __table_args__ = (
        db.UniqueConstraint("user_id", "code", name="uq_modules_user_code"),
        db.CheckConstraint("target >= 0 AND target <= 100", name="ck_modules_target"),
        {"schema": "student"},
    )

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("identity.users.id", ondelete="CASCADE"), nullable=False)
    code = db.Column(db.String(CODE_MAX), nullable=False)
    name = db.Column(db.String(NAME_MAX), nullable=True)
    target = db.Column(db.Float, nullable=False)
