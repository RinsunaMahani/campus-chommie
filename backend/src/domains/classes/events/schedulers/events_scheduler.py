"""
Class events' scheduled job. Declares only -- the logic lives in jobs/.
Once a day: old announcement text, undecided announcements and old flags go.
"""
from __future__ import annotations

from src.master_scheduler.interfaces import JobSpec

from ..jobs import forget_old_announcements

JOB_SPECS: list[JobSpec] = [
    JobSpec(name="events_forget_old_announcements", func=forget_old_announcements.run, interval_seconds=86_400),
]
