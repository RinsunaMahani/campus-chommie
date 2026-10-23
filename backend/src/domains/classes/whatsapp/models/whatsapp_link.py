"""
WhatsappLink -- a WhatsApp number linked to an account, kept only as a keyed hash (HMAC-SHA256 with the server's
WHATSAPP_PHONE_KEY). A per-row salt would make the hash impossible to look up when a message arrives; a secret key
gives the same protection against a leaked table, since without the key no number can be tested against it.

WhatsappLinkCode -- the one-time code the app shows; kept as a keyed hash too, one per account, until it is used
or expires.

WhatsappSeen -- the hash of a message id Meta sent, so a retry is answered once. No person in it.
"""
from __future__ import annotations

from sqlalchemy.dialects.postgresql import UUID

from src.core.base_model import BaseModel
from src.extensions import db

_HEX64 = "~ '^[0-9a-f]{64}$'"


class WhatsappLink(BaseModel):
    __tablename__ = "whatsapp_links"
    __table_args__ = (
        db.UniqueConstraint("phone_hash", name="uq_whatsapp_links_phone"),
        db.CheckConstraint(f"phone_hash {_HEX64}", name="ck_whatsapp_links_phone_hash"),
        db.Index("ix_whatsapp_links_user", "user_id"),
        {"schema": "classes"},
    )

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("identity.users.id", ondelete="CASCADE"), nullable=False)
    phone_hash = db.Column(db.String(64), nullable=False)


class WhatsappLinkCode(BaseModel):
    __tablename__ = "whatsapp_link_codes"
    __table_args__ = (
        db.UniqueConstraint("user_id", name="uq_whatsapp_link_codes_user"),
        db.UniqueConstraint("code_hash", name="uq_whatsapp_link_codes_code"),
        db.CheckConstraint(f"code_hash {_HEX64}", name="ck_whatsapp_link_codes_code_hash"),
        {"schema": "classes"},
    )

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("identity.users.id", ondelete="CASCADE"), nullable=False)
    code_hash = db.Column(db.String(64), nullable=False)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)


class WhatsappSeen(BaseModel):
    __tablename__ = "whatsapp_seen"
    __table_args__ = (
        db.UniqueConstraint("message_hash", name="uq_whatsapp_seen_message"),
        db.CheckConstraint(f"message_hash {_HEX64}", name="ck_whatsapp_seen_message_hash"),
        db.Index("ix_whatsapp_seen_created", "created_at"),
        {"schema": "classes"},
    )

    message_hash = db.Column(db.String(64), nullable=False)
