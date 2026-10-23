"""
All database access for the WhatsApp bot. Only this feature's services call it. A link is found by its number's
hash (a message arriving) or by its account (the app's own routes); nothing lists another account's links.
Deleting is real: unlinking removes the row.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import func

from src.extensions import db

from ..models import WhatsappLink, WhatsappLinkCode, WhatsappSeen


def link_for_phone(phone_hash: str) -> WhatsappLink | None:
    return WhatsappLink.query.filter_by(phone_hash=phone_hash).first()


def links_for(user_id: uuid.UUID) -> list[WhatsappLink]:
    return WhatsappLink.query.filter_by(user_id=user_id).order_by(WhatsappLink.created_at).all()


def count_links(user_id: uuid.UUID) -> int:
    return db.session.query(func.count(WhatsappLink.id)).filter(WhatsappLink.user_id == user_id).scalar()


def add_link(user_id: uuid.UUID, phone_hash: str) -> WhatsappLink:
    row = WhatsappLink(user_id=user_id, phone_hash=phone_hash)
    db.session.add(row)
    return row


def delete(row) -> None:
    db.session.delete(row)


def delete_links(user_id: uuid.UUID) -> int:
    return WhatsappLink.query.filter_by(user_id=user_id).delete(synchronize_session=False)


def code_for(user_id: uuid.UUID) -> WhatsappLinkCode | None:
    return WhatsappLinkCode.query.filter_by(user_id=user_id).first()


def code_by_hash(code_hash: str) -> WhatsappLinkCode | None:
    return WhatsappLinkCode.query.filter_by(code_hash=code_hash).first()


def add_code(user_id: uuid.UUID, code_hash: str, expires_at: datetime) -> WhatsappLinkCode:
    row = WhatsappLinkCode(user_id=user_id, code_hash=code_hash, expires_at=expires_at)
    db.session.add(row)
    return row


def delete_codes(user_id: uuid.UUID) -> int:
    return WhatsappLinkCode.query.filter_by(user_id=user_id).delete(synchronize_session=False)


def add_seen(message_hash: str) -> None:
    db.session.add(WhatsappSeen(message_hash=message_hash))


def forget_seen_before(cutoff: datetime) -> int:
    return WhatsappSeen.query.filter(WhatsappSeen.created_at < cutoff).delete(synchronize_session=False)


def forget_codes_before(cutoff: datetime) -> int:
    return WhatsappLinkCode.query.filter(WhatsappLinkCode.expires_at < cutoff).delete(synchronize_session=False)
