"""
Job service: a class is kept for its academic year and one more (the
brief), then deleted with its members, rep codes, announcements and events.
Expired rep codes go too. No arguments, returns a JobResult, doesn't know
it's scheduled.
"""
from __future__ import annotations

import logging
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from src.extensions import db
from src.shared.scheduling.scheduling_types import JobResult

from ..constants import TIMEZONE, YEARS_KEPT_AFTER
from ..repositories import class_repository as repo

logger = logging.getLogger(__name__)


def run() -> JobResult:
    try:
        this_year = datetime.now(ZoneInfo(TIMEZONE)).year
        classes = repo.delete_classes_before(this_year - YEARS_KEPT_AFTER)
        codes = repo.delete_expired_rep_invites(datetime.now(UTC))
        db.session.commit()
    except Exception:  # noqa: BLE001
        db.session.rollback()
        logger.exception("classes: forgetting old classes failed")
        return JobResult(success=False, count=0, detail="forgetting old classes failed")
    return JobResult(
        success=True,
        count=classes + codes,
        detail=f"{classes} classes from before {this_year - YEARS_KEPT_AFTER} and {codes} expired rep codes deleted",
    )
