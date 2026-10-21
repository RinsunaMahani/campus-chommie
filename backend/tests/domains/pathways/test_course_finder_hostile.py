"""
The course finder against someone trying things: odd bodies, impossible marks,
unknown universities and programmes, floods. It must also never keep or log
a mark: learners using it may be under 18 and have no account.
"""
from __future__ import annotations

import logging

import pytest
from course_finder_helpers import ASSESS, PLAN, STRONG, marks
from sqlalchemy import event

from src.extensions import db
from src.shared.rate_limit.limiter import limiter

TEN_SUBJECTS = [
    {"subject": s, "percent": 60}
    for s in (
        "english", "mathematics", "physical_sciences", "life_sciences", "life_orientation",
        "geography", "history", "accounting", "economics", "business_studies",
    )
]


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


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"university": "smu"},
        {"university": "smu", "marks": []},
        {"university": "smu", "marks": TEN_SUBJECTS},
        {"university": "smu", "marks": marks(english=-1)},
        {"university": "smu", "marks": marks(english=101)},
        {"university": "smu", "marks": marks(english="seventy")},
        {"university": "smu", "marks": marks(english=True)},
        {"university": "smu", "marks": marks(english=None)},
        {"university": "smu", "marks": [{"subject": "maths", "percent": 70}]},
        {"university": "smu", "marks": [{"subject": 7, "percent": 70}]},
        {"university": "smu", "marks": [{"subject": "english", "percent": 70}, {"subject": "english", "percent": 80}]},
        {"university": "smu", "marks": [{"subject": "english", "percent": 70, "id_number": "0001015009087"}]},
        {"university": "smu", "marks": STRONG, "id_number": "0001015009087"},
        {"university": "smu", "marks": {"english": 70}},
        {"university": ["smu"], "marks": STRONG},
        {"university": "", "marks": STRONG},
        {"university": "x" * 41, "marks": STRONG},
    ],
)
def test_odd_bodies_are_refused(client, body):
    assert client.post(ASSESS, json=body).status_code == 422


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity"])
def test_special_numbers_are_refused(client, value):
    raw = '{"university": "smu", "marks": [{"subject": "english", "percent": ' + value + "}]}"
    assert client.post(ASSESS, data=raw, content_type="application/json").status_code == 422


def test_a_plan_needs_a_goal(client):
    assert client.post(PLAN, json={"university": "smu", "marks": STRONG}).status_code == 422


def test_unknown_university_or_programme_is_a_404(client):
    r = client.post(ASSESS, json={"university": "hogwarts", "marks": STRONG})
    assert r.status_code == 404 and r.get_json()["code"] == "UNIVERSITY_NOT_FOUND"
    r = client.post(PLAN, json={"university": "hogwarts", "goal": "mbchb", "marks": STRONG})
    assert r.status_code == 404 and r.get_json()["code"] == "UNIVERSITY_NOT_FOUND"
    r = client.post(PLAN, json={"university": "smu", "goal": "potions", "marks": STRONG})
    assert r.status_code == 404 and r.get_json()["code"] == "PROGRAMME_NOT_FOUND"


def test_not_json_is_refused(client):
    assert client.post(ASSESS, data="english=80", content_type="application/x-www-form-urlencoded").status_code == 422


def test_huge_and_deep_bodies_are_refused(client):
    huge = '{"university": "smu", "marks": [], "x": "' + "a" * (1024 * 1024 + 10) + '"}'
    assert client.post(ASSESS, data=huge, content_type="application/json").status_code == 413
    deep: dict = {}
    node = deep
    for _ in range(200):
        node["x"] = {}
        node = node["x"]
    assert client.post(ASSESS, json=deep).status_code in (400, 422)


def test_a_refusal_never_repeats_the_mark(client):
    r = client.post(ASSESS, json={"university": "smu", "marks": marks(english=101.37)})
    assert r.status_code == 422 and "101.37" not in r.get_data(as_text=True)


def test_marks_are_never_logged(client, caplog):
    caplog.set_level(logging.DEBUG)
    rows = marks(english=73.37, mathematics=81.29)
    client.post(ASSESS, json={"university": "smu", "marks": rows})
    client.post(PLAN, json={"university": "smu", "goal": "mbchb", "marks": rows})
    client.post(ASSESS, json={"university": "smu", "marks": marks(english=173.37)})  # a refusal too
    assert "73.37" not in caplog.text and "81.29" not in caplog.text


def test_the_course_finder_never_touches_the_database(app, client):
    with app.app_context():
        engine = db.engine
    statements: list[str] = []

    def record(conn, cursor, statement, *args):
        statements.append(statement)

    event.listen(engine, "before_cursor_execute", record)
    try:
        assert client.post(ASSESS, json={"university": "smu", "marks": STRONG}).status_code == 200
        assert client.post(PLAN, json={"university": "smu", "goal": "mbchb", "marks": STRONG}).status_code == 200
        assert client.post(ASSESS, json={"university": "smu", "marks": []}).status_code == 422
    finally:
        event.remove(engine, "before_cursor_execute", record)
    assert statements == []


def test_the_course_finder_is_limited_per_ip(client, limits_on):
    body = {"university": "smu", "marks": STRONG}
    codes = [client.post(ASSESS, json=body).status_code for _ in range(121)]
    assert codes[:120] == [200] * 120 and codes[120] == 429
    r = client.post(PLAN, json=dict(body, goal="mbchb"))
    assert r.status_code == 200  # each endpoint keeps its own count
