"""A campus on a map: its outline, the buildings and named places inside it, and where campus
support is, when a support service names a building the map knows.

Everything comes from OpenStreetMap (backend/data/maps/), plus names a person added on campus.
A building nobody has named stays unnamed: the map shows its shape and never guesses what it is.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .schemas import CampusMap, LatLon, Place, Street, University, UniversityMap
from .text import plural

#: The credit OpenStreetMap asks for wherever its data is shown, linking to its copyright page.
ATTRIBUTION = "© OpenStreetMap contributors"
ATTRIBUTION_URL = "https://www.openstreetmap.org/copyright"
#: The licence the data stays under, our copy included: named and linked wherever it goes out as data.
LICENCE = "Open Database License (ODbL) 1.0"
LICENCE_URL = "https://opendatacommons.org/licenses/odbl/1-0/"
#: How far past the outline the map shows when it has streets (degrees, about 120 m), so the roads that lead in
#: are on it.
STREET_MARGIN = 0.0011


@dataclass
class SupportPlace:
    """A support service whose contact names a building on this campus's map."""

    kind: str
    name: str
    place_id: str


@dataclass
class CampusView:
    campus: str
    name: str  # from the university's pack
    mapped: bool
    outline: list[list[LatLon]] = field(default_factory=list)
    south_west: LatLon | None = None
    north_east: LatLon | None = None
    centre: LatLon | None = None
    places: list[Place] = field(default_factory=list)
    streets: list[Street] = field(default_factory=list)
    support: list[SupportPlace] = field(default_factory=list)
    lines: list[str] = field(default_factory=list)
    source_url: str | None = None


def _support(campus: CampusMap, uni: University) -> list[SupportPlace]:
    """Support services on this campus whose contact names a building on the map ("Clinpath Building,
    room 3L003"). Only whole names, at least two words long, so "Block" alone never matches."""
    named = [p for p in campus.places if p.name and len(p.name.split()) >= 2]
    found: list[SupportPlace] = []
    for service in uni.support_services:
        if service.campuses and campus.campus not in service.campuses:
            continue
        text = service.contact.lower()
        place = next((p for p in named if p.name.lower() in text), None)
        if place:
            found.append(SupportPlace(service.kind, service.name, place.id))
    return found


def campus_view(uni: University, umap: UniversityMap | None, campus_id: str) -> CampusView:
    """One campus as the map screen needs it, with plain-words lines about what's known."""
    campus_name = next((c.name for c in uni.campuses if c.id == campus_id), campus_id)
    campus = umap.campus(campus_id) if umap else None
    if campus is None:
        return CampusView(campus_id, campus_name, False, lines=[f"{campus_name} isn't mapped yet."])
    south_west, north_east = campus.bounds
    if campus.streets:
        m = STREET_MARGIN
        south_west, north_east = (south_west[0] - m, south_west[1] - m), (north_east[0] + m, north_east[1] + m)
    centre = ((south_west[0] + north_east[0]) / 2, (south_west[1] + north_east[1]) / 2)
    named = [p for p in campus.places if p.name]
    by_person = [p for p in named if p.name_source]
    source = umap.source(campus.source)
    lines = [_count_line(len(campus.places), len(named))]
    if not named:
        lines.append("None of its buildings has a name yet, so the map shows their shapes only.")
    elif len(named) < len(campus.places):
        lines.append("Buildings without a name show as shapes only: we never guess what they are.")
    if by_person:
        lines.append(f"{plural(len(by_person), 'name')} added by the team on campus.")
    return CampusView(
        campus_id, campus_name, True, list(campus.outline), south_west, north_east, centre, list(campus.places),
        list(campus.streets), _support(campus, uni), lines, source.url if source else None,
    )


def _count_line(total: int, named: int) -> str:
    places = "1 building or place" if total == 1 else f"{total} buildings and places"
    return f"{places} from OpenStreetMap, {named} with a name."


def university_views(uni: University, umap: UniversityMap | None) -> list[CampusView]:
    """Every campus in the university's pack, in its order: mapped ones in full, the rest said to be not mapped yet."""
    return [campus_view(uni, umap, c.id) for c in uni.campuses]
