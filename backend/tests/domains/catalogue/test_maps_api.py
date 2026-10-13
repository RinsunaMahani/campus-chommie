"""
Campus maps over the API: public and read-only, every campus in the pack's order (the ones not
mapped yet said so), the credit OpenStreetMap's licence asks for, and odd requests refused.
"""
from __future__ import annotations

import re

import pytest
from sqlalchemy import event

from src.extensions import db
from src.shared.rate_limit.limiter import limiter

API = "/api/v1/universities"


@pytest.fixture
def limits_on(app):
    was = limiter.enabled
    limiter.enabled = True
    with app.app_context():
        limiter.reset()
    yield
    with app.app_context():
        limiter.reset()
    limiter.enabled = was


def test_smus_map_needs_no_account(client):
    r = client.get(f"{API}/smu/map")
    assert r.status_code == 200
    data = r.get_json()["data"]
    assert data["university"]["id"] == "smu"
    assert (data["attribution"], data["attribution_url"]) == ("© OpenStreetMap contributors", "https://www.openstreetmap.org/copyright")
    assert (data["licence"], data["licence_url"]) == ("Open Database License (ODbL) 1.0", "https://opendatacommons.org/licenses/odbl/1-0/")
    assert (data["confirmed"], data["notice"]) == (False, "Not yet confirmed by the team.")
    (campus,) = data["campuses"]
    assert (campus["id"], campus["name"], campus["mapped"]) == ("ga_rankuwa", "Ga-Rankuwa (Molotlegi Street)", True)
    south, west = campus["south_west"]
    north, east = campus["north_east"]
    assert south < north and west < east and len(campus["outline"]) >= 1
    assert campus["source_url"] == "https://www.openstreetmap.org/way/86253741"
    building = campus["places"][0]
    assert set(building) == {"id", "name", "kind", "centre", "outline", "named_by_team"}
    assert re.fullmatch(r"\d+ buildings and places from OpenStreetMap, \d+ with a name\.", campus["lines"][0])


def test_every_campus_is_listed_and_the_unmapped_ones_say_so(client):
    campuses = client.get(f"{API}/up/map").get_json()["data"]["campuses"]
    assert [c["id"] for c in campuses] == ["hatfield", "groenkloof", "hillcrest", "mamelodi", "onderstepoort", "prinshof", "gibs"]
    gibs = next(c for c in campuses if c["id"] == "gibs")
    assert (gibs["mapped"], gibs["places"], gibs["lines"]) == (False, [], ["GIBS (Sandton, Johannesburg) isn't mapped yet."])
    assert next(c for c in campuses if c["id"] == "mamelodi")["mapped"] is True


def test_one_campus_at_a_time(client):
    data = client.get(f"{API}/tut/map", query_string={"campus": "pretoria"}).get_json()["data"]
    assert [c["id"] for c in data["campuses"]] == ["pretoria"]


def test_unknown_universities_and_campuses_are_404s(client):
    r = client.get(f"{API}/hogwarts/map")
    assert r.status_code == 404 and r.get_json()["code"] == "UNIVERSITY_NOT_FOUND"
    r = client.get(f"{API}/smu/map", query_string={"campus": "atlantis"})
    assert r.status_code == 404 and r.get_json()["code"] == "CAMPUS_NOT_FOUND"


@pytest.mark.parametrize(
    "query",
    [
        {"campus": ""},
        {"campus": "Ga_Rankuwa"},
        {"campus": "ga-rankuwa"},
        {"campus": "x" * 41},
        {"campus": "ga_rankuwa' OR 1=1"},
        {"zoom": "15"},
        {"near": "-25.6,28.0"},  # nothing about where the person is
    ],
)
def test_odd_queries_are_refused(client, query):
    assert client.get(f"{API}/smu/map", query_string=query).status_code == 422


def test_a_campus_given_twice_is_refused(client):
    assert client.get(f"{API}/smu/map?campus=ga_rankuwa&campus=ga_rankuwa").status_code == 422


def test_the_map_never_touches_the_database(app, client):
    with app.app_context():
        engine = db.engine
    statements: list[str] = []

    def record(conn, cursor, statement, *args):
        statements.append(statement)

    event.listen(engine, "before_cursor_execute", record)
    try:
        assert client.get(f"{API}/smu/map").status_code == 200
        assert client.get(f"{API}/hogwarts/map").status_code == 404
        assert client.get(f"{API}/smu/map", query_string={"zoom": "1"}).status_code == 422
    finally:
        event.remove(engine, "before_cursor_execute", record)
    assert statements == []


def test_the_map_is_limited_per_ip(client, limits_on):
    codes = [client.get(f"{API}/smu/map").status_code for _ in range(121)]
    assert codes[:120] == [200] * 120 and codes[120] == 429
