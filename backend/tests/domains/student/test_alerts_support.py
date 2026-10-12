"""
Alerts and support (F5) on the personas' date. Home's alerts come from the
student's own week, money and marks, each ending in things to do that lead
somewhere real: a screen, or their campus's own support service. The
Support screen lists every kind of support the brief names for the
student's campus, says "Not verified yet" where the pack has none, and holds
crisis lines back until a person has checked them. The cheap-things list is
the student's campus's own.
"""
from __future__ import annotations

from datetime import date

import pytest
from student_helpers import DEMO_TODAY, fresh_password, on_day, seed_demo, sign_in_demo, student

from src.domains.catalogue.universities.services import university_service
from src.domains.student.alerts import constants
from src.domains.student.money.services import money_service

API = "/api/v1"


@pytest.fixture(autouse=True)
def on_12_october(monkeypatch):
    on_day(monkeypatch, DEMO_TODAY)


@pytest.fixture
def me(client, outbox):
    return student(client, outbox, "lerato@example.com")


@pytest.fixture
def demo(app):
    password = fresh_password()
    seed_demo(app, password)
    return password


def get(client, headers, path):
    r = client.get(f"{API}{path}", headers=headers)
    assert r.status_code == 200, r.get_json()
    return r.get_json()["data"]


def place(client, who, university, campus):
    r = client.put(f"{API}/me/profile", json={"university": university, "campus": campus}, headers=who.headers)
    assert r.status_code == 200, r.get_json()


@pytest.mark.parametrize("path", ["/alerts", "/support", "/money/cheap-things"])
def test_every_route_needs_a_token(client, path):
    assert client.get(f"{API}{path}").status_code == 401


# ------------------------------------------------------------------ alerts


def test_no_alerts_before_there_is_anything_to_go_on(client, me):
    data = get(client, me.headers, "/alerts")
    assert data == {"today": "2026-10-12", "alerts": [], "notes": [constants.NO_CLASSES, constants.NO_MONEY]}


def test_the_allowance_funded_persona_gets_one_combined_alert(client, demo):
    data = get(client, sign_in_demo(client, "naledi", demo), "/alerts")
    assert [a["kind"] for a in data["alerts"]] == ["combined"] and data["notes"] == []
    alert = data["alerts"][0]
    assert alert["title"] == "Heavy week from Mon 19 Oct, and money running short"
    assert alert["message"].endswith("Your money may run out around Sat 24 Oct, before your next payment lands.")
    targets = [(a["target"], a["support_kind"]) for a in alert["actions"]]
    assert targets == [("money", None), ("week", None), ("support", "financial_aid"), ("support", "counselling")]
    aid, counselling = alert["actions"][2], alert["actions"][3]
    assert aid["service"]["name"] == "Financial Aid Office: fee blocks and financial clearance"
    assert aid["service"]["contact"].startswith("012 521 4614")
    assert counselling["service"]["name"].startswith("Centre for Student Counselling and Development")


def test_the_self_funded_persona_gets_a_heavy_week_alert_with_his_campus_support(client, demo):
    data = get(client, sign_in_demo(client, "sipho", demo), "/alerts")
    assert [a["kind"] for a in data["alerts"]] == ["heavy_week"]
    alert = data["alerts"][0]
    assert alert["title"] == "Heavy week from Mon 12 Oct" and alert["message"].startswith("Heavy:")
    services = {a["support_kind"]: a["service"] for a in alert["actions"] if a["target"] == "support"}
    assert services["tutoring"]["name"] == "Academic success coaches, by faculty"
    assert services["counselling"]["name"] == "Student Counselling Unit"
    assert services["counselling"]["source_url"].startswith("https://")


def test_the_rep_sees_his_classes_heavy_week_too(client, demo):
    data = get(client, sign_in_demo(client, "thabo", demo), "/alerts")
    assert [a["kind"] for a in data["alerts"]] == ["heavy_week"]
    assert data["notes"] == [constants.NO_MONEY]


def test_a_module_out_of_reach_gets_a_gentle_alert(client, me):
    module = client.post(f"{API}/academics/modules", json={"code": "ANA201", "target": 75}, headers=me.headers)
    module_id = module.get_json()["data"]["module"]["id"]
    client.post(f"{API}/academics/modules/{module_id}/assessments", json={"name": "Test 1", "weight": 60, "mark": 40},
                headers=me.headers)
    data = get(client, me.headers, "/alerts")
    alert = data["alerts"][0]
    assert (alert["kind"], alert["title"]) == ("module", "ANA201: your 75% target is out of reach")
    assert {a["support_kind"] for a in alert["actions"]} >= {"tutoring", "counselling"}
    assert "at risk" not in str(data).lower()


