"""
Reading OpenStreetMap's answers into a map file, offline: a saved answer stands in for Overpass.
The fetch itself (scripts/fetch_osm_maps.py) needs the network and isn't run here.
"""
from __future__ import annotations

import http.client
import json
from datetime import date

import scripts.fetch_osm_maps as fetcher
from campus_engine.catalogue import load_map
from scripts.fetch_osm_maps import (
    apply_names, campus_query, name_university, parse_campus, parse_streets, place_kind, write_map,
)


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
        {"type": "way", "id": 16, "tags": {"highway": "tertiary", "name": "Lynnwood Road"},
         "geometry": [node(-25.7495, 28.21), node(-25.7495, 28.24)]},
        {"type": "way", "id": 17, "tags": {"highway": "footway"}, "geometry": [node(-25.755, 28.221), node(-25.756, 28.229)]},
        {"type": "way", "id": 18, "tags": {"highway": "motorway"}, "geometry": [node(-25.74, 28.2), node(-25.74, 28.3)]},
        {"type": "way", "id": 19, "tags": {"highway": "service"}, "geometry": [node(-25.751, 28.221)]},  # one point: skipped
    ]
}


def test_the_query_asks_for_the_outline_its_buildings_and_named_points():
    q = campus_query(["way/10", "way/20", "relation/30"])
    assert "way(id:10,20);" in q and "rel(id:30);" in q
    assert 'way["building"](area.a)' in q and ".points out body;" in q
    assert "way(around.campus:120)" in q and ".streets out tags geom;" in q  # the roads that lead in, and the paths


def test_roads_around_and_paths_across_become_streets_never_places():
    streets = parse_streets(ANSWER)
    assert streets == [
        {"kind": "road", "line": [[-25.7495, 28.21], [-25.7495, 28.24]], "name": "Lynnwood Road"},
        {"kind": "path", "line": [[-25.755, 28.221], [-25.756, 28.229]]},
    ]  # a motorway isn't a way in; a one-point way isn't a line
    _, places = parse_campus(ANSWER, ["way/10"])
    assert not [p for p in places if p["id"] in ("w16", "w17")]


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
    streets = parse_streets(ANSWER)
    write_map("ex", [{"campus": "main", "source": "s-osm-ex-main", "outline": rings, "places": places, "streets": streets}],
              [source], path)
    text = path.read_text(encoding="utf-8")
    assert "(c) OpenStreetMap contributors, under the ODbL" in text
    assert "https://opendatacommons.org/licenses/odbl/1-0/" in text  # the licence travels with the data
    m = load_map(path)
    assert m.release is False and m.campus("main").places[0].name == "Aula"
    assert [s.name for s in m.campus("main").streets] == ["Lynnwood Road", None]
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


def test_a_server_that_hangs_up_is_skipped_for_the_next(monkeypatch):
    calls = []

    class Answer:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def read(self):
            return json.dumps({"elements": []}).encode()

    def urlopen(request, timeout):
        calls.append(request.full_url)
        if len(calls) == 1:
            raise http.client.RemoteDisconnected("Remote end closed connection without response")
        return Answer()

    monkeypatch.setattr(fetcher.urllib.request, "urlopen", urlopen)
    monkeypatch.setattr(fetcher.time, "sleep", lambda s: None)
    assert fetcher._fetch("[out:json];") == {"elements": []}
    assert calls == list(fetcher.ENDPOINTS[:2])
