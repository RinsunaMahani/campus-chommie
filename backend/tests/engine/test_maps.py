"""
Campus maps: what a map file may hold, a campus as the map screen sees it, and where campus
support is on it. Made-up campuses, so the rules are tested apart from the shipped maps (the last
tests check those load and sit where the campuses are).
"""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from campus_engine.catalogue import load_catalogue, load_maps
from campus_engine.maps import ATTRIBUTION, ATTRIBUTION_URL, LICENCE, LICENCE_URL, campus_view, university_views
from campus_engine.schemas import University, UniversityMap

SQUARE = [[-25.75, 28.22], [-25.75, 28.23], [-25.76, 28.23], [-25.76, 28.22]]
SOURCE = {"id": "s-osm", "url": "https://www.openstreetmap.org/way/1", "publisher": "OpenStreetMap contributors"}


def place(pid: str, name: str | None = None, **extra) -> dict:
    out = {"id": pid, "kind": "academic", "centre": [-25.755, 28.225],
           "outline": [[-25.7551, 28.2251], [-25.7551, 28.2252], [-25.7552, 28.2252]]}
    if name:
        out["name"] = name
    return out | extra


def umap(*places: dict, **extra) -> dict:
    base = {
        "university": "ex",
        "campuses": [{"campus": "main", "source": "s-osm", "outline": [SQUARE], "places": list(places)}],
        "sources": [SOURCE],
    }
    return base | extra


def university(**extra) -> University:
    return University.model_validate({
        "university": "ex", "name": "Example University", "city": "Pretoria", "academic_year": 2027,
        "campuses": [
            {"id": "main", "name": "Main", "source": "s"},
            {"id": "far", "name": "Far Away", "source": "s"},
        ],
        "sources": [{"id": "s", "url": "https://example.org", "publisher": "Example"}],
    } | extra)


# ------------------------------------------------------------------ the map's rules


def test_a_place_cites_known_sources_and_has_an_openstreetmap_id():
    with pytest.raises(ValidationError, match="campus 'main' cites unknown source 'missing'"):
        UniversityMap.model_validate(umap(campuses=[{"campus": "main", "source": "missing", "outline": [SQUARE]}]))
    with pytest.raises(ValidationError, match="main/w1 name cites unknown source 's-person'"):
        UniversityMap.model_validate(umap(place("w1", "Library", name_source="s-person")))
    with pytest.raises(ValidationError):
        UniversityMap.model_validate(umap(place("building-1")))
    with pytest.raises(ValidationError, match="place ids must be unique"):
        UniversityMap.model_validate(umap(place("w1"), place("w1")))


def test_points_stay_on_the_campus_and_in_south_africa():
    with pytest.raises(ValidationError, match="main/w1: its centre lies outside the campus"):
        UniversityMap.model_validate(umap(place("w1", centre=[-25.80, 28.30])))
    with pytest.raises(ValidationError, match="a point lies outside South Africa"):
        UniversityMap.model_validate(umap(place("w1", centre=[51.5, -0.12])))
    with pytest.raises(ValidationError):
        UniversityMap.model_validate(umap(campuses=[{"campus": "main", "source": "s-osm", "outline": [SQUARE[:2]]}]))


def test_a_campus_is_mapped_once():
    twice = umap()
    twice["campuses"] = twice["campuses"] * 2
    with pytest.raises(ValidationError, match="campus ids must be unique"):
        UniversityMap.model_validate(twice)


# ------------------------------------------------------------ a campus on the map


def test_a_campus_with_its_shape_bounds_and_places():
    m = UniversityMap.model_validate(umap(place("w1", "Library"), place("w2"), place("n3", "Cafe", kind="food", outline=[])))
    v = campus_view(university(), m, "main")
    assert (v.campus, v.name, v.mapped) == ("main", "Main", True)
    assert (v.south_west, v.north_east) == ((-25.76, 28.22), (-25.75, 28.23))
    assert v.centre == pytest.approx((-25.755, 28.225))
    assert [p.id for p in v.places] == ["w1", "w2", "n3"]
    assert v.lines == [
        "3 buildings and places from OpenStreetMap, 2 with a name.",
        "Buildings without a name show as shapes only: we never guess what they are.",
    ]
    assert v.source_url == "https://www.openstreetmap.org/way/1"


def test_streets_widen_the_map_so_the_roads_that_lead_in_show():
    road = {"kind": "road", "name": "Lynnwood Road", "line": [[-25.7495, 28.21], [-25.7495, 28.24]]}
    m = UniversityMap.model_validate(umap(place("w1", "Library")) | {
        "campuses": [{"campus": "main", "source": "s-osm", "outline": [SQUARE], "places": [place("w1", "Library")],
                      "streets": [road, {"kind": "path", "line": [[-25.755, 28.221], [-25.756, 28.229]]}]}],
    })
    v = campus_view(university(), m, "main")
    assert [(s.kind, s.name) for s in v.streets] == [("road", "Lynnwood Road"), ("path", None)]
    assert v.south_west == pytest.approx((-25.7611, 28.2189)) and v.north_east == pytest.approx((-25.7489, 28.2311))


