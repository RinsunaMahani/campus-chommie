"""
The audit trail's scheduled job. Declares only -- the logic lives in jobs/. Hourly.
"""
from __future__ import annotations

from src.master_scheduler.interfaces import JobSpec

from ..constants import WATCH_EVERY_SECONDS
from ..jobs import attack_watch

JOB_SPECS: list[JobSpec] = [
    JobSpec(name="security_attack_watch", func=attack_watch.run, interval_seconds=WATCH_EVERY_SECONDS),
]
