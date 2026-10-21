"""
Marks in, matches and a plan out. Services call the engine; routes never do.

Marks exist only for the length of one request: nothing here writes to the
database or logs them. Every answer keeps the engine's plain-words "why"
lines and the source of each fact, and says whether a person has checked
the pack it came from.

A plan also says how to apply, on today's date in South Africa: each choice's
application windows, every date still ahead, each university's fee, documents
and next steps, and national funding (NSFAS).
"""
from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

from campus_engine.applications import ApplyGuide, Group, Guide, WindowStatus, apply_guide
from campus_engine.bridges import GUARANTEE_LABELS, Plan, Slot, build_plan
from campus_engine.matching import Match, assess_all
from campus_engine.overview import UniversityPoints, points_everywhere
from campus_engine.schemas import University
from src.core.exceptions import NotFoundError
from src.domains.catalogue.funding.services import funding_service as funding
from src.domains.catalogue.universities.services import university_service as catalogue

from ..constants import TIMEZONE


def _today() -> date:
    """Today in South Africa: every application date is SAST."""
    return datetime.now(ZoneInfo(TIMEZONE)).date()


def _marks(rows: list[dict]) -> dict[str, float]:
    return {row["subject"]: row["percent"] for row in rows}


def points(rows: list[dict]) -> dict:
    """The learner's points at every university we cover, each by its own rule, in name order."""
    packs = catalogue.packs()
    return {"universities": [_points(u, packs) for u in points_everywhere(packs, _marks(rows))]}


def assess(university_id: str, rows: list[dict]) -> dict:
    """Every programme at one university for these marks, best tiers first."""
    uni = catalogue.get(university_id)
    packs = catalogue.packs()
    return {"university": catalogue.summary(uni), "matches": [_match(m, packs) for m in assess_all(uni, _marks(rows))]}


def plan(university_id: str, goal: str, rows: list[dict]) -> dict:
    """The three-choice plan: the goal, a published route into it, a safer related choice, and how to apply."""
    uni = catalogue.get(university_id)
    if all(p.id != goal for p in uni.programmes):
        raise NotFoundError("That university has no such programme.", code="PROGRAMME_NOT_FOUND")
    packs = catalogue.packs()
    built = build_plan(packs, uni.university, goal, _marks(rows))
    guide = apply_guide(packs, funding.pack(), built, _today())
    return {"plan": _plan(built, packs, guide)}


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


def _points(u: UniversityPoints, packs: dict[str, University]) -> dict:
    return {
        "university": u.university,
        "university_name": u.name,
        "points": u.points,
        "counted": u.counted,
        "tiers": u.tiers,
        "summary": u.summary,
        "lines": u.lines,
        "source_url": u.source_url,
        **catalogue.confirmation(packs[u.university]),
    }


def _slot(slot: Slot | None, packs: dict[str, University], guide: ApplyGuide) -> dict | None:
    if slot is None:
        return None
    windows = guide.windows[(slot.match.university, slot.match.programme_id)]
    out = {
        "number": slot.number,
        "role": slot.role,
        "match": _match(slot.match, packs),
        "notes": slot.notes,
        "apply": [_window(w) for w in windows],
    }
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


def _plan(plan: Plan, packs: dict[str, University], guide: ApplyGuide) -> dict:
    return {
        "goal": _slot(plan.goal, packs, guide),
        "bridge": _slot(plan.bridge, packs, guide),
        "safe": _slot(plan.safe, packs, guide),
        "other_routes": [_slot(s, packs, guide) for s in plan.other_routes],
        "notes": plan.notes,
        "apply": _apply(guide, packs),
    }


def _iso(d: date | None) -> str | None:
    return d.isoformat() if d else None


def _window(w: WindowStatus) -> dict:
    return {
        "intake": w.intake,
        "heading": w.heading,
        "status": w.status,
        "label": w.label,
        "opens": _iso(w.opens),
        "closes": _iso(w.closes),
        "closes_one_of": [d.isoformat() for d in w.closes_one_of],
        "late_opens": _iso(w.late_opens),
        "late_closes": _iso(w.late_closes),
        "next_date": _iso(w.next_date),
        "days": w.days,
        "lines": w.lines,
        "source_url": w.source_url,
    }


def _group(group: Group | None) -> dict | None:
    return {"items": group.items, "source_url": group.source_url} if group else None


def _guide(g: Guide, confirmation: dict) -> dict:
    return {
        "id": g.id,
        "name": g.name,
        "kind": g.kind,
        "url": g.url,
        "how": g.how,
        "fee_cents": g.fee_cents,
        "fee_note": g.fee_note,
        "contact": g.contact,
        "max_choices": g.max_choices,
        "documents": _group(g.documents),
        "after": [{"text": a.text, "source_url": a.source_url} for a in g.after],
        "who_can_apply": _group(g.who_can_apply),
        "tips": _group(g.tips),
        "warnings": _group(g.warnings),
        "windows": [_window(w) for w in g.windows],
        "lines": g.lines,
        "source_url": g.source_url,
        **confirmation,
    }


def _apply(guide: ApplyGuide, packs: dict[str, University]) -> dict:
    funding_confirmation = funding.confirmation(funding.pack())
    return {
        "today": guide.today.isoformat(),
        "universities": [_guide(g, catalogue.confirmation(packs[g.id])) for g in guide.universities],
        "funding": [_guide(g, funding_confirmation) for g in guide.funding],
        "deadlines": [
            {
                "date": d.on.isoformat(),
                "days": d.days,
                "text": d.text,
                "intake": d.intake,
                "who": d.who,
                "programme": d.programme_id,
                "source_url": d.source_url,
            }
            for d in guide.deadlines
        ],
        "notes": guide.notes,
    }
