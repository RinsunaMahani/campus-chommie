"""Fetch campus maps from OpenStreetMap into backend/data/maps/<university>.yaml.

For each campus in data/maps/osm_campuses.yaml: its outline, the buildings inside it, the named
places (a library, a clinic, a cafe) marked as points, and the streets: roads within about 120 m of the
outline and the footpaths across it. Names a person added on campus come from
data/maps/names/<university>.yaml and win over OpenStreetMap's.

The data is (c) OpenStreetMap contributors, under the Open Database License (ODbL) 1.0: the app
shows the credit, and our copy, with the names a person added, stays under the ODbL
(docs/research/maps.md). Every file this writes is an agent draft (release: false) until a person
has checked it.

Usage: python scripts/fetch_osm_maps.py [university ...]   (all of them when none is named)
       python scripts/fetch_osm_maps.py --names-only smu    (names/smu.yaml onto the map we have, offline)
Fetching needs the network; tests use the parsing and naming functions on saved answers.
"""
from __future__ import annotations

import argparse
import http.client
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MAPS_DIR = ROOT / "data" / "maps"
ENDPOINTS = (
    "https://overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
)
USER_AGENT = "CampusChommie/0.1 (student hackathon project; campus maps from OpenStreetMap)"
#: Roads a student walks or drives in by; paths across the campus. Motorways and tracks aren't ways in.
ROADS = ("trunk", "primary", "secondary", "tertiary", "unclassified", "residential", "living_street", "service")
PATHS = ("pedestrian", "footway", "path", "steps")
#: How far past the outline roads are fetched (metres): the ones that lead in.
ROAD_RADIUS = 120
POINT_AMENITIES = (
    "library", "clinic", "doctors", "pharmacy", "cafe", "restaurant", "fast_food", "food_court", "bank", "atm",
    "post_office", "police", "place_of_worship", "parking", "bus_station", "toilets",
)


def place_kind(tags: dict) -> str:
    """A rough kind for the app's icon, from OpenStreetMap's tags. The name says what it is."""
    amenity, building, leisure = tags.get("amenity", ""), tags.get("building", ""), tags.get("leisure", "")
    name = tags.get("name", "").lower()
    if amenity == "library" or building == "library" or "library" in name:
        return "library"
    if amenity in ("clinic", "doctors", "hospital", "pharmacy") or building == "hospital" or tags.get("healthcare"):
        return "health"
    if amenity in ("cafe", "restaurant", "fast_food", "food_court"):
        return "food"
    if amenity in ("parking", "bus_station") or building in ("parking", "garage", "garages"):
        return "parking"
    if leisure in ("sports_centre", "stadium", "sports_hall", "fitness_centre") or building in ("sports_hall", "stadium"):
        return "sport"
    if building in ("dormitory", "residential", "apartments", "house") or "residence" in name or " res" in f" {name}":
        return "residence"
    if amenity in ("bank", "atm", "post_office", "police", "toilets", "place_of_worship"):
        return "services"
    if "admin" in name:
        return "admin"
    if building in ("university", "college", "school") or tags.get("amenity") in ("university", "college"):
        return "academic"
    return "other"


def _point(node: dict) -> list[float]:
    return [round(node["lat"], 6), round(node["lon"], 6)]


def _ring(geometry: list[dict]) -> list[list[float]]:
    ring = [_point(n) for n in geometry]
    if len(ring) > 1 and ring[0] == ring[-1]:
        ring = ring[:-1]  # the closing point repeats the first
    return ring


def _centre(ring: list[list[float]]) -> list[float]:
    return [round(sum(p[0] for p in ring) / len(ring), 6), round(sum(p[1] for p in ring) / len(ring), 6)]


def campus_query(elements: list[str]) -> str:
    """One Overpass query: the campus outline with its geometry, then the buildings and named points inside."""
    ways = [e.split("/")[1] for e in elements if e.startswith("way/")]
    rels = [e.split("/")[1] for e in elements if e.startswith("relation/")]
    select = "".join([f"way(id:{','.join(ways)});" if ways else "", f"rel(id:{','.join(rels)});" if rels else ""])
    amenities = "|".join(POINT_AMENITIES)
    return (
        "[out:json][timeout:120];"
        f"({select})->.campus;"
        ".campus out geom;"
        ".campus map_to_area->.a;"
        '(way["building"](area.a);)->.buildings;'
        ".buildings out tags geom;"
        f'(node["amenity"~"^({amenities})$"]["name"](area.a);)->.points;'
        ".points out body;"  # body: a node's tags and its position
        f'(way(around.campus:{ROAD_RADIUS})["highway"~"^({"|".join(ROADS)})$"];'
        f'way["highway"~"^({"|".join(PATHS)})$"](area.a);)->.streets;'
        ".streets out tags geom;"
    )


