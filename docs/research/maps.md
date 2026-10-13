# Campus maps: research notes

Agent draft, 12 and 13 Oct 2026. Campus maps are a scope change Rinsuna made on 12 Oct 2026: the brief had an
interactive map on the roadmap only. She chose OpenStreetMap for the data, buildings as well as campus outlines, and
to name SMU's buildings herself on campus. Nobody has checked the map files yet (`release: false`).

## Where the data comes from

- **OpenStreetMap** (openstreetmap.org), the map anyone can edit. `backend/scripts/fetch_osm_maps.py` reads it
  through the Overpass API, trying three public servers in turn. For each campus in
  `backend/data/maps/osm_campuses.yaml` it takes:
  - the campus outline: the OpenStreetMap way or relation that marks the campus (two for a campus in two parts)
  - every building inside the outline, with its shape
  - named points inside it, such as a library, a clinic, a cafe or an ATM (the list is in the script)
- **Kinds** (`academic`, `library`, `health`, `residence` and so on) come from OpenStreetMap's tags and, failing
  those, from a word in the name ("Library", "Residence"). They only choose an icon: the name says what a place is.
- **Names a person reads on campus** go in `backend/data/maps/names/<university>.yaml` and win over OpenStreetMap's.
  `python scripts/fetch_osm_maps.py --names-only smu` puts them on the map we have, without fetching again. The
  file's shape:

  ```yaml
  source:                       # the person who read the names, and when
    id: s-smu-names
    url: https://www.openstreetmap.org/way/86253741
    publisher: <who read them>, on campus
    title: "SMU Ga-Rankuwa: building names read on campus"
    retrieved: <date>
    last_verified: <date>
    verified_by: <who read them>
  campuses:
    ga_rankuwa:
      w123: {name: <the name on the building>, kind: academic}   # w123: the place's id on the map
  ```

- **Nothing is guessed.** A building without a name in OpenStreetMap is drawn as a shape only, and the app says so.

## The licence: what OpenStreetMap asks of us

OpenStreetMap's data is © OpenStreetMap contributors, under the Open Data Commons Open Database License (ODbL) 1.0.
We read its [copyright page](https://www.openstreetmap.org/copyright) and
[the licence](https://opendatacommons.org/licenses/odbl/1-0/) on 13 Oct 2026. For us that means:

- **Credit wherever the map is shown:** "© OpenStreetMap contributors", linking to the copyright page. The API sends
  both with every map (`attribution`, `attribution_url`).
- **Name and link the licence when the data goes out as data:** the copyright page asks this of anyone "distributing
  OSM in data form". The API sends `licence` and `licence_url`, and every map file starts with the same notice
  (ODbL 4.2).
- **Share-alike:** "If you alter or build upon our data, you may distribute the result only under the same license"
  (ODbL 4.4). Our map files, with the names we add, are such a result: they stay under the ODbL, never "all rights
  reserved" like the rest of the repository. REUSE.md lists them with the other third-party material.
- **A copy for anyone who uses it** (ODbL 4.6): the public API serves every campus map in full, machine-readable and
  free of charge, and `fetch_osm_maps.py` is the method that made it.
- **South African sources:** OpenStreetMap's copyright page says its data includes data "sourced from Chief
  Directorate: National Geo-Spatial Information, State copyright reserved". OpenStreetMap's own credit covers it.

The names Rinsuna reads on campus could also go into OpenStreetMap itself, so every map gains them. That's her call.

## What's mapped (13 Oct 2026)

| University | Campus | Buildings and places | With a name | Outline in OpenStreetMap |
|---|---|---|---|---|
| UP | Hatfield | 151 | 96 | [relation 17478004](https://www.openstreetmap.org/relation/17478004) |
| UP | Groenkloof | 38 | 30 | [way 433978067](https://www.openstreetmap.org/way/433978067) (fetched on 12 Oct; busy servers on 13 Oct) |
| UP | Prinshof | 19 | 3 | [way 1010238957](https://www.openstreetmap.org/way/1010238957) and [way 1098735040](https://www.openstreetmap.org/way/1098735040) |
| UP | Onderstepoort | 2 | 0 | [way 427085320](https://www.openstreetmap.org/way/427085320) and [way 236250989](https://www.openstreetmap.org/way/236250989): OpenStreetMap has only these 2 buildings mapped there (checked 13 Oct) |
| UP | Mamelodi | 22 | 18 | [way 1009606676](https://www.openstreetmap.org/way/1009606676) |
| TUT | Pretoria | 118 | 20 | [way 63131200](https://www.openstreetmap.org/way/63131200) |
| TUT | Arts | 25 | 0 | [way 435671653](https://www.openstreetmap.org/way/435671653) |
| TUT | Arcadia | 9 | 0 | [way 723941347](https://www.openstreetmap.org/way/723941347) |
| TUT | Ga-Rankuwa | 0 | 0 | [way 293217287](https://www.openstreetmap.org/way/293217287): the outline only, since OpenStreetMap has no buildings mapped there (checked 13 Oct) |
| TUT | Soshanguve South | 8 | 2 | [way 413120107](https://www.openstreetmap.org/way/413120107) (fetched on 12 Oct; busy servers on 13 Oct) |
| SMU | Ga-Rankuwa | 281 | 6 | [way 86253741](https://www.openstreetmap.org/way/86253741): the six names are all sewage works, so the buildings wait for Rinsuna's names |

**No outline in OpenStreetMap, so not mapped:** UP Hillcrest and GIBS (Sandton); TUT Soshanguve North, eMalahleni,
Mbombela and Polokwane. A person could draw an outline in OpenStreetMap, then add it to `osm_campuses.yaml`.

**When the servers are busy:** Overpass's public servers often time out (on 12 and 13 Oct). The script then keeps
that campus's last copy, says so, and can be run again later for the rest.

## The map's background (not chosen yet)

The API gives shapes, and the app can draw them on a plain background with no outside service. A background map with
streets is an outside service, so it's Rinsuna's call (CLAUDE.md, "Ask Rinsuna first"; OPEN_QUESTIONS, "Campus maps"):

- **OpenStreetMap's own tiles** are free, but its [tile usage policy](https://operations.osmfoundation.org/policies/tiles/)
  (read on 13 Oct 2026) says "Availability is best-effort: there is no SLA or guarantee", and that they "may block
  access, without notice". An app must use `https://tile.openstreetmap.org/{z}/{x}/{y}.png`, show the credit on the
  map, send its own User-Agent, cache tiles (at least 7 days) and never download areas ahead or for offline use.
- **A tile service built on OpenStreetMap:** the policy points to "an alternative OSM-derived service". These usually
  need an account and a key.

## Where a student is

The API never asks where a student is: a `near`, or any field but `campus`, is refused (422). A "you are here" dot
would use the phone's own location and keep it on the phone. It needs a location permission and a package the reused
app removed, so it's Rinsuna's call (OPEN_QUESTIONS, "Campus maps").
