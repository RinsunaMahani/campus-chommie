"""
My marks end to end: modules and assessments, where the student stands, the
average they need for their target and the projected final mark, all from
the engine. Then the hostile side: odd numbers (true, text, NaN, a
400-digit integer), weights past 100%, unknown fields, and another
student's marks, which are the same 404 as marks that don't exist.
"""
from __future__ import annotations

import uuid

import pytest
from student_helpers import personas, student

from src.domains.student.academics.services import academics_service
from src.shared.rate_limit.limiter import limiter

MARKS = "/api/v1/academics/modules"


@pytest.fixture
def me(client, outbox):
    return student(client, outbox, "naledi@example.com")


@pytest.fixture
def other(client, outbox):
    return student(client, outbox, "sipho@example.com")


def add_module(client, who, **body):
    r = client.post(MARKS, json={"code": "ANA201", "name": "Anatomy", "target": 60} | body, headers=who.headers)
    assert r.status_code == 201, r.get_json()
    return r.get_json()["data"]["module"]


def add_assessment(client, who, module_id, **body):
    r = client.post(f"{MARKS}/{module_id}/assessments", json=body, headers=who.headers)
    assert r.status_code == 201, r.get_json()
    return r.get_json()["data"]["module"]


@pytest.mark.parametrize(
    "method, path",
    [
        ("get", ""), ("post", ""), ("put", f"/{uuid.uuid4()}"), ("delete", f"/{uuid.uuid4()}"),
        ("post", f"/{uuid.uuid4()}/assessments"), ("put", f"/{uuid.uuid4()}/assessments/{uuid.uuid4()}"),
        ("delete", f"/{uuid.uuid4()}/assessments/{uuid.uuid4()}"),
    ],
)
def test_every_marks_route_needs_a_token(client, method, path):
    assert getattr(client, method)(f"{MARKS}{path}", json={}).status_code == 401


def test_a_module_before_any_assessments(client, me):
    module = add_module(client, me, code="ana201")
    assert (module["code"], module["target"], module["standing"], module["projection"]) == ("ANA201", 60, None, None)
    assert module["lines"] == [academics_service.NO_ASSESSMENTS]
    default = client.post(MARKS, json={"code": "PHY 121"}, headers=me.headers).get_json()["data"]["module"]
    assert (default["code"], default["name"], default["target"]) == ("PHY 121", None, 50)  # the usual pass mark
    listed = client.get(MARKS, headers=me.headers).get_json()["data"]["modules"]
    assert [m["code"] for m in listed] == ["ANA201", "PHY 121"]


def test_the_personas_marks_give_the_engines_numbers(client, me):
    """Naledi's ANA201 (fictional): 64% on a 20% test and 71% on a 10% assignment, aiming for 60%."""
    _, people = personas()
    plan = people["naledi"]["modules"][0]
    module = add_module(client, me, code=plan["code"], name=plan["name"], target=plan["target"])
    for a in plan["assessments"]:
        module = add_assessment(client, me, module["id"], **a)
    s, p = module["standing"], module["projection"]
    assert module["total_weight"] == 100
    assert s["status"] == "possible"
    assert s["current"] == 66.3  # (20 x 64 + 10 x 71) / 30
    assert s["needed"] == 57.3  # (60 x 100 - 1990) / 70
    assert (s["completed_weight"], s["remaining_weight"]) == (30, 70)
    assert s["message"] == "You need an average of 57.3% on the remaining 70% of the mark to reach 60%."
    assert p["projected"] == 66.3 and p["based_on"] == 2 and p["below_target"] is False
    assert p["low"] < p["projected"] < p["high"]
    assert module["lines"] == [s["message"], p["message"]]


def test_weights_short_of_100_count_the_rest_as_still_to_come(client, me):
    module = add_module(client, me)
    module = add_assessment(client, me, module["id"], name="Test 1", weight=20, mark=64)
    assert module["total_weight"] == 20
    assert module["lines"][0] == "The weights you've entered add up to 20%. The other 80% counts as still to come until you add it."
    # 60 x 100 - 20 x 64 = 4720 still to earn, on the other 80%.
    assert module["standing"]["needed"] == 59.0 and module["standing"]["remaining_weight"] == 80


def test_a_finished_module_and_one_out_of_reach(client, me):
    done = add_module(client, me, code="BCH111", target=50)
    done = add_assessment(client, me, done["id"], name="Tests", weight=40, mark=70)
    done = add_assessment(client, me, done["id"], name="Exam", weight=60, mark=45)
    assert done["standing"]["status"] == "final" and done["standing"]["current"] == 55.0
    assert done["projection"]["message"] == "This module is complete: 55.0%."

    hard = add_module(client, me, code="PHY121", target=75)
    hard = add_assessment(client, me, hard["id"], name="Test 1", weight=50, mark=20)
    assert hard["standing"]["status"] == "out_of_reach"
    assert "at risk" not in " ".join(hard["lines"]).lower()