def test_alerts_are_the_students_own(client, me, demo):
    """The personas next door have heavy weeks and short money; none of it reaches someone else."""
    assert get(client, me.headers, "/alerts")["alerts"] == []


# ----------------------------------------------------------------- support


def test_support_for_a_campus(client, me):
    place(client, me, "up", "hatfield")
    data = get(client, me.headers, "/support")
    assert (data["university"]["id"], data["campus_name"], data["university"]["confirmed"]) == ("up", "Hatfield", False)
    assert [k["kind"] for k in data["kinds"]] == list(constants.SUPPORT_KINDS) + ["careers", "disability"]
    kinds = {k["kind"]: k for k in data["kinds"]}
    assert kinds["counselling"]["services"][0]["name"] == "Student Counselling Unit"
    assert kinds["counselling"]["line"] is None
    for missing in ("financial_aid", "food_support", "chaplaincy"):
        assert kinds[missing] == {"kind": missing, "services": [], "line": "Not verified yet"}
    # Every crisis line in the pack is still an agent's draft: held back until a person checks it.
    assert kinds["crisis"] == {"kind": "crisis", "services": [], "line": constants.CRISIS_HELD}
    for k in data["kinds"]:
        for s in k["services"]:
            assert s["source_url"].startswith("https://") and s["last_verified"] is None


def test_crisis_lines_show_once_a_person_has_checked_them(client, me, monkeypatch):
    up = university_service.packs()["up"]
    checked = up.model_copy(update={"sources": [
        s.model_copy(update={"verified_by": "Rinsuna Mahani", "last_verified": date(2026, 10, 11)})
        if s.id == "s-up-infoguide-2026" else s
        for s in up.sources
    ]})
    monkeypatch.setattr(university_service, "packs", lambda: {**university_service.all_packs(), "up": checked})
    place(client, me, "up", "hatfield")
    crisis = next(k for k in get(client, me.headers, "/support")["kinds"] if k["kind"] == "crisis")
    assert crisis["line"] is None
    assert crisis["services"][0]["name"] == "UP crisis line (toll-free)"
    assert crisis["services"][0]["last_verified"] == "2026-10-11"


def test_support_and_cheap_things_need_a_campus(client, me):
    data = get(client, me.headers, "/support")
    assert data["kinds"] == [] and data["lines"] == [constants.NO_CAMPUS]
    things = get(client, me.headers, "/money/cheap-things")
    assert things["cheap_things"] == [] and things["lines"] == [money_service.NO_CAMPUS]


# ------------------------------------------------------------ cheap things


def test_cheap_things_near_the_campus(client, me):
    place(client, me, "up", "hatfield")
    data = get(client, me.headers, "/money/cheap-things")
    assert [c["name"] for c in data["cheap_things"]] == [
        "Pretoria National Botanical Garden", "Freedom Park", "Voortrekker Monument",
        "DITSONG National Museum of Natural History",
    ]
    for c in data["cheap_things"]:
        assert c["cost_note"] and c["source_url"].startswith("https://") and c["read_on"]
        assert c["last_verified"] is None  # an agent read the price; no person has checked it yet
    assert data["university"]["notice"] == "Not yet confirmed by the team." and data["lines"] == []

    place(client, me, "up", "gibs")  # Johannesburg: the Pretoria list isn't for it
    assert get(client, me.headers, "/money/cheap-things")["cheap_things"] == []
    place(client, me, "smu", "ga_rankuwa")
    smu = get(client, me.headers, "/money/cheap-things")
    assert [c["name"] for c in smu["cheap_things"]] == [
        "Wonderboom Nature Reserve: a fig tree over 1 000 years old, and walks on the Magaliesberg",
        "DITSONG: Tswaing Meteorite Crater",
    ]


@pytest.mark.parametrize("path", ["/alerts?all=1", "/support?campus=hatfield", "/money/cheap-things?university=up"])
def test_odd_queries_are_refused(client, me, path):
    assert client.get(f"{API}{path}", headers=me.headers).status_code == 422
