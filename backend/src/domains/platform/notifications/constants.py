"""Notifications' limits."""
from __future__ import annotations

PAGE_DEFAULT = 20
PAGE_MAX = 50
#: Older alerts are deleted by the scheduler: they copy what each feature
#: and the audit trail already keep.
RETENTION_DAYS = 90

#: "Today" for the daily checks is the student's day, and every student is in South Africa.
TIMEZONE = "Africa/Johannesburg"

#: Per user. The app asks for the count every 20 s while it's open (3 a
#: minute), so 120 leaves room for two phones and pulling to refresh.
READ_LIMIT = "120 per minute"
CHANGE_LIMIT = "30 per minute"
