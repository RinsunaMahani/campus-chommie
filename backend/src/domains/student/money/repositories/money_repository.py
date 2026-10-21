"""
All database access for My money. Only this feature's services call it, and
every query about someone's money takes their user_id: a row that isn't
theirs is simply not found (IDOR rule).

Deleting is real here: a student's money entries are theirs to remove
(POPIA), so rows go, instead of the soft delete other tables use.
"""
from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import and_, func, or_
from sqlalchemy.dialects.postgresql import insert

from src.extensions import db

from ..models import ExpectedPayment, IncomeSource, MoneySettings, SpendingEntry

# ------------------------------------------------------------------ settings


def settings_for(user_id: uuid.UUID) -> MoneySettings | None:
    return MoneySettings.query.filter_by(user_id=user_id).first()


def save_settings(user_id: uuid.UUID, values: dict) -> MoneySettings:
    row = settings_for(user_id) or MoneySettings(user_id=user_id)
    for key, value in values.items():
        setattr(row, key, value)
    db.session.add(row)
    return row


# ------------------------------------------------------------ income sources


def sources_for(user_id: uuid.UUID) -> list[IncomeSource]:
    return IncomeSource.query.filter_by(user_id=user_id).order_by(IncomeSource.created_at, IncomeSource.id).all()


def source(user_id: uuid.UUID, source_id: uuid.UUID) -> IncomeSource | None:
    return IncomeSource.query.filter_by(id=source_id, user_id=user_id).first()


def count_sources(user_id: uuid.UUID) -> int:
    return db.session.query(func.count(IncomeSource.id)).filter(IncomeSource.user_id == user_id).scalar()


def add(row) -> None:
    db.session.add(row)


def delete(row) -> None:
    db.session.delete(row)


# ---------------------------------------------------------------- payments


def ensure_payments(rows: list[dict]) -> None:
    """Add the expected payments that don't exist yet; one per source and occurrence."""
    if not rows:
        return
    stmt = (
        insert(ExpectedPayment.__table__)
        .values(
            [
                {"id": uuid.uuid4(), "created_at": func.now(), "updated_at": func.now(), "is_deleted": False, **r}
                for r in rows
            ]
        )
        .on_conflict_do_nothing(index_elements=["income_source_id", "scheduled_on"])
    )
    db.session.execute(stmt)


def clear_upcoming(source_id: uuid.UUID, from_day: date) -> None:
    """A source changed: its occurrences from `from_day` that haven't arrived are made again."""
    ExpectedPayment.query.filter(
        ExpectedPayment.income_source_id == source_id,
        ExpectedPayment.scheduled_on >= from_day,
        ExpectedPayment.received_on.is_(None),
    ).delete(synchronize_session=False)


def payments_for(user_id: uuid.UUID, since: date) -> list[ExpectedPayment]:
    """Payments still to come or overdue since `since`, and those received since then."""
    return (
        ExpectedPayment.query.filter(
            ExpectedPayment.user_id == user_id,
            or_(
                and_(ExpectedPayment.received_on.is_(None), ExpectedPayment.expected_on >= since),
                ExpectedPayment.received_on >= since,
            ),
        )
        .order_by(ExpectedPayment.expected_on, ExpectedPayment.id)
        .all()
    )


def payment(user_id: uuid.UUID, payment_id: uuid.UUID) -> ExpectedPayment | None:
    return ExpectedPayment.query.filter_by(id=payment_id, user_id=user_id).first()


def received_between(user_id: uuid.UUID, after: date, until: date) -> int:
    """Cents marked received after `after`, up to and including `until`."""
    return int(
        db.session.query(func.coalesce(func.sum(ExpectedPayment.amount_cents), 0))
        .filter(
            ExpectedPayment.user_id == user_id,
            ExpectedPayment.received_on > after,
            ExpectedPayment.received_on <= until,
        )
        .scalar()
    )


# ---------------------------------------------------------------- spending


def spending_between(user_id: uuid.UUID, after: date, until: date) -> int:
    """Cents logged after `after`, up to and including `until`."""
    return int(
        db.session.query(func.coalesce(func.sum(SpendingEntry.amount_cents), 0))
        .filter(SpendingEntry.user_id == user_id, SpendingEntry.spent_on > after, SpendingEntry.spent_on <= until)
        .scalar()
    )


def spending_since(user_id: uuid.UUID, since: date) -> list[SpendingEntry]:
    return (
        SpendingEntry.query.filter(SpendingEntry.user_id == user_id, SpendingEntry.spent_on >= since)
        .order_by(SpendingEntry.spent_on)
        .all()
    )


def spending_on(user_id: uuid.UUID, day: date) -> SpendingEntry | None:
    return SpendingEntry.query.filter_by(user_id=user_id, spent_on=day).first()


def delete_spending_before(cutoff: date) -> int:
    """Everyone's spending logged before `cutoff` (the scheduler's rolling year)."""
    return SpendingEntry.query.filter(SpendingEntry.spent_on < cutoff).delete(synchronize_session=False)


def erase_all(user_id: uuid.UUID) -> None:
    """Everything the student entered: spending, payments, income sources and settings."""
    SpendingEntry.query.filter_by(user_id=user_id).delete(synchronize_session=False)
    ExpectedPayment.query.filter_by(user_id=user_id).delete(synchronize_session=False)
    IncomeSource.query.filter_by(user_id=user_id).delete(synchronize_session=False)
    MoneySettings.query.filter_by(user_id=user_id).delete(synchronize_session=False)


def all_payments(user_id: uuid.UUID) -> list[ExpectedPayment]:
    return ExpectedPayment.query.filter_by(user_id=user_id).order_by(ExpectedPayment.expected_on).all()


def all_spending(user_id: uuid.UUID) -> list[SpendingEntry]:
    return SpendingEntry.query.filter_by(user_id=user_id).order_by(SpendingEntry.spent_on).all()
