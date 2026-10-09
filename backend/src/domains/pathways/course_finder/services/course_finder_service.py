"""
Marks in, matches and a plan out. Services call the engine; routes never do.

Marks exist only for the length of one request: nothing here writes to the
database or logs them. Every answer keeps the engine's plain-words "why"
lines and the source of each fact, and says whether a person has checked
the pack it came from.
"""
from __future__ import annotations

from campus_engine.bridges import GUARANTEE_LABELS, Plan, Slot, build_plan
from campus_engine.matching import Match, assess_all
from campus_engine.schemas import University
from src.core.exceptions import NotFoundError
from src.domains.catalogue.universities.services import university_service as catalogue


def _marks(rows: list[dict]) -> dict[str, float]:
    return {row["subject"]: row["percent"] for row in rows}


def assess(university_id: str, rows: list[dict]) -> dict:
    """Every programme at one university for these marks, best tiers first."""
    uni = catalogue.get(university_id)
    packs = catalogue.packs()
    return {"university": catalogue.summary(uni), "matches": [_match(m, packs) for m in assess_all(uni, _marks(rows))]}


def plan(university_id: str, goal: str, rows: list[dict]) -> dict:
    """The three-choice plan: the goal, a published route into it, and a safer related choice."""
    uni = catalogue.get(university_id)
    if all(p.id != goal for p in uni.programmes):
        raise NotFoundError("That university has no such programme.", code="PROGRAMME_NOT_FOUND")
    packs = catalogue.packs()
    return {"plan": _plan(build_plan(packs, uni.university, goal, _marks(rows)), packs)}


def _match(m: Match, packs: dict[str, University]) -> dict:
    return {
        "university": m.university,
        "university_name": m.university_name,
        "programme": m.programme_id,
        "programme_name": m.programme_name,
        "tier": m.tier,
        "label": m.label,
        "selective": m.selective,
        "points": m.points,
        "min_points": m.min_points,
        "gap": m.gap,
        "failed": m.failed,
        "explanation": m.explanation,
        "source_url": m.source_url,
        **catalogue.confirmation(packs[m.university]),
    }


def _slot(slot: Slot | None, packs: dict[str, University]) -> dict | None:
    if slot is None:
        return None
    out = {"number": slot.number, "role": slot.role, "match": _match(slot.match, packs), "notes": slot.notes}
    if slot.bridge is not None:
        bridge = slot.bridge
        source = packs[slot.match.university].source(bridge.source)
        out["bridge"] = {
            "to": bridge.to,
            "guarantee": bridge.guarantee,
            "guarantee_label": GUARANTEE_LABELS[bridge.guarantee],
            "conditions": bridge.conditions,
            "max_places": bridge.max_places,
            "added_years": bridge.added_years,
            "eligibility_note": bridge.eligibility_note,
            "source_url": source.url if source else None,
        }
    return out


def _plan(plan: Plan, packs: dict[str, University]) -> dict:
    return {
        "goal": _slot(plan.goal, packs),
        "bridge": _slot(plan.bridge, packs),
        "safe": _slot(plan.safe, packs),
        "other_routes": [_slot(s, packs) for s in plan.other_routes],
        "notes": plan.notes,
    }
