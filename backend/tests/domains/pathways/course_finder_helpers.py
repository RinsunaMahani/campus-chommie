"""Shared by the course-finder tests: the endpoints and the strong SMU learner."""
from __future__ import annotations

ASSESS = "/api/v1/pathways/assess"
PLAN = "/api/v1/pathways/plan"

#: The strong learner from the engine tests (47 points at SMU), as the app sends them.
STRONG = [
    {"subject": "english", "percent": 82},
    {"subject": "mathematics", "percent": 81},
    {"subject": "physical_sciences", "percent": 80},
    {"subject": "life_sciences", "percent": 85},
    {"subject": "life_orientation", "percent": 88},
    {"subject": "geography", "percent": 74},
    {"subject": "other_language", "percent": 79},
]


def marks(**changes) -> list[dict]:
    """STRONG with some subjects' marks changed, e.g. marks(mathematics=55)."""
    return [{"subject": m["subject"], "percent": changes.get(m["subject"], m["percent"])} for m in STRONG]
