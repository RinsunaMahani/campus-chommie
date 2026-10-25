"""Match a learner to programmes and explain every result in plain words.

Tiers:
- not_yet: a required subject or the minimum points are not met
- reach: the minimum is met, but places are limited and selection is competitive
- meets_minimum: the minimum is met for a programme without competitive selection
- competitive: points reach a cut-off the university itself publishes
- subjects_met: no points rule we can apply here, but every subject minimum is met; the card says how this
  university counts points (or the average it selects on) and where to check
- unverified: we have not verified this programme's requirements yet

Either/or requirements ("Mathematics 5, or Mathematical Literacy 7 with 28 points") are met
by the route that serves the learner best: the one with the lowest minimum.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product

from .points import LIFE_ORIENTATION, compute_points
from .schemas import Choice, Option, PointsRule, Programme, Requirements, University
from .text import join, num

COMPETITIVE = "competitive"
MEETS_MINIMUM = "meets_minimum"
REACH = "reach"
NOT_YET = "not_yet"
UNVERIFIED = "unverified"
SUBJECTS_MET = "subjects_met"

TIER_LABELS = {
    COMPETITIVE: "Competitive",
    MEETS_MINIMUM: "Meets the minimum",
    REACH: "Reach",
    NOT_YET: "Not yet",
    UNVERIFIED: "Not verified yet",
    SUBJECTS_MET: "Subjects met",
}
TIER_RANK = {COMPETITIVE: 0, MEETS_MINIMUM: 1, REACH: 2, SUBJECTS_MET: 3, UNVERIFIED: 4, NOT_YET: 5}

#: The national NSC achievement levels (80-100% = 7 down to 0-29% = 1), the same at every university: subject
#: minimums are written in them, so a learner's subjects can be checked even where we can't add up points.
NSC_LEVELS = PointsRule.model_validate({"source": "nsc", "life_orientation": "full", "scale": [
    {"min_percent": 80, "level": 7}, {"min_percent": 70, "level": 6}, {"min_percent": 60, "level": 5},
    {"min_percent": 50, "level": 4}, {"min_percent": 40, "level": 3}, {"min_percent": 30, "level": 2},
    {"min_percent": 0, "level": 1},
]})

NO_GUARANTEE = "Meeting the minimum does not guarantee a place."


@dataclass
class Match:
    university: str
    university_name: str
    programme_id: str
    programme_name: str
    tier: str
    selective: bool = False
    faculty: str | None = None
    fields: list[str] = field(default_factory=list)
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


def _route(
    choices: list[Choice], levels: dict[str, int], base: float | None
) -> tuple[list[Option | None], float | None]:
    """The options that serve the learner best, one per choice (None where none is met),
    and the minimum points they lead to. The lowest minimum wins, and no published minimum
    counts as the lowest; on a tie the university's own order of options decides."""
    met = [[o for o in c.one_of if _meets(o, levels)] or [None] for c in choices]
    best: tuple[list[Option | None], float | None] | None = None
    for combo in product(*met):  # with no choices, one empty route
        own = [o.min_points for o in combo if o is not None and o.min_points is not None]
        minimum = max(own) if own else base
        if best is None or _lower(minimum, best[1]):
            best = (list(combo), minimum)
    assert best is not None
    return best


def _lower(a: float | None, b: float | None) -> bool:
    """Whether minimum a is lower than b, where None (nothing published) is lowest."""
    if a is None:
        return b is not None
    return b is not None and a < b


def _check_subjects(req: Requirements, levels: dict[str, int], marks: dict[str, float]
                    ) -> tuple[list[str], list[str], float | None]:
    """What the subject requirements leave unmet, notes on either/or choices, and the minimum points the
    learner's best route leads to."""
    failed: list[str] = []
    for subject, minimum in req.subject_minimums.items():
        level = levels.get(subject)
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

    route, min_points = _route(req.choices, levels, req.min_points)
    route_notes: list[str] = []
    named = set(req.subject_minimums) | set(req.subject_min_percents) | {LIFE_ORIENTATION}
    for choice, option in zip(req.choices, route, strict=True):
        listed = [s for o in choice.one_of for s in o.subjects]
        if option is None:
            line = f"Needs one of: {_either([_describe(o) for o in choice.one_of])}."
            have = [s for s in dict.fromkeys(listed) if s in levels]
            if have:
                line += " You have " + join([f"{_pretty(s)} at level {levels[s]}" for s in have]) + "."
            failed.append(line)
            named |= set(listed)
        else:
            counted = join([f"{_pretty(s)} (level {levels[s]})" for s in option.subjects])
            route_notes.append(f"Counted {counted} for an either/or requirement.")
            named |= set(option.subjects)
    if min_points != req.min_points:
        cause = next(o for o in route if o is not None and o.min_points == min_points)
        instead = "" if req.min_points is None else f" instead of {num(req.min_points)}"
        route_notes.append(f"With {_describe(cause)}, the minimum is {num(min_points)} points{instead}.")

    remaining = sorted((lvl for s, lvl in levels.items() if s not in named), reverse=True)
    for i, minimum in enumerate(req.additional_minimums):
        if i >= len(remaining):
            failed.append(f"Additional subject {i + 1} is missing (needs level {minimum}).")
        elif remaining[i] < minimum:
            failed.append(f"Additional subject {i + 1}: level {remaining[i]}, needs {minimum}.")

    return failed, route_notes, min_points


