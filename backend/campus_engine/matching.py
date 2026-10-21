"""Match a learner to programmes and explain every result in plain words.

Tiers:
- not_yet: a required subject or the minimum points are not met
- reach: the minimum is met, but places are limited and selection is competitive
- meets_minimum: the minimum is met for a programme without competitive selection
- competitive: points reach a cut-off the university itself publishes
- unverified: we have not verified this programme's requirements yet
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .points import LIFE_ORIENTATION, compute_points
from .schemas import Programme, University
from .text import num

COMPETITIVE = "competitive"
MEETS_MINIMUM = "meets_minimum"
REACH = "reach"
NOT_YET = "not_yet"
UNVERIFIED = "unverified"

TIER_LABELS = {
    COMPETITIVE: "Competitive",
    MEETS_MINIMUM: "Meets the minimum",
    REACH: "Reach",
    NOT_YET: "Not yet",
    UNVERIFIED: "Not verified yet",
}
TIER_RANK = {COMPETITIVE: 0, MEETS_MINIMUM: 1, REACH: 2, UNVERIFIED: 3, NOT_YET: 4}

NO_GUARANTEE = "Meeting the minimum does not guarantee a place."


@dataclass
class Match:
    university: str
    university_name: str
    programme_id: str
    programme_name: str
    tier: str
    selective: bool = False
    points: float | None = None
    min_points: float | None = None
    gap: float | None = None
    failed: list[str] = field(default_factory=list)
    explanation: list[str] = field(default_factory=list)
    source_url: str | None = None

    @property
    def label(self) -> str:
        return TIER_LABELS[self.tier]


def _pretty(subject: str) -> str:
    return subject.replace("_", " ").capitalize()


def assess(uni: University, programme: Programme, marks: dict[str, float]) -> Match:
    """Assess one programme for one learner."""
    match = Match(
        university=uni.university,
        university_name=uni.name,
        programme_id=programme.id,
        programme_name=programme.name,
        tier=NOT_YET,
        selective=programme.selective,
    )
    req = programme.requirements
    if req is None or uni.points_rules is None:
        match.tier = UNVERIFIED
        match.explanation = [
            "We haven't verified this programme's requirements yet. "
            "Check the university's official prospectus."
        ]
        return match

    source = uni.source(req.source)
    match.source_url = source.url if source else None
    result = compute_points(marks, uni.points_rules)
    match.points = result.total
    match.min_points = req.min_points

    failed: list[str] = []
    for subject, minimum in req.subject_minimums.items():
        level = result.levels.get(subject)
        if level is None:
            failed.append(f"{_pretty(subject)} is required (level {minimum} or higher).")
        elif level < minimum:
            failed.append(f"{_pretty(subject)}: level {level}, needs {minimum}.")
    named = set(req.subject_minimums) | {LIFE_ORIENTATION}
    remaining = sorted((lvl for s, lvl in result.levels.items() if s not in named), reverse=True)
    for i, minimum in enumerate(req.additional_minimums):
        if i >= len(remaining):
            failed.append(f"Additional subject {i + 1} is missing (needs level {minimum}).")
        elif remaining[i] < minimum:
            failed.append(f"Additional subject {i + 1}: level {remaining[i]}, needs {minimum}.")

    explanation = [f"Your points: {num(result.total)} (minimum {num(req.min_points)})."] + result.notes
    if result.total < req.min_points:
        match.gap = req.min_points - result.total

    if failed or match.gap:
        match.failed = failed
        if match.gap:
            explanation.append(f"You need {num(match.gap)} more points to meet the minimum.")
        match.explanation = explanation + failed + req.extras
        return match

    if programme.selective:
        match.tier = REACH
        notes = ["Places are limited and selection is competitive."]
        if programme.selection_note:
            notes.append(programme.selection_note)
        match.explanation = explanation + notes + req.extras + [NO_GUARANTEE]
        return match

    if req.competitive_points is not None and result.total >= req.competitive_points:
        match.tier = COMPETITIVE
    else:
        match.tier = MEETS_MINIMUM
    match.explanation = explanation + req.extras + [NO_GUARANTEE]
    return match


def assess_all(uni: University, marks: dict[str, float]) -> list[Match]:
    """Assess every programme at a university, best tiers first."""
    matches = [assess(uni, p, marks) for p in uni.programmes]
    return sorted(matches, key=lambda m: (TIER_RANK[m.tier], m.programme_name))
