"""
A student's data, theirs to see and theirs to delete (POPIA). GET /me/export
holds everything we keep about them, from every feature, and nothing about
anyone else. DELETE /me, after the password, takes the account and every
row that points at it; what belongs to the class (the events a rep
confirmed) stays, with no name on it. A demo account can't be deleted, and
a new table that points at an account must say how it's exported.
"""
from __future__ import annotations

import uuid

import pytest
from demo_helpers import PASSWORD, TODAY, fresh_password, on_day, seed, student
from sqlalchemy import text

from src.extensions import db
from src.shared.privacy import privacy
from src.shared.queue.queue import wait_until_idle
from src.shared.rate_limit.limiter import limiter

API = "/api/v1"

#: Every table outside identity that points at an account, and the export section that holds it. A new one
#: fails test_every_table_that_points_at_an_account_is_exported until it's added here and to the export.
EXPORTED_TABLES = {
    "student.profiles": "profile",
    "student.money_settings": "money",
    "student.income_sources": "money",
    "student.expected_payments": "money",
    "student.spending_entries": "money",
    "student.modules": "marks",
    "student.assessments": "marks",
    "classes.class_members": "classes",
    "classes.announcements": "class_messages",
    "classes.event_flags": "class_messages",
    "platform.notifications": "alerts",
    "platform.notification_switches": "alert_switches",
    "student.saved_funders": "saved_funding",
    "student.timetable_entries": "timetable",
    # Not a student's own data: who confirmed or changed an event (cleared when they go), and which
    # account plays a demo persona.
    "classes.class_events": None,
    "classes.event_changes": None,
    "platform.demo_accounts": None,
}


@pytest.fixture(autouse=True)
def on_12_october(monkeypatch):
    on_day(monkeypatch, TODAY)


@pytest.fixture
def me(client, outbox):
    return student(client, outbox, "lerato@example.com")


@pytest.fixture
def other(client, outbox):
    return student(client, outbox, "sipho@example.com")


def ok(response, status=200):
    assert response.status_code == status, response.get_json()
    return response.get_json()["data"]


def fill(client, who, code: str) -> dict:
    """Something in every feature that keeps personal data, entered through the API."""
    h = who.headers
    ok(client.put(f"{API}/me/profile", json={"university": "up", "campus": "hatfield"}, headers=h))
    ok(client.put(f"{API}/money/settings", json={"balance_cents": 100000, "balance_on": "2026-10-12",
                                                "essentials_per_day_cents": 4000}, headers=h))
    ok(client.post(f"{API}/money/income-sources", json={"label": "Allowance", "amount_cents": 150000, "day_of_month": 25},
                   headers=h), 201)
    ok(client.put(f"{API}/money/spending/2026-10-11", json={"amount_cents": 4500}, headers=h))
    module = ok(client.post(f"{API}/academics/modules", json={"code": code, "target": 60}, headers=h), 201)["module"]
    ok(client.post(f"{API}/academics/modules/{module['id']}/assessments", json={"name": "Test 1", "weight": 20, "mark": 64},
                   headers=h), 201)
    made = ok(client.post(f"{API}/classes", json={"university": "up", "campus": "hatfield", "module_code": code,
                                                 "year": 2026}, headers=h), 201)["class"]
    candidate = ok(client.post(f"{API}/classes/{made['id']}/announcements", json={"text": f"{code} test 2 on 20 Oct at 08:00"},
                               headers=h), 201)["candidate"]
    body = {k: v for k, v in candidate["proposed"].items() if k != "event_id"}
    event = ok(client.post(f"{API}/candidates/{candidate['id']}/confirm", json=body, headers=h))["event"]
    ok(client.post(f"{API}/events/{event['id']}/flag", json={"reason": "wrong_venue"}, headers=h))
    ok(client.put(f"{API}/me/funding/funza_lushaka", headers=h))
    ok(client.post(f"{API}/auth/logout-others", headers=h))  # an alert: "Other phones signed out"
    wait_until_idle(timeout=10)
    return {"class": made, "event": event}


def export(client, who) -> dict:
    return ok(client.get(f"{API}/me/export", headers=who.headers))


# ------------------------------------------------------------------ export


def test_the_export_holds_everything_about_me(client, me):
    fill(client, me, "ANA201")
    data = export(client, me)
    assert set(privacy.sections()) <= set(data)
    assert data["account"]["email"] == "lerato@example.com"
    assert data["profile"] == {"university": "up", "campus": "hatfield"}
    money = data["money"]
    assert money["settings"]["balance_cents"] == 100000
    assert [s["label"] for s in money["income_sources"]] == ["Allowance"]
    assert money["payments"] and all(p["label"] == "Allowance" for p in money["payments"])
    assert money["spending"] == [{"spent_on": "2026-10-11", "amount_cents": 4500}]
    assert data["marks"] == [{"code": "ANA201", "name": None, "target": 60,
                              "assessments": [{"name": "Test 1", "weight": 20, "mark": 64}]}]
    assert [(c["module_code"], c["role"]) for c in data["classes"]] == [("ANA201", "rep")]
    messages = data["class_messages"]
    assert [(a["module"], a["status"], a["text"]) for a in messages["announcements"]] == [
        ("ANA201", "confirmed", "ANA201 test 2 on 20 Oct at 08:00")]
    assert [(f["event"], f["reason"]) for f in messages["flags"]] == [("Test 2", "wrong_venue")]
    assert "Other phones signed out" in [a["title"] for a in data["alerts"]]
    assert data["saved_funding"] == {"saved": [{"funder": "funza_lushaka", "name": "Funza Lushaka", "saved_on": "2026-10-12"}]}


