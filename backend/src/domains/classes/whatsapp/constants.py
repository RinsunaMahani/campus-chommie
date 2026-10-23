"""The WhatsApp bot's limits."""
from __future__ import annotations

#: Per student, in the app.
READ_LIMIT = "60 per minute"
CODE_LIMIT = "10 per hour"
CHANGE_LIMIT = "30 per minute"
#: Meta's servers, per address: every student's messages come through them, so this only stops a flood.
WEBHOOK_LIMIT = "600 per minute"
#: Per WhatsApp number (counted on its hash). LINK attempts are counted on their own, so codes can't be guessed.
SENDER_LIMIT = "30/minute;300/day"
LINK_ATTEMPT_LIMIT = "5/hour"

#: A link code: 8 characters a person can't misread (no 0/O, 1/I/L), so ~8e11 codes; valid this long, once.
CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
CODE_LENGTH = 8
CODE_MINUTES = 10
#: Numbers one account may link (a demo account's judges share it).
MAX_LINKS = 5

#: A message older than this when it reaches us is dropped (a replay or a very late retry), and one from
#: further than this in the future too.
MAX_AGE_SECONDS = 300
MAX_AHEAD_SECONDS = 60
#: Message ids seen are kept this long, so Meta's retries are answered once.
SEEN_HOURS = 48

#: WhatsApp's own limits on what we send.
TEXT_MAX = 4096
BUTTON_BODY_MAX = 1024
SEND_TIMEOUT_SECONDS = 10

#: WEEK looks this many days ahead.
WEEK_DAYS = 7

TIMEZONE = "Africa/Johannesburg"
