"""Timetable's limits."""
from __future__ import annotations

#: Per student.
READ_LIMIT = "120 per minute"
CHANGE_LIMIT = "60 per minute"
#: Reading a PDF is heavier than a click: a few tries a minute is plenty.
IMPORT_LIMIT = "6 per minute;30 per hour"

#: More than any real week holds (about 30 classes), so the cap only stops abuse.
MAX_ENTRIES = 60

#: Exams a student keeps: a year's papers with room to spare.
MAX_EXAMS = 40

#: A timetable PDF longer than this isn't one student's timetable.
MAX_PAGES = 30

KINDS = ("lecture", "tutorial", "practical", "other")

#: Classes run between these times (SAST); anything outside is a typing mistake.
EARLIEST = "06:00"
LATEST = "22:00"
