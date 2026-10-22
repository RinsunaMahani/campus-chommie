"""My money's limits."""
from __future__ import annotations

#: Per student.
READ_LIMIT = "120 per minute"
CHANGE_LIMIT = "60 per minute"

#: "Today" is the student's day, and every student is in South Africa.
TIMEZONE = "Africa/Johannesburg"

#: R1 000 000: an amount bigger than this is almost certainly a typo.
MAX_CENTS = 100_000_000

MAX_SOURCES = 10
MAX_GOALS = 10
GOAL_LABEL_MAX = 80
GOAL_KINDS = ("goal", "family", "stokvel", "buffer", "big_purchase")
#: A goal's date: from today to this many days ahead (a fee date for next year fits).
GOAL_DAYS_AHEAD = 731
#: University fee dates shown this far ahead.
UNIVERSITY_DATES_AHEAD = 366
LABEL_MAX = 60
RELIABILITY = ("on_time", "sometimes_late", "often_late", "not_sure")

#: A payment this many days overdue still shows, so it can be marked received; older ones are history.
PAST_DAYS = 31

#: How far back a balance, a one-off payment or a day's spending may be dated.
MAX_DAYS_BACK = 366

#: Spending is kept for a rolling year (the brief), then the scheduler deletes it.
SPENDING_RETENTION_DAYS = 366

#: The logged days the spending pace is worked out from.
PACE_DAYS = 30
