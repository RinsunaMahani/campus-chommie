"""
Reading OpenStreetMap's answers into a map file, offline: a saved answer stands in for Overpass.
The fetch itself (scripts/fetch_osm_maps.py) needs the network and isn't run here.
"""
from __future__ import annotations

from datetime import date

from campus_engine.catalogue import load_map
from scripts.fetch_osm_maps import apply_names, campus_query, name_university, parse_campus, place_kind, write_map


def node(lat: float, lon: float) -> dict:
    return {"lat": lat, "lon": lon}


SQUARE = [node(-25.75, 28.22), node(-25.75, 28.23), node(-25.76, 28.23), node(-25.76, 28.22), node(-25.75, 28.22)]
BUILDING = [node(-25.7551, 28.2251), node(-25.7551, 28.2253), node(-25.7553, 28.2253), node(-25.7553, 28.2251),
            node(-25.7551, 28.2251)]
ANSWER = {
    "elements": [
        {"type": "way", "id": 10, "tags": {"amenity": "university"}, "geometry": SQUARE},
        {"type": "way", "id": 11, "tags": {"building": "university", "name": "Aula"}, "geometry": BUILDING},
        {"type": "way", "id": 12, "tags": {"building": "yes"}, "geometry": BUILDING},
        {"type": "way", "id": 13, "tags": {"building": "yes"}, "geometry": BUILDING[:2]},  # not a shape: skipped
        {"type": "node", "id": 14, "lat": -25.756, "lon": 28.226, "tags": {"amenity": "cafe", "name": "Coffee Shop"}},
        {"type": "node", "id": 15, "tags": {"amenity": "cafe", "name": "No position"}},  # skipped
    ]
}


def test_the_query_asks_for_the_outline_its_buildings_and_named_points():
    q = campus_query(["way/10", "way/20", "relation/30"])
    assert "way(id:10,20);" in q and "rel(id:30);" in q
    assert 'way["building"](area.a)' in q and ".points out body;" in q


def test_an_answer_becomes_an_outline_and_places_named_first():
    rings, places = parse_campus(ANSWER, ["way/10"])
    assert rings == [[[-25.75, 28.22], [-25.75, 28.23], [-25.76, 28.23], [-25.76, 28.22]]]  # the closing point dropped
    assert [(p["id"], p.get("name"), p["kind"]) for p in places] == [
        ("w11", "Aula", "academic"), ("n14", "Coffee Shop", "food"), ("w12", None, "other"),
    ]
    aula = places[0]
    assert aula["centre"] == [-25.7552, 28.2252] and len(aula["outline"]) == 4
    assert "outline" not in places[1]  # a point


def test_a_relation_brings_its_outer_ways():
    relation = {"type": "relation", "id": 30, "tags": {"type": "multipolygon"},
                "members": [{"type": "way", "role": "outer", "geometry": SQUARE},
                            {"type": "way", "role": "inner", "geometry": BUILDING}]}
    rings, _ = parse_campus({"elements": [relation]}, ["relation/30"])
    assert len(rings) == 1  # the courtyard (inner) isn't part of the outline


def test_kinds_from_openstreetmap_tags():
    assert place_kind({"amenity": "library"}) == "library"
    assert place_kind({"building": "yes", "name": "Merensky Library"}) == "library"
    assert place_kind({"amenity": "clinic"}) == "health"
    assert place_kind({"building": "dormitory"}) == "residence"
    assert place_kind({"building": "yes", "name": "Kollege Residence"}) == "residence"
    assert place_kind({"leisure": "sports_centre"}) == "sport"
    assert place_kind({"amenity": "parking"}) == "parking"
    assert place_kind({"amenity": "atm"}) == "services"
    assert place_kind({"building": "yes", "name": "Administration Building"}) == "admin"
    assert place_kind({"building": "yes"}) == "other"


def test_names_from_campus_win_and_say_who_gave_them():
    _, places = parse_campus(ANSWER, ["way/10"])
    applied = apply_names(places, {"w12": {"name": "Clinpath Building", "kind": "health"}}, "s-person")
    named = next(p for p in places if p["id"] == "w12")
    assert applied == 1 and (named["name"], named["kind"], named["name_source"]) == ("Clinpath Building", "health", "s-person")


def test_a_written_map_loads_and_keeps_the_credit(tmp_path):
    rings, places = parse_campus(ANSWER, ["way/10"])
    path = tmp_path / "ex.yaml"
    source = {"id": "s-osm-ex-main", "url": "https://www.openstreetmap.org/way/10", "publisher": "OpenStreetMap contributors",
              "title": "Example: campus outline (ODbL)", "retrieved": date(2026, 10, 12).isoformat(),
              "verified_by": "agent draft, needs human check"}
    write_map("ex", [{"campus": "main", "source": "s-osm-ex-main", "outline": rings, "places": places}], [source], path)
    text = path.read_text(encoding="utf-8")
    assert "(c) OpenStreetMap contributors, under the ODbL" in text
    assert "https://opendatacommons.org/licenses/odbl/1-0/" in text  # the licence travels with the data
    m = load_map(path)
    assert m.release is False and m.campus("main").places[0].name == "Aula"
    assert m.source("s-osm-ex-main").last_verified is None


def test_names_go_onto_the_map_we_have_without_fetching_again(tmp_path):
    rings, places = parse_campus(ANSWER, ["way/10"])
    path = tmp_path / "ex.yaml"
    osm = {"id": "s-osm-ex-main", "url": "https://www.openstreetmap.org/way/10", "publisher": "OpenStreetMap contributors",
           "title": "Example: campus outline (ODbL)", "retrieved": "2026-10-12", "verified_by": "agent draft, needs human check"}
    write_map("ex", [{"campus": "main", "source": osm["id"], "outline": rings, "places": places}], [osm], path)
    person = {"id": "s-ex-names", "url": "https://www.openstreetmap.org/way/10", "publisher": "A student, on campus",
              "title": "Example: building names read on campus", "retrieved": "2026-10-13", "last_verified": "2026-10-13",
              "verified_by": "A student"}
    names = {"source": person, "campuses": {"main": {"w12": {"name": "Clinpath Building", "kind": "health"}}}}

    assert name_university("ex", path, names) == 1
    m = load_map(path)
    assert [p.name for p in m.campus("main").places] == ["Aula", "Clinpath Building", "Coffee Shop"]  # named first, by name
    assert m.campus("main").places[1].name_source == "s-ex-names"
    assert name_university("ex", path, names) == 1  # again: the same answer
    assert [s.id for s in load_map(path).sources] == ["s-osm-ex-main", "s-ex-names"]  # the person's source once
