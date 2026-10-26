"""Points (APS-style) calculation, using each university's own rules.

Universities count subjects differently, so there is no shared national formula here:
the scale, the number of subjects and the treatment of Life Orientation all come
from the university's data pack.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .schemas import PointsRule
from .text import plural

LIFE_ORIENTATION = "life_orientation"


def level_for(percent: float, rule: PointsRule) -> int:
    """Convert a percentage to this university's level."""
    if not 0 <= percent <= 100:
        raise ValueError(f"percentage must be between 0 and 100, got {percent}")
    for band in sorted(rule.scale, key=lambda b: b.min_percent, reverse=True):
        if percent >= band.min_percent:
            return band.level
    raise ValueError("points scale has no band for this percentage")  # schema requires a 0% band


@dataclass
class PointsResult:
    total: float
    levels: dict[str, int]
    counted: list[str]
    notes: list[str] = field(default_factory=list)
    adds: dict[str, float] = field(default_factory=dict)  # what each subject added: 0 when not counted
    complete: bool = True


def subject_points(subject: str, percent: float, level: int, rule: PointsRule) -> float:
    """What one subject is worth at this university: its own table's points where the university
    gives one; points from the percentage where the university counts that way; otherwise its level
    (none below the rule's lowest counted level)."""
    table = rule.subject_points.get(subject) or rule.other_points
    if table:
        return next(b.points for b in sorted(table, key=lambda b: b.min_percent, reverse=True) if percent >= b.min_percent)
    if rule.percent_points:
        p = rule.percent_points
        return round(percent * p.per_percent, 2) if percent >= p.from_percent else 0.0
    return float(points_for(level, rule))


def points_for(level: int, rule: PointsRule) -> int:
    """Points one subject adds: its level, or nothing below the rule's lowest counted level."""
    return level if level >= rule.count_from_level else 0


def compute_points(marks: dict[str, float], rule: PointsRule, english_language_level: str | None = None,
                   language_marks: dict[str, tuple[float, str | None]] | None = None) -> PointsResult:
    """Total points for one learner.

    `marks` maps a subject key (for example 'mathematics') to a percentage.
    Life Orientation counts fully, as half, or not at all, as the rule says.
    The remaining places go to the learner's best other subjects. A subject below the
    rule's lowest counted level takes a place but adds no points.
    """
    levels = {subject: level_for(pct, rule) for subject, pct in marks.items()}
    worth = {subject: subject_points(subject, marks[subject], lvl, rule) for subject, lvl in levels.items()}
    notes: list[str] = []
    complete = True
    if rule.exact_subject_count and (len(marks) != rule.subjects_counted or LIFE_ORIENTATION not in marks):
        complete = False
        notes.append(f"Enter exactly {rule.subjects_counted} NSC subjects including Life Orientation to calculate this APS; ask the university how to handle extra subjects.")
    if rule.home_language_points:
        roles = {s: entry[1] for s, entry in (language_marks or {}).items() if s in marks}
        if "english" in marks:
            roles["english"] = english_language_level
        if "other_language" in marks:
            roles.setdefault("other_language", None)
        for subject, role in roles.items():
            if role == "home":
                worth[subject] = next(b.points for b in sorted(rule.home_language_points, key=lambda b: b.min_percent, reverse=True)
                                      if marks[subject] >= b.min_percent)
            elif role != "first_additional":
                complete = False
                notes.append(f"Choose Home or First Additional Language for {subject.replace('_', ' ')} to calculate its APS bonus.")
    has_lo = LIFE_ORIENTATION in levels
    lo_counts = has_lo and rule.life_orientation != "exclude"
    lo_points = 0.0
    if has_lo:
        if rule.life_orientation == "full":
            lo_points = worth[LIFE_ORIENTATION]
        elif rule.life_orientation == "half":
            lo_points = worth[LIFE_ORIENTATION] / 2
            notes.append("Life Orientation counts for half its points here.")
        else:
            notes.append("Life Orientation is not counted here.")
    places = rule.subjects_counted - (1 if lo_counts else 0)
    # The best are the ones worth most here; on a tie, the higher level, then the order given.
    others = sorted(
        ((s, lvl) for s, lvl in levels.items() if s != LIFE_ORIENTATION),
        key=lambda kv: (worth[kv[0]], kv[1]),
        reverse=True,
    )
    best = others[:places]
    total = sum(worth[s] for s, _ in best) + lo_points
    counted = [s for s, _ in best] + ([LIFE_ORIENTATION] if lo_counts else [])
    adds = {s: 0.0 for s in levels}
    adds.update({s: worth[s] for s, _ in best})
    if lo_counts:
        adds[LIFE_ORIENTATION] = lo_points
    if any(levels[s] < rule.count_from_level for s in counted):
        notes.append(f"Subjects below level {rule.count_from_level} add no points here.")
    if rule.note:
        notes.append(rule.note)
    if len(marks) < rule.subjects_counted:
        notes.append(
            f"Only {plural(len(marks), 'subject')} entered; this university counts {rule.subjects_counted}."
        )
    return PointsResult(total=total, levels=levels, counted=counted, notes=notes, adds=adds, complete=complete)