def test_a_street_is_a_line_in_south_africa():
    with pytest.raises(ValidationError):
        UniversityMap.model_validate(umap() | {"campuses": [{"campus": "main", "source": "s-osm", "outline": [SQUARE],
                                                             "streets": [{"kind": "road", "line": [[-25.75, 28.22]]}]}]})
    with pytest.raises(ValidationError, match="outside South Africa"):
        UniversityMap.model_validate(umap() | {"campuses": [{"campus": "main", "source": "s-osm", "outline": [SQUARE],
                                                             "streets": [{"kind": "road", "line": [[-25.75, 28.22], [51.5, -0.1]]}]}]})
    with pytest.raises(ValidationError):
        UniversityMap.model_validate(umap() | {"campuses": [{"campus": "main", "source": "s-osm", "outline": [SQUARE],
                                                             "streets": [{"kind": "highway", "line": [[-25.75, 28.22], [-25.75, 28.23]]}]}]})


def test_a_campus_whose_buildings_have_no_names_says_so():
    v = campus_view(university(), UniversityMap.model_validate(umap(place("w1"), place("w2"))), "main")
    assert v.lines == [
        "2 buildings and places from OpenStreetMap, 0 with a name.",
        "None of its buildings has a name yet, so the map shows their shapes only.",
    ]


def test_names_the_team_added_on_campus_are_counted():
    person = {"id": "s-person", "url": "https://www.openstreetmap.org/way/2", "publisher": "Rinsuna Mahani, on campus"}
    m = UniversityMap.model_validate(umap(place("w1", "Clinpath Building", name_source="s-person"), sources=[SOURCE, person]))
    assert campus_view(university(), m, "main").lines[-1] == "1 name added by the team on campus."


def test_a_campus_not_mapped_yet_says_so():
    v = campus_view(university(), UniversityMap.model_validate(umap()), "far")
    assert (v.mapped, v.places, v.lines) == (False, [], ["Far Away isn't mapped yet."])
    assert campus_view(university(), None, "main").mapped is False  # a university with no map file


def test_every_campus_in_the_packs_order():
    views = university_views(university(), UniversityMap.model_validate(umap()))
    assert [(v.campus, v.mapped) for v in views] == [("main", True), ("far", False)]


def test_support_shows_on_the_map_when_its_contact_names_a_building():
    uni = university(support_services=[
        {"kind": "counselling", "name": "Counselling", "contact": "012 000 0000; Clinpath Building, room 3L003", "source": "s"},
        {"kind": "health", "name": "Clinic", "contact": "012 000 0001; Block A", "source": "s"},  # one word: never matched
        {"kind": "tutoring", "name": "Tutors", "contact": "Clinpath Building", "campuses": ["far"], "source": "s"},
    ])
    m = UniversityMap.model_validate(umap(place("w1", "Clinpath Building"), place("w2", "Block")))
    (found,) = campus_view(uni, m, "main").support
    assert (found.kind, found.name, found.place_id) == ("counselling", "Counselling", "w1")


def test_the_credit_and_the_licence_openstreetmap_asks_for():
    assert (ATTRIBUTION, ATTRIBUTION_URL) == ("© OpenStreetMap contributors", "https://www.openstreetmap.org/copyright")
    assert (LICENCE, LICENCE_URL) == ("Open Database License (ODbL) 1.0", "https://opendatacommons.org/licenses/odbl/1-0/")


# ---------------------------------------------------------------- the shipped maps


def test_the_shipped_maps_load_and_name_only_campuses_we_have():
    maps, catalogue = load_maps(), load_catalogue()
    assert {"up", "tut", "smu"} <= set(maps) <= set(catalogue)  # more universities as their maps are fetched
    for uni, m in maps.items():
        campus_ids = {c.id for c in catalogue[uni].campuses}
        assert {c.campus for c in m.campuses} <= campus_ids
        assert m.release is False  # an agent draft until a person checks it
        assert all(s.publisher == "OpenStreetMap contributors" for s in m.sources if s.id.startswith("s-osm-"))


def test_smu_is_mapped_where_ga_rankuwa_is():
    smu = load_maps()["smu"].campus("ga_rankuwa")
    (south, west), (north, east) = smu.bounds
    assert -25.63 < south < north < -25.60 and 28.00 < west < east < 28.04  # Ga-Rankuwa, north-west of Pretoria
    assert len(smu.places) > 50
