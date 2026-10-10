"""Match a learner to programmes and explain every result in plain words.

Tiers:
- not_yet: a required subject or the minimum points are not met
- reach: the minimum is met, but places are limited and selection is competitive
- meets_minimum: the minimum is met for a programme without competitive selection
- competitive: points reach a cut-off the university itself publishes
- unverified: we have not verified this programme's requirements yet

Either/or requirements ("Mathematics 5, or Mathematical Literacy 7 with 28 points") are met
by the route that serves the learner best: the one with the lowest minimum.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product

from .points import LIFE_ORIENTATION, compute_points
from .schemas import Choice, Option, Programme, University
from .text import join, num

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


def _either(parts: list[str]) -> str:
    """Join a choice's options (always two or more) with a final 'or'. Options naming several
    subjects are kept apart with semicolons."""
    if any(" and " in p for p in parts):
        return "; ".join(parts[:-1]) + "; or " + parts[-1]
    return ", ".join(parts[:-1]) + " or " + parts[-1]


def _describe(option: Option) -> str:
    return join([f"{_pretty(s)} level {lvl}" for s, lvl in option.subjects.items()])


def _meets(option: Option, levels: dict[str, int]) -> bool:
    return all(levels.get(s, 0) >= lvl for s, lvl in option.subjects.items())


def _route(choices: list[Choice], levels: dict[str, int], base: float) -> tuple[list[Option | None], float]:
    """The options that serve the learner best, one per choice (None where none is met),
    and the minimum points they lead to. The lowest minimum wins; on a tie the university's
    own order of options decides."""
    met = [[o for o in c.one_of if _meets(o, levels)] or [None] for c in choices]
    best: tuple[list[Option | None], float] | None = None
    for combo in product(*met):  # with no choices, one empty route
        own = [o.min_points for o in combo if o is not None and o.min_points is not None]
        minimum = max(own) if own else base
        if best is None or minimum < best[1]:
            best = (list(combo), minimum)
    assert best is not None
    return best


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
    rule = programme.points_rules or uni.points_rules
    if req is None or rule is None:
        match.tier = UNVERIFIED
        match.explanation = [
            "We can't check this programme's requirements against your marks yet. "
            "Check the university's official prospectus."
        ]
        if programme.selection_note:
            match.explanation.append(programme.selection_note)
        return match

    source = uni.source(req.source)
    match.source_url = source.url if source else None
    result = compute_points(marks, rule)
    match.points = result.total

    failed: list[str] = []
    for subject, minimum in req.subject_minimums.items():
        level = result.levels.get(subject)
        if level is None:
            failed.append(f"{_pretty(subject)} is required (level {minimum} or higher).")
        elif level < minimum:
            failed.append(f"{_pretty(subject)}: level {level}, needs {minimum}.")
    for subject, minimum in req.subject_min_percents.items():
        percent = marks.get(subject)
        if percent is None:
            failed.append(f"{_pretty(subject)} is required ({minimum}% or higher).")
        elif percent < minimum:
            failed.append(f"{_pretty(subject)}: {num(percent)}%, needs {minimum}%.")

    route, min_points = _route(req.choices, result.levels, req.min_points)
    match.min_points = min_points
    route_notes: list[str] = []
    named = set(req.subject_minimums) | set(req.subject_min_percents) | {LIFE_ORIENTATION}
    for choice, option in zip(req.choices, route, strict=True):
        listed = [s for o in choice.one_of for s in o.subjects]
        if option is None:
            line = f"Needs one of: {_either([_describe(o) for o in choice.one_of])}."
            have = [s for s in dict.fromkeys(listed) if s in result.levels]
            if have:
                line += " You have " + join([f"{_pretty(s)} at level {result.levels[s]}" for s in have]) + "."
            failed.append(line)
            named |= set(listed)
        else:
            counted = join([f"{_pretty(s)} (level {result.levels[s]})" for s in option.subjects])
            route_notes.append(f"Counted {counted} for an either/or requirement.")
            named |= set(option.subjects)
    if min_points != req.min_points:
        cause = next(o for o in route if o is not None and o.min_points == min_points)
        route_notes.append(
            f"With {_describe(cause)}, the minimum is {num(min_points)} points instead of {num(req.min_points)}."
        )

    remaining = sorted((lvl for s, lvl in result.levels.items() if s not in named), reverse=True)
    for i, minimum in enumerate(req.additional_minimums):
        if i >= len(remaining):
            failed.append(f"Additional subject {i + 1} is missing (needs level {minimum}).")
        elif remaining[i] < minimum:
            failed.append(f"Additional subject {i + 1}: level {remaining[i]}, needs {minimum}.")

    explanation = [f"Your points: {num(result.total)} (minimum {num(min_points)})."]
    if programme.points_rules is not None:
        explanation.append("This programme uses its own points table, not the university's usual one.")
    explanation += result.notes + route_notes
    if result.total < min_points:
        match.gap = min_points - result.total

    if failed or match.gap:
        match.failed = failed
        if match.gap:
            unit = "point" if match.gap == 1 else "points"
            explanation.append(f"You need {num(match.gap)} more {unit} to meet the minimum.")
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
