"""Timetable's limits."""
from __future__ import annotations

#: Per student.
READ_LIMIT = "120 per minute"
CHANGE_LIMIT = "60 per minute"

#: More than any real week holds (about 30 classes), so the cap only stops abuse.
MAX_ENTRIES = 60

KINDS = ("lecture", "tutorial", "practical", "other")

#: Classes run between these times (SAST); anything outside is a typing mistake.
EARLIEST = "06:00"
LATEST = "22:00"
