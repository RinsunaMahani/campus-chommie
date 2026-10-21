"""
Classes' scheduled job. Declares only -- the logic lives in jobs/.
Once a day: classes past their academic year and one more go, with expired rep codes.
"""
from __future__ import annotations

from src.master_scheduler.interfaces import JobSpec

from ..jobs import forget_old_classes

JOB_SPECS: list[JobSpec] = [
    JobSpec(name="classes_forget_old_classes", func=forget_old_classes.run, interval_seconds=86_400),
]