def street_of(el: dict) -> dict | None:
    """A road or path from an Overpass way, or None for anything else."""
    tags = el.get("tags", {})
    highway = tags.get("highway", "")
    if el.get("type") != "way" or highway not in ROADS + PATHS or len(el.get("geometry") or []) < 2:
        return None
    street = {"kind": "road" if highway in ROADS else "path", "line": [_point(n) for n in el["geometry"]]}
    if tags.get("name"):
        street["name"] = tags["name"].strip()
    return street


def parse_streets(answer: dict) -> list[dict]:
    """The roads and paths in an Overpass answer: roads first, then by name, so the file diffs stay small."""
    found = [s for el in answer.get("elements", []) if (s := street_of(el))]
    return sorted(found, key=lambda s: (s["kind"] != "road", s.get("name") or "~", s["line"][0]))


def parse_campus(answer: dict, elements: list[str]) -> tuple[list[list[list[float]]], list[dict]]:
    """The campus outline (one or more rings) and its places, from an Overpass answer."""
    wanted = {(e.split("/")[0], int(e.split("/")[1])) for e in elements}
    rings: list[list[list[float]]] = []
    places: list[dict] = []
    for el in answer.get("elements", []):
        key = (el["type"], el["id"])
        if key in wanted:
            if el["type"] == "way" and el.get("geometry"):
                rings.append(_ring(el["geometry"]))
            for member in el.get("members", []):  # a relation: its outer ways
                if member.get("role") in ("outer", "") and member.get("geometry"):
                    rings.append(_ring(member["geometry"]))
            continue
        tags = el.get("tags", {})
        if tags.get("highway"):
            continue  # a street: parse_streets takes it
        if el["type"] == "way" and el.get("geometry"):
            ring = _ring(el["geometry"])
            if len(ring) < 3:
                continue
            place = {"id": f"w{el['id']}", "kind": place_kind(tags), "centre": _centre(ring), "outline": ring}
        elif el["type"] == "node" and tags.get("name") and "lat" in el:
            place = {"id": f"n{el['id']}", "kind": place_kind(tags), "centre": _point(el)}
        else:
            continue
        if tags.get("name"):
            place["name"] = tags["name"].strip()
        places.append(place)
    return [r for r in rings if len(r) >= 3], _sorted(places)


def _sorted(places: list[dict]) -> list[dict]:
    """Named places first, by name, then the rest by id: the order the map screen lists them in."""
    return sorted(places, key=lambda p: (p.get("name") is None, (p.get("name") or "").lower(), p["id"]))


def apply_names(places: list[dict], names: dict, source: str) -> int:
    """Names a person added on campus, by place id; they win over OpenStreetMap's. Returns how many applied."""
    applied = 0
    for place in places:
        entry = names.get(place["id"])
        if entry:
            place["name"] = entry["name"]
            place["kind"] = entry.get("kind", place["kind"])
            place["name_source"] = source
            applied += 1
    return applied


def _fetch(query: str) -> dict:
    body = urllib.parse.urlencode({"data": query}).encode()
    last = None
    for _attempt in range(2):
        for endpoint in ENDPOINTS:
            request = urllib.request.Request(endpoint, data=body, headers={"User-Agent": USER_AGENT})
            try:
                # Bandit B310 (file:// and other schemes): the ENDPOINTS above are fixed https addresses.
                with urllib.request.urlopen(request, timeout=150) as response:  # nosec B310
                    return json.loads(response.read())
            # OSError covers URLError, timeouts and a server that hangs up (RemoteDisconnected); HTTPException a
            # half-sent answer. Any of them: try the next server.
            except (OSError, http.client.HTTPException, json.JSONDecodeError) as exc:
                last = f"{endpoint}: {exc}"
                time.sleep(10)  # a busy instance: give it a moment
    raise RuntimeError(f"every Overpass instance failed; last: {last}")


def _flow(value) -> str:
    """JSON is valid YAML: one line per place keeps the files readable and diffs small."""
    return json.dumps(value, ensure_ascii=False)


def header(university: str) -> list[str]:
    """The notice each map file starts with: the credit, and the licence it stays under (ODbL 4.2)."""
    return [
        f"# Campus maps for {university}, from OpenStreetMap: (c) OpenStreetMap contributors, under the ODbL",
        "# (Open Database License 1.0: https://opendatacommons.org/licenses/odbl/1-0/; the credit and terms:",
        "# https://www.openstreetmap.org/copyright). This file, with the names a person added on campus",
        "# (names/<university>.yaml), stays under the ODbL. Written by scripts/fetch_osm_maps.py; an agent",
        "# draft until a person has checked it.",
    ]


