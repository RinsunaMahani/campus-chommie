"""
Job service: spending logged more than a year ago is deleted (the brief keeps
spending for a rolling 12 months). No arguments, returns a JobResult,
doesn't know it's scheduled.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from src.extensions import db
from src.shared.scheduling.scheduling_types import JobResult

from ..constants import SPENDING_RETENTION_DAYS, TIMEZONE
from ..repositories import money_repository as repo

logger = logging.getLogger(__name__)


def run() -> JobResult:
    try:
        today = datetime.now(ZoneInfo(TIMEZONE)).date()
        n = repo.delete_spending_before(today - timedelta(days=SPENDING_RETENTION_DAYS))
        db.session.commit()
    except Exception:  # noqa: BLE001
        db.session.rollback()
        logger.exception("money: forgetting old spending failed")
        return JobResult(success=False, count=0, detail="forgetting old spending failed")
    return JobResult(success=True, count=n, detail=f"{n} spending entries older than {SPENDING_RETENTION_DAYS} days deleted")
