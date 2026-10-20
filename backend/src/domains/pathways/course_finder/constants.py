"""The course finder's limits and the subjects a learner can enter."""
from __future__ import annotations

from campus_engine.schemas import SUBJECTS

#: Per IP: no account, so no user to count by. A school computer lab shares
#: one address, so this leaves room for a class asking at the same time.
ASSESS_LIMIT = "120 per minute"
PLAN_LIMIT = "120 per minute"
POINTS_LIMIT = "120 per minute"
#: How to apply (no marks): the same room as the rest of the course finder.
APPLY_LIMIT = "120 per minute"

#: The most subjects a learner can enter: the NSC has seven, and some learners take more.
MAX_SUBJECTS = 9

#: Rows for subjects no admission rule names. They count towards points only,
#: so the app needn't list every school subject (decided 9 Oct 2026).
ANOTHER_SUBJECTS = ("another_subject_1", "another_subject_2", "another_subject_3")

#: Every subject key a learner may send.
SUBJECT_KEYS = frozenset(SUBJECTS) | frozenset(ANOTHER_SUBJECTS)

#: Application dates are South African dates: a plan's "today" is today in SAST.
TIMEZONE = "Africa/Johannesburg"
