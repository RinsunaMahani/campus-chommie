"""
Job service: the demo accounts are re-based once a day from 02:00 SAST, so
judges always see current dates. The scheduler only runs jobs every so many
seconds, so this runs hourly and acts on the first run from 02:00 that finds
them not yet re-based today. No arguments, returns a JobResult, doesn't know
it's scheduled.
"""
from __future__ import annotations

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from src.extensions import db
from src.shared.scheduling.scheduling_types import JobResult

from ..constants import REBASE_HOUR, TIMEZONE
from ..services import demo_service

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(ZoneInfo(TIMEZONE))


def run() -> JobResult:
    now = _now()
    if now.hour < REBASE_HOUR:
        return JobResult(success=True, count=0, detail=f"before {REBASE_HOUR:02d}:00 SAST")
    try:
        if not demo_service.due(now.date()):
            return JobResult(success=True, count=0, detail="no demo accounts, or already re-based today")
        n = demo_service.rebase(now.date())
    except Exception:  # noqa: BLE001
        db.session.rollback()
        logger.exception("demo: re-basing the demo accounts failed")
        return JobResult(success=False, count=0, detail="re-basing the demo accounts failed")
    return JobResult(success=True, count=n, detail=f"{n} demo accounts re-based on {now.date().isoformat()}")
