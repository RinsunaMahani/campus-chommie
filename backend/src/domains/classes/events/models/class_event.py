"""
ClassEvent -- a test, quiz, practical, assignment or exam a class rep has
confirmed: a verified event. `version` goes up with every confirmed change;
the changes themselves are EventChange rows. The module is always the
class's own.
"""
from __future__ import annotations

from sqlalchemy.dialects.postgresql import UUID

from src.core.base_model import BaseModel
from src.extensions import db

from ..constants import MODULE_MAX, TITLE_MAX, VENUE_MAX


class ClassEvent(BaseModel):
    __tablename__ = "class_events"
    __table_args__ = (
        db.CheckConstraint(
            "kind IN ('quiz', 'assignment', 'practical', 'test', 'exam')", name="ck_class_events_kind"
        ),
        db.CheckConstraint("weighting IS NULL OR (weighting > 0 AND weighting <= 100)", name="ck_class_events_weighting"),
        db.CheckConstraint("version >= 1", name="ck_class_events_version"),
        db.Index("ix_class_events_class_on", "class_id", "on_date"),
        {"schema": "classes"},
    )

    class_id = db.Column(UUID(as_uuid=True), db.ForeignKey("classes.classes.id", ondelete="CASCADE"), nullable=False)
    kind = db.Column(db.String(12), nullable=False)
    title = db.Column(db.String(TITLE_MAX), nullable=False)
    module = db.Column(db.String(MODULE_MAX), nullable=False)
    on_date = db.Column(db.Date, nullable=False)
    at_time = db.Column(db.Time, nullable=True)  # None: no time given (a due date)
    venue = db.Column(db.String(VENUE_MAX), nullable=True)
    weighting = db.Column(db.Float, nullable=True)  # share of the module mark, in %
    verified_by = db.Column(UUID(as_uuid=True), db.ForeignKey("identity.users.id", ondelete="SET NULL"), nullable=True)
    source_announcement_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("classes.announcements.id", ondelete="SET NULL"), nullable=True
    )
    cancelled = db.Column(db.Boolean, nullable=False, default=False)
    version = db.Column(db.Integer, nullable=False, default=1)
