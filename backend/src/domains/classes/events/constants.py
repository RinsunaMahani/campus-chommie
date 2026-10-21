"""Class events' and the week's limits."""
from __future__ import annotations

#: Per student.
READ_LIMIT = "120 per minute"
CHANGE_LIMIT = "60 per minute"
#: Pasting announcements: plenty for a rep at the start of a semester, slow for a spammer.
ANNOUNCE_LIMIT = "60 per hour"

#: "Today" is the student's day, and every student is in South Africa.
TIMEZONE = "Africa/Johannesburg"

KINDS = ("quiz", "assignment", "practical", "test", "exam")
CHANGES = ("moved", "cancelled")
FLAG_REASONS = ("wrong_date", "wrong_time", "wrong_venue", "not_happening", "duplicate", "other")

TEXT_MAX = 2000
TITLE_MAX = 80
VENUE_MAX = 80
MODULE_MAX = 16

#: An announcement can be dated this many days back (a message forwarded late).
SENT_DAYS_BACK = 60
#: A confirmed event's date: from this many days back...
EVENT_DAYS_BACK = 31
#: ...to this many days ahead.
EVENT_DAYS_AHEAD = 366
#: A "moved" or "cancelled" message is matched against events from this many days before it was sent.
MATCH_DAYS_BACK = 31

#: Announcements one student can have waiting for a rep, per class.
MAX_PENDING = 10

#: The brief: an announcement's text is deleted 30 days after a rep confirms (or discards) it.
TEXT_RETENTION_DAYS = 30
#: An announcement no rep decides on is deleted after this many days.
PENDING_DAYS = 60
#: The brief: flags are kept for 12 months.
FLAG_RETENTION_DAYS = 365

#: GET /classes/<id>/events with no dates: a week back and four months ahead.
EVENTS_BACK_DAYS = 7
EVENTS_AHEAD_DAYS = 120
RANGE_MAX_DAYS = 366

DEFAULT_WEEKS = 8
MAX_WEEKS = 16

#: The engine's week colours, as the app says them.
LOAD_LABELS = {"green": "Manageable", "amber": "Busy", "red": "Heavy"}
