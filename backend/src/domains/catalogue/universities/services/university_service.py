"""
The catalogue's answers. Other features (the course finder) read packs
through here, never through the repository.

A pack nobody has checked yet is still served, with `confirmed: false` and a
notice the app shows next to it.
"""
from __future__ import annotations

from datetime import date

from campus_engine.journey import FirstSteps
from campus_engine.journey import first_steps as build_first_steps
from campus_engine.schemas import University
from campus_engine.text import read_from
from src.core.exceptions import NotFoundError
from src.domains.catalogue.funding.services import funding_service as funding
from src.shared.clock.clock import today_sast

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
    """Pack completeness and accepted source evidence are separate from personal sign-off."""
    name = f"the {uni.name}" if uni.name.startswith("University") else uni.name
    notice = read_from(f"{name}'s own documents", [s.retrieved for s in uni.sources])
    confirmed = uni.release and bool(uni.sources) and all(s.verified for s in uni.sources)
    return {"confirmed": confirmed, "notice": None if confirmed else notice}


#: How a university's type reads, where its own page states it.
TYPE_LABELS = {"university_of_technology": "University of technology", "comprehensive": "Comprehensive university"}


def summary(uni: University) -> dict:
    return {
        "id": uni.university,
        "name": uni.name,
        "city": uni.city,
        "province": uni.province,
        "institution_type": uni.institution_type,
        "institution_type_label": TYPE_LABELS.get(uni.institution_type) if uni.institution_type else None,
        "academic_year": uni.academic_year,
        "programmes": len(uni.programmes),
        **confirmation(uni),
    }


def summaries() -> list[dict]:
    return [summary(uni) for uni in sorted(all_packs().values(), key=lambda u: u.name)]


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
