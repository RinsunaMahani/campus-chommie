"""All database access for the demo accounts' persona map. Only this feature's services call it."""
from __future__ import annotations

import uuid

from src.extensions import db

from ..models import DemoAccount


def all_accounts() -> list[DemoAccount]:
    return DemoAccount.query.order_by(DemoAccount.persona).all()


def ensure(user_id: uuid.UUID, persona: str) -> DemoAccount:
    row = DemoAccount.query.filter_by(persona=persona).first()
    if row is None:
        row = DemoAccount(user_id=user_id, persona=persona)
        db.session.add(row)
    row.user_id = user_id
    return row
