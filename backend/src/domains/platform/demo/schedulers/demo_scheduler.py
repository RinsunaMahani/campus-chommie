"""
The demo accounts' scheduled job. Declares only -- the logic lives in jobs/.
Hourly; it re-bases the demo accounts once a day, from 02:00 SAST. It also
runs as the scheduler starts, so a server that slept through 02:00 re-bases
as soon as it wakes, not an hour later.
"""
from __future__ import annotations

from src.master_scheduler.interfaces import JobSpec

from ..constants import REBASE_EVERY_SECONDS
from ..jobs import rebase_demo

JOB_SPECS: list[JobSpec] = [
    JobSpec(name="demo_rebase", func=rebase_demo.run, interval_seconds=REBASE_EVERY_SECONDS, run_at_start=True),
]
