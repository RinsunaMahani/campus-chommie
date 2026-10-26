"""How often the attack watch looks back over the audit trail, and when it speaks up (security sweep 3)."""
from __future__ import annotations

WATCH_EVERY_SECONDS = 60 * 60
#: Failed events of one kind in the last hour that are worth a look: far above what students mistyping a password
#: make (a handful an hour), well below what a password-guessing script makes.
WATCH_ONE_KIND = 50
#: All failed events in the last hour, of every kind together.
WATCH_ALL_KINDS = 200
