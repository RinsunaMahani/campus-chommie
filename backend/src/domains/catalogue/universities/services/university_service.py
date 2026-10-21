"""
The catalogue's answers. Other features (the course finder) read packs
through here, never through the repository.

A pack nobody has checked yet is still served, with `confirmed: false` and a
notice the app shows next to it.
"""
from __future__ import annotations

from campus_engine.schemas import University
from src.core.exceptions import NotFoundError

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
    return [summary(uni) for uni in sorted(all_packs().values(), key=lambda u: u.name)]


def detail(university_id: str) -> dict:
    """The whole pack: programmes, requirements, routes and sources, as the pack says them."""
    uni = get(university_id)
    data = uni.model_dump(mode="json", exclude={"university", "release"})
    return {"id": uni.university, **data, **confirmation(uni)}