def test_weights_can_never_pass_100(client, me):
    module = add_module(client, me)
    module = add_assessment(client, me, module["id"], name="Test 1", weight=60)
    r = client.post(f"{MARKS}/{module['id']}/assessments", json={"name": "Exam", "weight": 50}, headers=me.headers)
    assert r.status_code == 422
    assert r.get_json()["errors"][0]["weight"] == ["The weights would add up to 110%: they can't pass 100%."]
    # Replacing an assessment counts the others only.
    test1 = module["assessments"][0]["id"]
    r = client.put(f"{MARKS}/{module['id']}/assessments/{test1}", json={"name": "Test 1", "weight": 100, "mark": 55}, headers=me.headers)
    assert r.status_code == 200 and r.get_json()["data"]["module"]["standing"]["status"] == "final"


def test_editing_and_deleting(client, me):
    module = add_module(client, me)
    module = add_assessment(client, me, module["id"], name="Test 1", weight=20)
    aid = module["assessments"][0]["id"]
    r = client.put(f"{MARKS}/{module['id']}/assessments/{aid}", json={"name": "  Test   1 ", "weight": 25, "mark": 80}, headers=me.headers)
    changed = r.get_json()["data"]["module"]["assessments"][0]
    assert (changed["name"], changed["weight"], changed["mark"]) == ("Test 1", 25, 80)

    r = client.put(f"{MARKS}/{module['id']}", json={"code": "ANA 201", "name": "Anatomy II", "target": 65}, headers=me.headers)
    assert r.status_code == 200 and r.get_json()["data"]["module"]["code"] == "ANA 201"

    r = client.delete(f"{MARKS}/{module['id']}/assessments/{aid}", headers=me.headers)
    assert r.status_code == 200 and r.get_json()["data"]["module"]["assessments"] == []
    assert client.delete(f"{MARKS}/{module['id']}", headers=me.headers).status_code == 200
    assert client.get(MARKS, headers=me.headers).get_json()["data"]["modules"] == []


def test_deleting_a_module_takes_its_marks_with_it(client, me):
    # Found by our pen test (scripts/security/pentest_local.py): this was a 500.
    module = add_module(client, me)
    add_assessment(client, me, module["id"], name="Test 1", weight=20, mark=70)
    add_assessment(client, me, module["id"], name="Test 2", weight=30)
    assert client.delete(f"{MARKS}/{module['id']}", headers=me.headers).status_code == 200
    assert client.get(MARKS, headers=me.headers).get_json()["data"]["modules"] == []
    again = add_module(client, me)
    assert again["assessments"] == []


def test_a_module_code_is_once_per_student(client, me, other):
    first = add_module(client, me, code="ANA201")
    r = client.post(MARKS, json={"code": "ana201"}, headers=me.headers)
    assert r.status_code == 422 and r.get_json()["errors"][0]["code"] == ["You already have ANA201."]
    second = add_module(client, me, code="PHY121")
    assert client.put(f"{MARKS}/{second['id']}", json={"code": "ANA201"}, headers=me.headers).status_code == 422
    assert client.put(f"{MARKS}/{first['id']}", json={"code": "ANA201", "target": 70}, headers=me.headers).status_code == 200
    add_module(client, other, code="ANA201")  # another student's ANA201 is theirs


def test_limits_on_modules_and_assessments(client, me, monkeypatch):
    monkeypatch.setattr(academics_service, "MAX_MODULES", 2)
    monkeypatch.setattr(academics_service, "MAX_ASSESSMENTS", 2)
    module = add_module(client, me, code="ANA201")
    add_module(client, me, code="PHY121")
    r = client.post(MARKS, json={"code": "BCH111"}, headers=me.headers)
    assert r.status_code == 422 and "modules" in r.get_json()["errors"][0]
    add_assessment(client, me, module["id"], name="Test 1", weight=10)
    add_assessment(client, me, module["id"], name="Test 2", weight=10)
    r = client.post(f"{MARKS}/{module['id']}/assessments", json={"name": "Test 3", "weight": 10}, headers=me.headers)
    assert r.status_code == 422 and "assessments" in r.get_json()["errors"][0]


