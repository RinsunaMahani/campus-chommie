"""
The catalogue's answers. Other features (the course finder) read packs
through here, never through the repository.

A pack nobody has checked yet is still served, with `confirmed: false` and a
notice the app shows next to it.
"""
from __future__ import annotations

from datetime import date

import math

from campus_engine import browse
from campus_engine.config import load_config
from campus_engine.funding import cards as funding_cards
from campus_engine.journey import FirstSteps
from campus_engine.journey import first_steps as build_first_steps
from campus_engine.schemas import University
from src.core.exceptions import NotFoundError
from src.core.exceptions import ValidationError as ApiValidationError
from src.domains.catalogue.funding.services import funding_service as funding
from src.shared.clock.clock import today_sast

from ..constants import UNCONFIRMED_NOTICE
from ..repositories.pack_repository import all_packs


def packs() -> dict[str, University]:
    """Every pack, by university id: the whole catalogue a plan may draw on."""
    return all_packs()


def get(university_id: str) -> University:
    uni = all_packs().get(university_id)
    if uni is None:
        raise NotFoundError("We don't have that university.", code="UNIVERSITY_NOT_FOUND")
    return uni


def confirmation(uni: University) -> dict:
    """Whether a person has checked this pack, and the notice to show if not."""
    return {"confirmed": uni.release, "notice": None if uni.release else UNCONFIRMED_NOTICE}


def summary(uni: University) -> dict:
    return {
        "id": uni.university,
        "name": uni.name,
        "city": uni.city,
        "academic_year": uni.academic_year,
        "programmes": len(uni.programmes),
        **confirmation(uni),
    }


def summaries() -> list[dict]:
    """Every university, A to Z, with its application fee and where its applications stand today."""
    today = _today()
    return [_card(uni, today) for uni in sorted(all_packs().values(), key=lambda u: u.name)]


def _card(uni: University, today: date) -> dict:
    apps = uni.applications
    w = browse.application_headline(uni, today)
    return {
        **summary(uni),
        "fee_cents": apps.fee_cents if apps else None,
        "applications": None if w is None else {
            "intake": w.intake, "status": w.status, "label": w.label,
            "opens": w.opens.isoformat() if w.opens else None,
            "closes": w.closes.isoformat() if w.closes else None,
            "days": w.days, "lines": w.lines,
        },
    }


def programme_list(*, q: str | None = None, university: str | None = None, page: int = 1) -> dict:
    """Every programme we hold, by university and faculty, searchable by name or faculty, a page at a time;
    one university's all at once (its faculty sections need the whole set). No marks: minimum points are
    shown as each university publishes them."""
    least = load_config()["colleges"]["min_query_chars"]
    if q is not None and len(q.strip()) < least:
        raise ApiValidationError("Please check the highlighted fields.",
                                 errors=[{"q": [f"Type at least {least} letters or numbers."]}])
    packs = all_packs()
    if university is not None and university not in packs:
        raise NotFoundError("We don't have that university.", code="UNIVERSITY_NOT_FOUND")
    rows = browse.programmes(packs, query=q.strip() if q else None, university=university)
    size = max(1, len(rows)) if university else load_config()["browse"]["page_size"]
    return {
        "summary": browse.summary(rows),
        "total": len(rows),
        "page": page,
        "pages": max(1, math.ceil(len(rows) / size)),
        "programmes": [
            {"university": r.university, "university_name": r.university_name, "programme": r.programme,
             "name": r.name, "faculty": r.faculty, "fields": r.fields, "min_points": r.min_points,
             "selective": r.selective, "verified": r.verified}
            for r in rows[(page - 1) * size: page * size]
        ],
    }


def deadlines() -> dict:
    """What closes soonest across universities and funders, on today's date in South Africa."""
    today = _today()
    found = browse.deadlines(all_packs(), funding_cards(funding.pack(), today), today)
    return {
        "today": today.isoformat(),
        "deadlines": [
            {"kind": d.kind, "id": d.id, "name": d.name, "status": d.status, "label": d.label,
             "closes": d.closes.isoformat(), "days": d.days, "line": d.line}
            for d in found
        ],
    }


def detail(university_id: str) -> dict:
    """The whole pack: programmes, requirements, routes and sources, as the pack says them."""
    uni = get(university_id)
    data = uni.model_dump(mode="json", exclude={"university", "release"})
    return {"id": uni.university, **data, **confirmation(uni)}


def _today() -> date:
    """Today in South Africa, or a preview's test date (src/shared/clock)."""
    return today_sast()


def first_steps(university_id: str) -> dict:
    """From accepting an offer to the first lecture, on today's date: for this year's intake while
    it's still under way, and next year's."""
    uni = get(university_id)
    today = _today()
    return {
        "university": summary(uni),
        "today": today.isoformat(),
        "first_steps": [_first_steps(fs) for fs in build_first_steps(uni, today, funding.pack())],
    }


def _first_steps(fs: FirstSteps) -> dict:
    return {
        "intake": fs.intake,
        "notes": fs.notes,
        "steps": [
            {
                "key": s.key,
                "title": s.title,
                "status": s.status,
                "label": s.label,
                "starts": s.starts.isoformat() if s.starts else None,
                "ends": s.ends.isoformat() if s.ends else None,
                "days": s.days,
                "lines": s.lines,
                "source_urls": s.source_urls,
            }
            for s in fs.steps
        ],
    }
