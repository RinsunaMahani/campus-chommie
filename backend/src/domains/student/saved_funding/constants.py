"""Saved funding's limits."""
from __future__ import annotations

#: Per student.
READ_LIMIT = "120 per minute"
CHANGE_LIMIT = "60 per minute"

#: More than the funding pack holds today, so the cap only stops abuse.
MAX_SAVED = 50

#: "Today" is the student's day, and every student is in South Africa.
TIMEZONE = "Africa/Johannesburg"
