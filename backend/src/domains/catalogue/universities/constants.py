"""The catalogue's limits and wording."""
from __future__ import annotations

#: Per IP: the catalogue is public, with no user to count by. A school computer
#: lab shares one address, so this leaves room for a class browsing at once.
READ_LIMIT = "120 per minute"

#: Shown with every pack nobody has checked yet (`release: false`), which is
#: every pack today. Served anyway so the demo works (decided 9 Oct 2026).
UNCONFIRMED_NOTICE = "Not yet confirmed by the team."
