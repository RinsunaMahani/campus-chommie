"""
NotificationSwitch -- a student's own choice to switch a topic of alerts off
(or back on). No row means on: only a change is stored. Security alerts have
no topic and can't be switched off.
"""
from __future__ import annotations

from sqlalchemy.dialects.postgresql import UUID

from src.core.base_model import BaseModel
from src.extensions import db

from ..templates import TOPICS


class NotificationSwitch(BaseModel):
    __tablename__ = "notification_switches"
    __table_args__ = (
        db.UniqueConstraint("user_id", "topic", name="uq_notification_switches_user_topic"),
        db.CheckConstraint(
            "topic IN (" + ", ".join(f"'{t}'" for t in sorted(TOPICS)) + ")", name="ck_notification_switches_topic"
        ),
        {"schema": "platform"},
    )

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("identity.users.id", ondelete="CASCADE"), nullable=False)
    topic = db.Column(db.String(30), nullable=False)
    enabled = db.Column(db.Boolean, nullable=False)
