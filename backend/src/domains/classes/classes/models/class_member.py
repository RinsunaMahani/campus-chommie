"""
ClassMember -- a student in a class, as a student or a rep. One row per
student per class; it goes when they leave, delete their account, or the
class itself is deleted.
"""
from __future__ import annotations

from sqlalchemy.dialects.postgresql import UUID

from src.core.base_model import BaseModel
from src.extensions import db

from .module_class import ModuleClass


class ClassMember(BaseModel):
    __tablename__ = "class_members"
    __table_args__ = (
        db.UniqueConstraint("class_id", "user_id", name="uq_class_members_class_user"),
        db.CheckConstraint("role IN ('student', 'rep')", name="ck_class_members_role"),
        db.Index("ix_class_members_user", "user_id"),
        {"schema": "classes"},
    )

    class_id = db.Column(UUID(as_uuid=True), db.ForeignKey("classes.classes.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("identity.users.id", ondelete="CASCADE"), nullable=False)
    role = db.Column(db.String(10), nullable=False)

    module_class = db.relationship(ModuleClass, lazy="joined")
