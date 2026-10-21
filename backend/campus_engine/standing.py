"""Where a student stands in a module, and the average needed on what's left."""
from __future__ import annotations

from dataclasses import dataclass

from .text import num


@dataclass
class Assessment:
    name: str
    weight: float  # share of the module mark, e.g. weights that add up to 100
    mark: float | None = None  # percentage; None means not written yet


@dataclass
class Standing:
    current: float | None  # weighted average of completed work
    completed_weight: float
    remaining_weight: float
    needed: float | None  # average needed on the remaining work to reach the target
    status: str  # final | secured | possible | out_of_reach
    message: str


def standing(assessments: list[Assessment], target: float) -> Standing:
    total = sum(a.weight for a in assessments)
    if total <= 0:
        raise ValueError("assessment weights must add up to more than zero")
    done = [a for a in assessments if a.mark is not None]
    done_weight = sum(a.weight for a in done)
    earned = sum(a.weight * a.mark for a in done)
    remaining = total - done_weight
    current = earned / done_weight if done_weight else None

    if remaining <= 0:
        final = earned / total
        msg = f"Final mark {final:.1f}%. " + (
            "Target reached." if final >= target else f"That is {target - final:.1f} points below your {num(target)}% target."
        )
        return Standing(final, done_weight, 0, None, "final", msg)

    needed = (target * total - earned) / remaining
    share = remaining / total * 100
    if needed <= 0:
        status = "secured"
        msg = (
            f"Your completed work already reaches {num(target)}% on the weighted marks. "
            "Check the rule book for any sub-minimum, such as an exam minimum."
        )
    elif needed > 100:
        status = "out_of_reach"
        msg = (
            f"Even 100% on the rest wouldn't reach {num(target)}%. "
            "The rule book's options for supplementary or special assessments are worth a look."
        )
    else:
        status = "possible"
        msg = f"You need an average of {needed:.1f}% on the remaining {share:.0f}% of the mark to reach {num(target)}%."
    return Standing(current, done_weight, remaining, needed, status, msg)
