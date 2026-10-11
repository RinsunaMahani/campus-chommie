"""Funding's limits and wording."""
from __future__ import annotations

#: Shown with the funding pack while nobody has checked it (`release: false`), the same
#: words as an unchecked university pack.
UNCONFIRMED_NOTICE = "Not yet confirmed by the team."

#: Per IP: the funding list is public, with no user to count by. A school computer lab
#: shares one address, so this leaves room for a class browsing at once.
READ_LIMIT = "120 per minute"

#: The most field tags one search may name ("engineering,computing").
MAX_FIELDS = 10

#: Application dates are South African dates: the list's "today" is today in SAST.
TIMEZONE = "Africa/Johannesburg"
