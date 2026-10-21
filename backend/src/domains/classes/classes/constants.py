"""Classes' limits."""
from __future__ import annotations

#: Per student.
READ_LIMIT = "120 per minute"
CHANGE_LIMIT = "30 per minute"
#: Joining is slow on purpose: an invite code can't be found by guessing.
JOIN_LIMIT = "20 per hour"
CREATE_LIMIT = "10 per hour"

#: "Today" is the student's day, and every student is in South Africa.
TIMEZONE = "Africa/Johannesburg"

#: No 0/O or 1/I/L: a code read out in a lecture hall is typed right first time.
CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
INVITE_LENGTH = 8
#: Longer, so it can never be mistaken for an invite code.
REP_CODE_LENGTH = 10
REP_CODE_HOURS = 48

MAX_REPS = 3
#: Classes one student can be in at once.
MAX_CLASSES = 20

MODULE_CODE_MAX = 16
MODULE_NAME_MAX = 80
ROLES = ("student", "rep")

#: A class is kept for its academic year and one more (the brief), then the scheduler deletes it.
YEARS_KEPT_AFTER = 1
