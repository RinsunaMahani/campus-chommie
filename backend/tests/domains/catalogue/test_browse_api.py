"""
The course finder's tabs: every programme (no marks), what closes soonest, each university's fee and
application status, and how to apply without marks. Public, read-only, strict, never touching the
database or logging a search, and limited per IP.
"""
from __future__ import annotations

import logging
from datetime import date

import pytest
from sqlalchemy import event

from src.domains.catalogue.universities.services import university_service
from src.domains.pathways.course_finder.services import course_finder_service
from src.extensions import db
from src.shared.rate_limit.limiter import limiter


@pytest.fixture
def on_20_october(monkeypatch):
    monkeypatch.setattr(university_service, "_today", lambda: date(2026, 10, 20))
    monkeypatch.setattr(course_finder_service, "_today", lambda: date(2026, 10, 20))


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


def test_the_university_list_carries_fee_and_application_status(client, on_20_october):
    unis = {u["id"]: u for u in client.get("/api/v1/universities").get_json()["data"]["universities"]}
    uj = unis["uj"]
    assert uj["applications"]["closes"] == "2026-10-31" and uj["applications"]["days"] == 11
    assert "fee_cents" in uj
    assert all(set(u) >= {"id", "name", "city", "fee_cents", "applications"} for u in unis.values())


def test_programmes_page_through_every_university(client):
    data = client.get("/api/v1/programmes").get_json()["data"]
    assert data["total"] > 1000 and data["page"] == 1 and len(data["programmes"]) == 50
    assert data["summary"].endswith("universities.")
    first = data["programmes"][0]
    assert set(first) == {"university", "university_name", "programme", "name", "faculty", "fields",
                          "min_points", "selective", "verified"}


def test_programmes_narrow_to_one_university_and_a_search(client):
    up = client.get("/api/v1/programmes", query_string={"university": "up"}).get_json()["data"]
    assert up["programmes"] and all(p["university"] == "up" for p in up["programmes"])
    found = client.get("/api/v1/programmes", query_string={"q": "nursing"}).get_json()["data"]
    assert found["total"] > 0
    assert client.get("/api/v1/programmes", query_string={"university": "hogwarts"}).status_code == 404


def test_deadlines_nearest_first(client, on_20_october):
    data = client.get("/api/v1/deadlines").get_json()["data"]
    assert data["today"] == "2026-10-20"
    closes = [d["closes"] for d in data["deadlines"]]
    assert closes == sorted(closes) and {d["kind"] for d in data["deadlines"]} == {"university", "funding"}


def test_how_to_apply_needs_no_marks(client, on_20_october):
    data = client.get("/api/v1/pathways/apply/uj").get_json()["data"]
    assert data["university"]["id"] == "uj" and data["apply"]["today"] == "2026-10-20"
    assert data["apply"]["guide"]["windows"]
    assert client.get("/api/v1/pathways/apply/hogwarts").status_code == 404


@pytest.mark.parametrize("query", [
    {"include": "secrets"}, {"q": ""}, {"q": "ab"}, {"q": "x" * 121}, {"q": "a\nb c"},
    {"university": "UP"}, {"university": "u"}, {"university": "../up"}, {"page": "0"}, {"page": "201"}, {"page": "x"},
])
def test_odd_programme_searches_are_refused(client, query):
    assert client.get("/api/v1/programmes", query_string=query).status_code == 422


def test_odd_queries_elsewhere_are_refused(client):
    assert client.get("/api/v1/programmes?q=nursing&q=law").status_code == 422
    assert client.get("/api/v1/deadlines", query_string={"x": "1"}).status_code == 422
    assert client.get("/api/v1/pathways/apply/uj", query_string={"marks": "80"}).status_code == 422


def test_browsing_never_touches_the_database_or_logs_a_search(app, client, caplog):
    with app.app_context():
        engine = db.engine
    statements: list[str] = []

    def record(conn, cursor, statement, *args):
        statements.append(statement)

    event.listen(engine, "before_cursor_execute", record)
    caplog.set_level(logging.DEBUG)
    try:
        assert client.get("/api/v1/programmes", query_string={"q": "zebrasearch"}).status_code == 200
        assert client.get("/api/v1/deadlines").status_code == 200
        assert client.get("/api/v1/universities").status_code == 200
        assert client.get("/api/v1/pathways/apply/up").status_code == 200
    finally:
        event.remove(engine, "before_cursor_execute", record)
    assert statements == [] and "zebrasearch" not in caplog.text


def test_browsing_is_limited_per_ip(client, limits_on):
    for path in ("/api/v1/programmes", "/api/v1/deadlines", "/api/v1/pathways/apply/up"):
        codes = [client.get(path).status_code for _ in range(121)]
        assert codes[:120] == [200] * 120 and codes[120] == 429
