"""
A university's campus maps for the map screen. Services call the engine; routes never do.

Every campus in the university's pack is listed, in the pack's order: mapped ones with their
outline, places and support on the map; the rest said to be not mapped yet. A map nobody has
checked is still served, with `confirmed: false` and the notice the app shows next to it.
"""
from __future__ import annotations

from campus_engine.maps import ATTRIBUTION, ATTRIBUTION_URL, LICENCE, LICENCE_URL, CampusView, university_views
from campus_engine.text import read_from
from src.core.exceptions import NotFoundError
from src.domains.catalogue.universities.services import university_service as catalogue

from ..repositories.map_repository import all_maps


def university_map(university_id: str, campus: str | None = None) -> dict:
    uni = catalogue.get(university_id)  # an unknown university is the catalogue's 404
    umap = all_maps().get(uni.university)
    views = university_views(uni, umap)
    if campus is not None:
        views = [v for v in views if v.campus == campus]
        if not views:
            raise NotFoundError("That university has no such campus.", code="CAMPUS_NOT_FOUND")
    confirmed = bool(umap and umap.release)
    return {
        "university": catalogue.summary(uni),
        "campuses": [_campus(v) for v in views],
        "attribution": ATTRIBUTION,
        "attribution_url": ATTRIBUTION_URL,
        "licence": LICENCE,
        "licence_url": LICENCE_URL,
        "confirmed": confirmed,
        # Where the map comes from and when it was fetched; the campus names come from the university's pack.
        "notice": None if confirmed else read_from("OpenStreetMap", [s.retrieved for s in (umap.sources if umap else [])]),
    }


def _campus(v: CampusView) -> dict:
    return {
        "id": v.campus,
        "name": v.name,
        "mapped": v.mapped,
        "south_west": v.south_west,
        "north_east": v.north_east,
        "centre": v.centre,
        "outline": v.outline,
        "places": [
            {
                "id": p.id,
                "name": p.name,
                "kind": p.kind,
                "centre": p.centre,
                "outline": p.outline,
                "named_by_team": p.name_source is not None,
            }
            for p in v.places
        ],
        # Roads around the campus and paths across it, drawn under the buildings.
        "streets": [{"kind": s.kind, "name": s.name, "line": s.line} for s in v.streets],
        "support": [{"kind": s.kind, "name": s.name, "place": s.place_id} for s in v.support],
        "lines": v.lines,
        "source_url": v.source_url,
    }
