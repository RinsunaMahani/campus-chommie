"""
Job service: OWASP A09 (security logging and alerting failures). The audit trail records every failed sign-in,
code and signature check, but a record nobody reads alerts nobody. Hourly, this counts the last hour's failures and,
when they look like an attack (a password-guessing script, someone working through codes), logs one WARNING line
the host's log alerts can match: "security_alert ...". Counts only, never an email, address or id, so the log stays
free of personal data. No arguments, returns a JobResult, doesn't know it's scheduled.
"""
from __future__ import annotations

import logging
from datetime import timedelta

from src.core.base_model import utcnow
from src.shared.scheduling.scheduling_types import JobResult

from ..constants import WATCH_ALL_KINDS, WATCH_EVERY_SECONDS, WATCH_ONE_KIND
from ..repositories import audit_repository

logger = logging.getLogger("campus_chommie.security")


def run() -> JobResult:
    now = utcnow()
    by_kind, sources = audit_repository.failures_between(now - timedelta(seconds=WATCH_EVERY_SECONDS), now)
    total = sum(by_kind.values())
    loud = {kind: n for kind, n in by_kind.items() if n >= WATCH_ONE_KIND}
    if not loud and total < WATCH_ALL_KINDS:
        return JobResult(success=True, count=0, detail=f"{total} failed events in the last hour: nothing unusual")
    top = ", ".join(f"{kind}={n}" for kind, n in sorted(by_kind.items(), key=lambda kv: -kv[1])[:5])
    logger.warning("security_alert window_minutes=%d failures=%d sources=%d top=%s",
                   WATCH_EVERY_SECONDS // 60, total, sources, top)
    return JobResult(success=True, count=1, detail=f"alert: {total} failed events from {sources} addresses")
