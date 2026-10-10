"""
Job service: what the brief keeps only for a while. An announcement's text
goes 30 days after a rep confirms or discards it; an announcement no rep
decides on goes after 60 days (with its candidate); a flag goes after 12
months. No arguments, returns a JobResult, doesn't know it's scheduled.
"""
from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

from src.extensions import db
from src.shared.scheduling.scheduling_types import JobResult

from ..constants import FLAG_RETENTION_DAYS, PENDING_DAYS, TEXT_RETENTION_DAYS
from ..repositories import events_repository as repo

logger = logging.getLogger(__name__)


def run() -> JobResult:
    try:
        now = datetime.now(UTC)
        texts = repo.forget_text_decided_before(now - timedelta(days=TEXT_RETENTION_DAYS))
        pending = repo.delete_pending_before(now - timedelta(days=PENDING_DAYS))
        flags = repo.delete_flags_before(now - timedelta(days=FLAG_RETENTION_DAYS))
        db.session.commit()
    except Exception:  # noqa: BLE001
        db.session.rollback()
        logger.exception("class events: forgetting old announcements failed")
        return JobResult(success=False, count=0, detail="forgetting old announcements failed")
    return JobResult(
        success=True,
        count=texts + pending + flags,
        detail=f"{texts} announcement texts forgotten, {pending} undecided announcements and {flags} old flags deleted",
    )
