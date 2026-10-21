"""
Notification -- one alert for one user, with its read state.

The wording isn't stored: kind (a template key) + params are, and the
text is rendered from templates.py when the list is read, so it can be
improved without touching rows. UNIQUE (user_id, dedupe_key) makes the
same event land once however often the action behind it is retried.
"""
from __future__ import annotations

from sqlalchemy.dialects.postgresql import JSONB, UUID

from src.core.base_model import BaseModel
from src.extensions import db

from ..templates import LINK_TYPES, TEMPLATES


def _one_of(column: str, values, name: str):
    listed = ", ".join(f"'{v}'" for v in values)
    return db.CheckConstraint(f"{column} IN ({listed})", name=name)


class Notification(BaseModel):
    __tablename__ = "notifications"
    __table_args__ = (
        db.UniqueConstraint("user_id", "dedupe_key", name="uq_notifications_user_dedupe"),
        _one_of("kind", sorted(TEMPLATES), "ck_notifications_kind"),
        db.CheckConstraint(
            "link_type IS NULL OR link_type IN (" + ", ".join(f"'{t}'" for t in LINK_TYPES) + ")", name="ck_notifications_link_type"
        ),
        db.Index("ix_notifications_user_created", "user_id", "created_at"),
        {"schema": "platform"},
    )

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("identity.users.id", ondelete="CASCADE"), nullable=False)
    kind = db.Column(db.String(40), nullable=False)
    params = db.Column(JSONB, nullable=False, default=dict)
    link_type = db.Column(db.String(20), nullable=True)
    link_id = db.Column(db.String(64), nullable=True)
    dedupe_key = db.Column(db.String(160), nullable=False)
    read_at = db.Column(db.DateTime(timezone=True), nullable=True)
