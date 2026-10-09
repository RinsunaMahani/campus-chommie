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


def compute_points(marks: dict[str, float], rule: PointsRule) -> PointsResult:
    """Total points for one learner.

    `marks` maps a subject key (for example 'mathematics') to a percentage.
    Life Orientation counts fully, as half, or not at all, as the rule says.
    The remaining places go to the learner's best other subjects.
    """
    levels = {subject: level_for(pct, rule) for subject, pct in marks.items()}
    notes: list[str] = []
    has_lo = LIFE_ORIENTATION in levels
    lo_counts = has_lo and rule.life_orientation != "exclude"
    lo_points = 0.0
    if has_lo:
        if rule.life_orientation == "full":
            lo_points = float(levels[LIFE_ORIENTATION])
        elif rule.life_orientation == "half":
            lo_points = levels[LIFE_ORIENTATION] / 2
            notes.append("Life Orientation counts for half its points here.")
        else:
            notes.append("Life Orientation is not counted here.")
    places = rule.subjects_counted - (1 if lo_counts else 0)
    others = sorted(
        ((s, lvl) for s, lvl in levels.items() if s != LIFE_ORIENTATION),
        key=lambda kv: kv[1],
        reverse=True,
    )
    best = others[:places]
    total = sum(lvl for _, lvl in best) + lo_points
    counted = [s for s, _ in best] + ([LIFE_ORIENTATION] if lo_counts else [])
    if len(marks) < rule.subjects_counted:
        notes.append(
            f"Only {plural(len(marks), 'subject')} entered; this university counts {rule.subjects_counted}."
        )
    return PointsResult(total=total, levels=levels, counted=counted, notes=notes)
