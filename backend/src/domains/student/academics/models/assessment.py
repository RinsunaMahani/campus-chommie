"""
Assessment -- one test, assignment or exam in a module: its share of the
final mark (weight, in %) and, once written, the student's mark (in %).
"""
from __future__ import annotations

from sqlalchemy.dialects.postgresql import UUID

from src.core.base_model import BaseModel
from src.extensions import db

from ..constants import NAME_MAX
from .module import Module


class Assessment(BaseModel):
    __tablename__ = "assessments"
    __table_args__ = (
        db.CheckConstraint("weight > 0 AND weight <= 100", name="ck_assessments_weight"),
        db.CheckConstraint("mark IS NULL OR (mark >= 0 AND mark <= 100)", name="ck_assessments_mark"),
        db.Index("ix_assessments_module", "module_id"),
        {"schema": "student"},
    )

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("identity.users.id", ondelete="CASCADE"), nullable=False)
    module_id = db.Column(UUID(as_uuid=True), db.ForeignKey("student.modules.id", ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(NAME_MAX), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    mark = db.Column(db.Float, nullable=True)  # None until it's written

    # passive_deletes: deleting a module leaves its assessments to the database's ON DELETE CASCADE, rather than
    # SQLAlchemy blanking their module_id (NOT NULL, so that was a 500).
    module = db.relationship(
        Module,
        backref=db.backref("assessments", order_by="Assessment.created_at", lazy="selectin", cascade="all, delete-orphan", passive_deletes=True),
    )
