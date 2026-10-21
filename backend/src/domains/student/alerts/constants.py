"""Alerts' and support's limits and wording."""
from __future__ import annotations

#: Per student.
READ_LIMIT = "120 per minute"

#: "Today" is the student's day, and every student is in South Africa.
TIMEZONE = "Africa/Johannesburg"

#: The kinds of support the brief's Support screen lists, in its order; each shows, even when the pack has none.
SUPPORT_KINDS = ("counselling", "crisis", "financial_aid", "food_support", "tutoring", "chaplaincy", "health")
#: Shown too when the student's campus has them.
EXTRA_KINDS = ("careers", "disability")

NOT_VERIFIED = "Not verified yet"
NO_CAMPUS = "Choose your university and campus in your profile to see your campus's support."
#: CLAUDE.md: crisis contacts are verified by a person before release. Until then they're held back.
CRISIS_HELD = "Crisis numbers show here once a person on our team has checked them with the university."
NO_MONEY = "Add your balance in Money and we'll warn you before it runs short."
NO_CLASSES = "Join your classes and we'll warn you about heavy weeks."