# ------------------------------------------------------------- hostile


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"code": ""},
        {"code": "A"},
        {"code": "ANA201; DROP TABLE"},
        {"code": "<script>"},
        {"code": "-ANA201"},
        {"code": "A" * 17},
        {"code": 201},
        {"code": "ANA201", "target": 101},
        {"code": "ANA201", "target": -1},
        {"code": "ANA201", "target": "60"},
        {"code": "ANA201", "target": True},
        {"code": "ANA201", "target": 10**400},
        {"code": "ANA201", "name": "   "},
        {"code": "ANA201", "name": "x" * 81},
        {"code": "ANA201", "user_id": str(uuid.uuid4())},
        {"code": "ANA201", "student_number": "u12345678"},
    ],
)
def test_odd_modules_are_refused(client, me, body):
    assert client.post(MARKS, json=body, headers=me.headers).status_code == 422


@pytest.mark.parametrize(
    "body",
    [
        {"name": "Test 1"},
        {"name": "Test 1", "weight": 0},
        {"name": "Test 1", "weight": 100.5},
        {"name": "Test 1", "weight": "20"},
        {"name": "Test 1", "weight": False},
        {"name": "Test 1", "weight": 20, "mark": 101},
        {"name": "Test 1", "weight": 20, "mark": -0.5},
        {"name": "Test 1", "weight": 20, "mark": "64%"},
        {"name": "Test 1", "weight": 20, "mark": True},
        {"name": "", "weight": 20},
        {"name": " ", "weight": 20},
        {"weight": 20},
        {"name": "Test 1", "weight": 20, "module_id": str(uuid.uuid4())},
    ],
)
def test_odd_assessments_are_refused(client, me, body):
    module = add_module(client, me)
    assert client.post(f"{MARKS}/{module['id']}/assessments", json=body, headers=me.headers).status_code == 422


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity", "1e400"])
def test_special_numbers_are_refused(client, me, value):
    module = add_module(client, me)
    raw = '{"name": "Test 1", "weight": 20, "mark": ' + value + "}"
    r = client.post(f"{MARKS}/{module['id']}/assessments", data=raw, content_type="application/json", headers=me.headers)
    assert r.status_code in (400, 422)


def test_odd_queries_and_bodies_are_refused(client, me):
    assert client.get(f"{MARKS}?user_id=1", headers=me.headers).status_code == 422
    assert client.post(MARKS, data="not json", content_type="application/json", headers=me.headers).status_code == 422
    assert client.post(MARKS, json=["ANA201"], headers=me.headers).status_code == 422


def test_another_students_marks_are_not_found(client, me, other):
    module = add_module(client, me)
    module = add_assessment(client, me, module["id"], name="Test 1", weight=20, mark=64)
    aid = module["assessments"][0]["id"]
    body = {"name": "Test 1", "weight": 20, "mark": 0}

    r = client.put(f"{MARKS}/{module['id']}", json={"code": "HACK101"}, headers=other.headers)
    assert r.status_code == 404 and r.get_json()["code"] == "MODULE_NOT_FOUND"
    assert client.delete(f"{MARKS}/{module['id']}", headers=other.headers).status_code == 404
    assert client.post(f"{MARKS}/{module['id']}/assessments", json=body, headers=other.headers).status_code == 404
    assert client.put(f"{MARKS}/{module['id']}/assessments/{aid}", json=body, headers=other.headers).status_code == 404
    assert client.delete(f"{MARKS}/{module['id']}/assessments/{aid}", headers=other.headers).status_code == 404
    assert client.get(MARKS, headers=other.headers).get_json()["data"]["modules"] == []
    # An assessment reached through another module of their own is no different.
    theirs = add_module(client, other, code="STK210")
    r = client.put(f"{MARKS}/{theirs['id']}/assessments/{aid}", json=body, headers=other.headers)
    assert r.status_code == 404 and r.get_json()["code"] == "ASSESSMENT_NOT_FOUND"
    # ...and nothing of mine changed.
    mine = client.get(MARKS, headers=me.headers).get_json()["data"]["modules"]
    assert [(m["code"], m["assessments"][0]["mark"]) for m in mine] == [("ANA201", 64)]


def test_an_unknown_id_is_the_same_404(client, me):
    assert client.delete(f"{MARKS}/{uuid.uuid4()}", headers=me.headers).status_code == 404
    module = add_module(client, me)
    assert client.delete(f"{MARKS}/{module['id']}/assessments/{uuid.uuid4()}", headers=me.headers).status_code == 404
    assert client.delete(f"{MARKS}/not-a-uuid", headers=me.headers).status_code == 404


def test_changes_are_limited_per_student(client, me, other, app):
    limiter.enabled = True
    with app.app_context():
        limiter.reset()
    try:
        codes = [client.put(f"{MARKS}/{uuid.uuid4()}", json={"code": "ANA201"}, headers=me.headers).status_code for _ in range(61)]
        assert codes[:60] == [404] * 60 and codes[60] == 429
        assert client.post(MARKS, json={"code": "STK210"}, headers=other.headers).status_code == 201
    finally:
        with app.app_context():
            limiter.reset()
        limiter.enabled = False