def write_map(university: str, campuses: list[dict], sources: list[dict], path: Path) -> None:
    lines = [
        *header(university),
        "",
        f"university: {university}",
        "release: false",
        "",
        "campuses:",
    ]
    for c in campuses:
        lines += [f"  - campus: {c['campus']}", f"    source: {c['source']}", f"    outline: {_flow(c['outline'])}"]
        if c["places"]:
            lines.append("    places:")
            lines += [f"      - {_flow(p)}" for p in c["places"]]
        else:
            lines.append("    places: []")
        if c.get("streets"):
            lines.append("    streets:")
            lines += [f"      - {_flow(s)}" for s in c["streets"]]
    lines += ["", "sources:"]
    for s in sources:
        lines.append(f"  - id: {s['id']}")
        for key in ("url", "publisher", "title"):
            lines.append(f"    {key}: {_flow(s[key])}")
        checked = s.get("last_verified")
        lines += [
            f"    retrieved: {s['retrieved']}",
            f"    last_verified: {checked if checked else 'null'}",
            f"    verified_by: {_flow(s['verified_by'])}",
        ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def _previous(path: Path) -> tuple[dict, dict]:
    """The campuses and sources of the map file we're about to replace, to keep when a fetch fails."""
    if not path.exists():
        return {}, {}
    old = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {c["campus"]: c for c in old.get("campuses", [])}, {s["id"]: s for s in old.get("sources", [])}


def _names(university: str) -> dict:
    """Names a person added on campus, by campus and place id, with their source."""
    path = MAPS_DIR / "names" / f"{university}.yaml"
    return (yaml.safe_load(path.read_text(encoding="utf-8")) or {}) if path.exists() else {}


def _with_names_source(sources: list[dict], names: dict) -> list[dict]:
    """The sources, then the person who named places (and when they checked them), once."""
    if not names.get("source"):
        return sources
    return [s for s in sources if s["id"] != names["source"]["id"]] + [names["source"]]


def name_university(university: str, path: Path | None = None, names: dict | None = None) -> int:
    """Apply names/<university>.yaml to the map file we already have, without fetching again (Overpass
    is often busy). Returns how many places it named."""
    path = path or MAPS_DIR / f"{university}.yaml"
    names = _names(university) if names is None else names
    current = yaml.safe_load(path.read_text(encoding="utf-8"))
    applied = 0
    for campus in current["campuses"]:
        named = names.get("campuses", {}).get(campus["campus"], {})
        if named:
            applied += apply_names(campus["places"], named, names["source"]["id"])
            campus["places"] = _sorted(campus["places"])
    write_map(university, current["campuses"], _with_names_source(current["sources"], names), path)
    return applied


def fetch_university(university: str, config: dict, today: date) -> None:
    names = _names(university)
    old_campuses, old_sources = _previous(MAPS_DIR / f"{university}.yaml")
    campuses: list[dict] = []
    sources: list[dict] = []
    for campus_id, entry in config.items():
        elements = entry["osm"]
        try:
            answer = _fetch(campus_query(elements))
        except RuntimeError as exc:
            kept = old_campuses.get(campus_id)
            print(f"{university}/{campus_id}: fetch failed ({exc}); {'kept the last copy' if kept else 'skipped'}",
                  file=sys.stderr)
            if kept:
                campuses.append(kept)
                sources.append({k: v for k, v in old_sources[kept["source"]].items()})
            continue
        rings, places = parse_campus(answer, elements)
        streets = parse_streets(answer)
        if not rings:
            print(f"{university}/{campus_id}: no outline came back; skipped", file=sys.stderr)
            continue
        source_id = f"s-osm-{university}-{campus_id.replace('_', '-')}"
        named = names.get("campuses", {}).get(campus_id, {})
        if named:
            apply_names(places, named, names["source"]["id"])
        campuses.append({"campus": campus_id, "source": source_id, "outline": rings, "places": places, "streets": streets})
        sources.append({
            "id": source_id,
            "url": f"https://www.openstreetmap.org/{elements[0]}",
            "publisher": "OpenStreetMap contributors",
            "title": f"{entry['name']}: campus outline, buildings, named places and streets (ODbL)",
            "retrieved": today.isoformat(),
            "verified_by": "agent draft, needs human check",
        })
        print(f"{university}/{campus_id}: {len(places)} places, {sum(1 for p in places if p.get('name'))} named, "
              f"{len(streets)} streets")
        time.sleep(3)  # Overpass is shared
    write_map(university, campuses, _with_names_source(sources, names), MAPS_DIR / f"{university}.yaml")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch campus maps from OpenStreetMap.")
    parser.add_argument("universities", nargs="*")
    parser.add_argument("--names-only", action="store_true", help="apply names/<university>.yaml to the maps we have, offline")
    args = parser.parse_args(argv)
    config = yaml.safe_load((MAPS_DIR / "osm_campuses.yaml").read_text(encoding="utf-8"))
    for university in args.universities or list(config):
        if args.names_only:
            print(f"{university}: {name_university(university)} places named")
        else:
            fetch_university(university, config[university], date.today())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
