"""
RepInvite -- a one-time code a rep gives to the next rep. Only its SHA-256
hash is kept (the code is shown once, when it's made); it's deleted when it's
used, and the scheduler deletes it once it has expired.
"""
from __future__ import annotations

from sqlalchemy.dialects.postgresql import UUID

from src.core.base_model import BaseModel
from src.extensions import db

from .module_class import ModuleClass


class RepInvite(BaseModel):
    __tablename__ = "rep_invites"
    __table_args__ = (
        db.UniqueConstraint("code_hash", name="uq_rep_invites_code_hash"),
        db.Index("ix_rep_invites_class", "class_id"),
        {"schema": "classes"},
    )

    class_id = db.Column(UUID(as_uuid=True), db.ForeignKey("classes.classes.id", ondelete="CASCADE"), nullable=False)
    code_hash = db.Column(db.String(64), nullable=False)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)

    module_class = db.relationship(ModuleClass, lazy="joined")