def test_the_export_holds_nothing_about_anyone_else(client, me, other):
    mine = fill(client, me, "ANA201")
    fill(client, other, "STK210")
    ok(client.post(f"{API}/classes/join", json={"code": mine["class"]["invite_code"]}, headers=other.headers))
    ok(client.post(f"{API}/events/{mine['event']['id']}/flag", json={"reason": "wrong_date"}, headers=other.headers))
    text_of = str(export(client, me))
    assert "STK210" not in text_of and "sipho@example.com" not in text_of and other.id not in text_of
    assert "wrong_date" not in text_of  # their flag on my event is theirs


def test_a_new_student_exports_empty_sections(client, me):
    data = export(client, me)
    assert data["profile"] is None and data["marks"] == [] and data["classes"] == []
    assert data["money"] == {"settings": None, "income_sources": [], "payments": [], "spending": []}
    assert data["class_messages"] == {"announcements": [], "flags": []}
    assert data["saved_funding"] == {"saved": []}


# ------------------------------------------------------------------ delete


def _rows_for(user_id: str) -> dict[str, int]:
    counts = {}
    for table, column in [
        ("identity.users", "id"), ("identity.consents", "user_id"), ("identity.password_credentials", "user_id"),
        ("identity.sessions", "user_id"), ("student.profiles", "user_id"), ("student.money_settings", "user_id"),
        ("student.income_sources", "user_id"), ("student.expected_payments", "user_id"),
        ("student.spending_entries", "user_id"), ("student.modules", "user_id"), ("student.assessments", "user_id"),
        ("classes.class_members", "user_id"), ("classes.announcements", "submitted_by"),
        ("classes.event_flags", "user_id"), ("platform.notifications", "user_id"),
    ]:
        counts[table] = db.session.execute(
            text(f"SELECT count(*) FROM {table} WHERE {column} = :id"), {"id": uuid.UUID(user_id)}
        ).scalar()
    return counts


def test_deleting_needs_the_password_and_takes_everything(app, client, me, other):
    mine = fill(client, me, "ANA201")
    fill(client, other, "STK210")
    ok(client.post(f"{API}/classes/join", json={"code": mine["class"]["invite_code"]}, headers=other.headers))

    r = client.delete(f"{API}/me", json={"password": "Wrong-pass-1!"}, headers=me.headers)
    assert r.status_code == 400 and r.get_json()["code"] == "WRONG_PASSWORD"
    with app.app_context():
        assert _rows_for(me.id)["identity.users"] == 1

    ok(client.delete(f"{API}/me", json={"password": PASSWORD}, headers=me.headers))
    with app.app_context():
        left = _rows_for(me.id)
        assert left == dict.fromkeys(left, 0), left
        # What belongs to the class stays, with no name on it.
        verified_by = db.session.execute(text("SELECT verified_by FROM classes.class_events WHERE id = :id"),
                                         {"id": uuid.UUID(mine["event"]["id"])}).scalar()
        assert verified_by is None
    assert client.get(f"{API}/me", headers=me.headers).status_code == 401  # signed out everywhere
    assert client.post(f"{API}/auth/login", json={"email": "lerato@example.com", "password": PASSWORD}).status_code == 401

    theirs = export(client, other)  # nothing of anyone else's went
    assert [m["code"] for m in theirs["marks"]] == ["STK210"]
    assert sorted(c["module_code"] for c in theirs["classes"]) == ["ANA201", "STK210"]
    events = ok(client.get(f"{API}/classes/{mine['class']['id']}/events", headers=other.headers))["events"]
    assert [e["title"] for e in events] == ["Test 2"]


@pytest.mark.parametrize("body", [None, {}, {"password": ""}, {"password": PASSWORD, "confirm": True}, {"user_id": "x"}])
def test_odd_delete_requests_are_refused(client, me, body):
    r = client.delete(f"{API}/me", json=body, headers=me.headers) if body is not None else client.delete(
        f"{API}/me", headers=me.headers)
    assert r.status_code == 422
    assert client.get(f"{API}/me", headers=me.headers).status_code == 200


def test_deleting_needs_a_token(client):
    assert client.delete(f"{API}/me", json={"password": PASSWORD}).status_code == 401


def test_a_demo_account_cant_be_deleted(app, client):
    password = fresh_password()
    seed(app, password)
    r = client.post(f"{API}/auth/login", json={"email": "naledi.demo@example.com", "password": password})
    headers = {"Authorization": f"Bearer {r.get_json()['data']['access_token']}"}
    r = client.delete(f"{API}/me", json={"password": password}, headers=headers)
    assert r.status_code == 403 and r.get_json()["code"] == "DEMO_ACCOUNT"


def test_deleting_is_limited(app, client, me):
    limiter.enabled = True
    with app.app_context():
        limiter.reset()
    try:
        codes = [client.delete(f"{API}/me", json={"password": "Wrong-pass-1!"}, headers=me.headers).status_code
                 for _ in range(4)]
        assert codes == [400, 400, 400, 429]
    finally:
        with app.app_context():
            limiter.reset()
        limiter.enabled = False


def test_every_table_that_points_at_an_account_is_exported(app):
    """Adding a table with a user's id outside identity means deciding how it's exported."""
    pointing = set()
    for table in db.metadata.sorted_tables:
        if table.schema == "identity":
            continue
        for fk in table.foreign_keys:
            if fk.target_fullname == "identity.users.id":
                pointing.add(f"{table.schema}.{table.name}")
    assert pointing == set(EXPORTED_TABLES), "Add the table's export to src/__init__.py and to EXPORTED_TABLES"
    assert {s for s in EXPORTED_TABLES.values() if s} == set(privacy.sections())