def assess(uni: University, programme: Programme, marks: dict[str, float],
           english_language_level: str | None = None) -> Match:
    match = _assess(uni, programme, marks)
    req = programme.requirements
    if req and req.max_assessed_points is not None:
        if match.points is not None and match.points > req.max_assessed_points and match.tier != NOT_YET:
            match.tier = UNVERIFIED
            match.explanation.append(
                f"The published entry bands end at {num(req.max_assessed_points)} points. "
                "Your score is above those bands; ask the university which entry route applies."
            )
        elif match.points is None:
            match.explanation.append(
                f"The published entry bands end at {num(req.max_assessed_points)} points; "
                "the university needs to check your score against those bands."
            )
    if req and req.alternative_entry:
        match.explanation.append(req.alternative_entry)
        alternatives = req.alternative_entry_subjects
        if match.tier == NOT_YET and not match.gap and (not alternatives or all(
            any(failure.startswith(_pretty(subject) + suffix) for subject in alternatives for suffix in (" is required", ":"))
            for failure in match.failed
        )):
            match.tier = UNVERIFIED
            match.explanation.append("Your school marks do not meet this route. An alternative entry route needs the university to check your other qualifications or experience.")
    if not req or not req.english_language_levels:
        return match
    levels = req.english_language_levels
    level = compute_points({"english": marks["english"]}, NSC_LEVELS).levels["english"] if "english" in marks else 0
    if english_language_level in levels:
        needed = levels[english_language_level]
        if level < needed:
            message = f"English {english_language_level.replace('_', ' ')} language needs level {needed}; yours is {level}."
            match.tier = NOT_YET
            match.failed.append(message)
            match.explanation.append(message)
    elif level < min(levels.values()):
        match.tier = NOT_YET
        message = f"English needs at least level {min(levels.values())}."
        match.failed.append(message)
        match.explanation.append(message)
    elif level < max(levels.values()) and match.tier != NOT_YET:
        match.tier = UNVERIFIED
        match.explanation.append("Choose English Home Language or First Additional Language on the marks screen to check this requirement.")
    return match


def _assess(uni: University, programme: Programme, marks: dict[str, float]) -> Match:
    """Assess one programme for one learner."""
    match = Match(
        university=uni.university,
        university_name=uni.name,
        programme_id=programme.id,
        programme_name=programme.name,
        tier=NOT_YET,
        selective=programme.selective,
        faculty=programme.faculty,
        fields=list(programme.fields),
    )
    req = programme.requirements
    rule = programme.points_rules or uni.points_rules
    if req is not None and rule is None:
        return _subjects_only(uni, programme, req, marks, match)
    if req is None:
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
    failed, route_notes, min_points = _check_subjects(req, result.levels, marks)
    match.min_points = min_points
    if min_points is None:
        explanation = ["The source does not state the points threshold for your subject route. Only your subjects were checked."] if req.points_threshold_incomplete else [
            f"Your points: {num(result.total)}. The university publishes no points minimum for this "
            "programme, so only your subjects were checked."
        ]
    else:
        explanation = [f"Your points: {num(result.total)} (minimum {num(min_points)})."]
    if programme.points_rules is not None:
        explanation.append("This programme uses its own points table, not the university's usual one.")
    explanation += result.notes + route_notes
    if min_points is not None and result.total < min_points:
        match.gap = min_points - result.total

    if failed or match.gap:
        match.failed = failed
        if match.gap:
            unit = "point" if match.gap == 1 else "points"
            explanation.append(f"You need {num(match.gap)} more {unit} to meet the minimum.")
        match.explanation = explanation + failed + req.extras
        return match

    if min_points is None and req.points_threshold_incomplete:
        match.tier = SUBJECTS_MET
        match.explanation = explanation + req.extras + [NO_GUARANTEE]
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


def assess_all(uni: University, marks: dict[str, float], english_language_level: str | None = None) -> list[Match]:
    """Assess every programme at a university, best tiers first."""
    matches = [assess(uni, p, marks, english_language_level) for p in uni.programmes]
    return sorted(matches, key=lambda m: (TIER_RANK[m.tier], m.programme_name))


def _average(marks: dict[str, float], best: int) -> float | None:
    """The average of the learner's best `best` subjects, Life Orientation left out (None if they gave fewer)."""
    top = sorted((pct for s, pct in marks.items() if s != LIFE_ORIENTATION), reverse=True)[:best]
    return round(sum(top) / best, 1) if len(top) == best else None


def _subjects_only(uni: University, programme: Programme, req: Requirements, marks: dict[str, float],
                   match: Match) -> Match:
    """A university whose points we can't add up: check every subject requirement on the national NSC levels,
    then say how this university counts points (or the average it selects on) and where to check."""
    source = uni.source(req.source)
    match.source_url = source.url if source else None
    failed, route_notes, min_points = _check_subjects(req, compute_points(marks, NSC_LEVELS).levels, marks)
    how = uni.points_how
    points: list[str] = []
    if min_points is not None:
        points.append(f"It also asks for {num(min_points)} points, counted {uni.name}'s own way, which we can't "
                      "add up for you.")
    if how is not None:
        points.append(how.text)
        if how.average_of_best:
            avg = _average(marks, how.average_of_best)
            if avg is not None:
                points.append(f"Your average of your best {how.average_of_best} subjects, without Life "
                              f"Orientation: {num(avg)}%.")
    elif uni.points_note:
        points.append(uni.points_note)
    if failed:
        match.failed = failed
        match.explanation = ["Not all of this programme's subject minimums are met."] + failed + points + req.extras
        return match
    match.tier = SUBJECTS_MET
    selection = (["Places are limited and selection is competitive."]
                 + ([programme.selection_note] if programme.selection_note else [])) if programme.selective else []
    match.explanation = (["Your subjects meet this programme's minimums."] + route_notes + points + selection
                         + req.extras + [NO_GUARANTEE])
    return match
