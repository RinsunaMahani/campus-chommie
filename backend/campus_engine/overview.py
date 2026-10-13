"""Your points at every university we cover, each counted by its own rule, and how many of its
programmes you meet: what a learner sees before picking a university.

Every university counts differently, so the same marks give different points. Each answer says
how that university counts, in plain words, with its source.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .matching import COMPETITIVE, MEETS_MINIMUM, REACH, TIER_RANK, UNVERIFIED, assess_all
from .points import LIFE_ORIENTATION, PointsResult, compute_points
from .schemas import PointsRule, University
from .text import join, plural


@dataclass
class SubjectPoints:
    """One subject at one university: its level on that university's scale and the points it adds."""

    subject: str
    level: int
    points: float  # what it adds here: 0 when it isn't counted
    counted: bool


@dataclass
class UniversityPoints:
    university: str
    name: str
    points: float | None  # None when we don't hold the university's points rule yet
    counted: list[str] = field(default_factory=list)  # the subjects that counted
    subjects: list[SubjectPoints] = field(default_factory=list)  # each subject's level and points, as given
    tiers: dict[str, int] = field(default_factory=dict)  # how many programmes in each tier
    summary: str = ""
    lines: list[str] = field(default_factory=list)  # how this university counts
    source_url: str | None = None


def _how(rule: PointsRule) -> str:
    n = rule.subjects_counted
    if rule.life_orientation == "exclude":
        return f"Counts your best {n} subjects, leaving out Life Orientation."
    if rule.life_orientation == "half":
        return f"Counts {n} subjects: Life Orientation at half its points, and your best {n - 1} others."
    return f"Counts {n} subjects: Life Orientation and your best {n - 1} others."


def _own_tables(rule: PointsRule) -> str | None:
    """Which subjects count on a table of their own here, or points from the percentage, said once."""
    if rule.percent_points:
        p = rule.percent_points
        per = f"Each subject scores {p.per_percent * 100:g} points for every 100%"
        return per + (f", and nothing under {p.from_percent}%." if p.from_percent else ".")
    names = [s.replace("_", " ").title() if s != LIFE_ORIENTATION else "Life Orientation" for s in rule.subject_points]
    if not names:
        return None
    if len(names) == 1:
        return f"{names[0]} counts on its own points table here."
    return f"{join(names)} count on their own points tables here."


def _summary(tiers: dict[str, int]) -> str:
    """A Reach programme's minimum is met too: it adds competitive selection on top."""
    total = sum(tiers.values())
    if not total:
        return "We haven't added this university's programmes yet."
    meets = tiers[COMPETITIVE] + tiers[MEETS_MINIMUM] + tiers[REACH]
    parts = [f"You meet the minimum for {meets} of {plural(total, 'programme')}."]
    if tiers[REACH] == 1:
        parts.append("1 of them selects competitively, so it's a reach.")
    elif tiers[REACH]:
        parts.append(f"{tiers[REACH]} of them select competitively, so each is a reach.")
    if tiers[UNVERIFIED]:
        parts.append(f"We can't check {tiers[UNVERIFIED]} yet.")
    return " ".join(parts)


def university_points(uni: University, marks: dict[str, float]) -> UniversityPoints:
    """One university's points for these marks, and how many of its programmes they meet."""
    tiers = dict.fromkeys(TIER_RANK, 0)
    for m in assess_all(uni, marks):
        tiers[m.tier] += 1
    out = UniversityPoints(uni.university, uni.name, None, tiers=tiers, summary=_summary(tiers))
    rule = uni.points_rules
    if rule is None:
        out.lines = ["We don't have this university's points rule yet."]
        return out
    result = compute_points(marks, rule)
    source = uni.source(rule.source)
    out.points, out.counted = result.total, result.counted
    out.subjects = _subjects(result)
    out.source_url = source.url if source else None
    # The rule line already says how Life Orientation counts.
    out.lines = [_how(rule)] + [line for line in [_own_tables(rule)] if line] + [
        n for n in result.notes if not n.startswith("Life Orientation")
    ]
    if any(p.points_rules for p in uni.programmes):
        out.lines.append("Some programmes count points their own way: their cards show those points.")
    return out


def _subjects(result: PointsResult) -> list[SubjectPoints]:
    """Each subject's level and what it adds, in the order the learner gave them: together they
    make the total."""
    return [SubjectPoints(s, level, result.adds[s], s in result.counted) for s, level in result.levels.items()]


def points_everywhere(catalogue: dict[str, University], marks: dict[str, float]) -> list[UniversityPoints]:
    """Every university we cover, in name order: none is ranked above another."""
    return [university_points(uni, marks) for uni in sorted(catalogue.values(), key=lambda u: u.name)]

