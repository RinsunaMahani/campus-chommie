"""
My money's scheduled job. Declares only -- the logic lives in jobs/.
Once a day: spending older than a year goes.
"""
from __future__ import annotations

from src.master_scheduler.interfaces import JobSpec

from ..jobs import forget_old_spending

JOB_SPECS: list[JobSpec] = [
    JobSpec(name="money_forget_old_spending", func=forget_old_spending.run, interval_seconds=86_400),
]
