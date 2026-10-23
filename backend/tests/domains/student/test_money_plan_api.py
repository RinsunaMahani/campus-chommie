"""
Looking ahead with money, end to end: "can I afford this?" (nothing stored), the payday plan, goals (owner-only,
in the export) and the university's own fee dates to plan for. Hostile amounts, dates and fields are refused.
Fictional amounts; today is fixed.
"""
from __future__ import annotations

import uuid
from datetime import date

import pytest
from student_helpers import MONEY, PROFILE, student

from src.domains.student.money.services import money_service

TODAY = date(2026, 1, 10)
SETTINGS = {"balance_cents": 100000, "balance_on": "2026-01-10", "essentials_per_day_cents": 4000, "life_fund_reserve_cents": 10000}
# One-off payments, so no earlier month's unreceived payment counts as landing tomorrow.
ALLOWANCES = [{"label": "Allowance", "amount_cents": 150000, "expected_on": on, "reliability": "on_time"}
              for on in ("2026-01-30", "2026-02-28")]
GOAL = {"label": "Registration fee", "amount_cents": 90000, "due_on": "2026-03-31", "saved_cents": 20000}


@pytest.fixture(autouse=True)
def on_10_january(monkeypatch):
    monkeypatch.setattr(money_service, "_today", lambda: TODAY)


@pytest.fixture
def me(client, outbox):
    return student(client, outbox, "lerato@example.com")


@pytest.fixture
def other(client, outbox):
    return student(client, outbox, "sipho@example.com")


def ok(r, status=200):
    assert r.status_code == status, r.get_json()
    return r.get_json()["data"]


def set_up(client, who):
    ok(client.put(f"{MONEY}/settings", json=SETTINGS, headers=who.headers))
    for body in ALLOWANCES:
        ok(client.post(f"{MONEY}/income-sources", json=body, headers=who.headers), 201)


@pytest.mark.parametrize("method, path", [
    ("post", "/afford"), ("get", "/plan"), ("post", "/goals"), ("patch", f"/goals/{uuid.uuid4()}"),
    ("delete", f"/goals/{uuid.uuid4()}"),
])
def test_every_new_route_needs_a_token(client, method, path):
    assert getattr(client, method)(f"{MONEY}{path}", json={}).status_code == 401


def test_afford_needs_the_balance_first(client, me):
    r = client.post(f"{MONEY}/afford", json={"amount_cents": 5000}, headers=me.headers)
    assert r.status_code == 422 and "Add your balance" in str(r.get_json()["errors"])


def test_afford_says_yes_or_not_now_and_stores_nothing(client, me):
    set_up(client, me)
    yes = ok(client.post(f"{MONEY}/afford", json={"amount_cents": 5000}, headers=me.headers))
    assert yes["verdict"] == "yes" and yes["lines"][0].startswith("After it you'd still have about")
    no = ok(client.post(f"{MONEY}/afford", json={"amount_cents": 90000}, headers=me.headers))
    assert no["verdict"] == "not_now"
    # Even out of the 30 Jan payment it would run short before 28 Feb, so there's no safe day to suggest.
    assert no["wait_until"] is None and no["lines"][-1].startswith("Even out of your next payment")
    assert no["days_after"] < no["days_before"]
    export = ok(client.get("/api/v1/me/export", headers=me.headers))
    assert "90000" not in str(export["money"]) and "afford" not in str(export).lower()


@pytest.mark.parametrize("body", [
    {}, {"amount_cents": 0}, {"amount_cents": -100}, {"amount_cents": 12.5}, {"amount_cents": "5000"},
    {"amount_cents": True}, {"amount_cents": 10**12}, {"amount_cents": 5000, "user_id": "x"},
])
def test_odd_prices_are_refused(client, me, body):
    set_up(client, me)
    assert client.post(f"{MONEY}/afford", json=body, headers=me.headers).status_code == 422


def test_afford_takes_no_query_string(client, me):
    set_up(client, me)
    assert client.post(f"{MONEY}/afford?debug=1", json={"amount_cents": 5000}, headers=me.headers).status_code == 422


def test_the_plan_splits_the_next_payday_and_shares_each_goal(client, me):
    set_up(client, me)
    ok(client.post(f"{MONEY}/goals", json=GOAL, headers=me.headers), 201)
    plan = ok(client.get(f"{MONEY}/plan", headers=me.headers))
    assert plan["payday"]["lands_on"] == "2026-01-30" and plan["payday"]["amount_cents"] == 150000
    assert [p["label"] for p in plan["payday"]["pots"]] == ["Essentials", "Registration fee"]
    assert plan["payday"]["pots"][0]["cents"] == 4000 * 29  # 30 Jan to the next payday, 28 Feb
    assert plan["goals"][0] | {"id": "x"} == {
        "id": "x", "label": "Registration fee", "kind": "goal", "amount_cents": 90000, "saved_cents": 20000,
        "due_on": "2026-03-31", "due_day": "Tue 31 Mar 2026", "from_university": False, "stokvel_funded": False,
        "per_week_cents": 5834, "lines": ["About R58.34 a week for 12 weeks gets you there by Tue 31 Mar 2026."],
    }


def test_the_plan_lists_the_universitys_own_fee_dates_without_amounts(client, me):
    ok(client.put(PROFILE, json={"university": "tut", "campus": "soshanguve_south"}, headers=me.headers))
    plan = ok(client.get(f"{MONEY}/plan", headers=me.headers))
    assert plan["university_dates"], "TUT's pack lists fee dates in early 2026"
    first = plan["university_dates"][0]
    assert first["on"] >= "2026-01-10" and first["kind"] in ("fee_due", "discount_deadline")
    assert first["source_url"].startswith("https://")
    assert not any("cents" in key for d in plan["university_dates"] for key in d)


def test_a_plan_without_settings_says_what_to_add(client, me):
    plan = ok(client.get(f"{MONEY}/plan", headers=me.headers))
    assert plan["payday"] is None and plan["lines"] == ["Add your balance and what you spend on essentials each day first."]


def test_goals_change_and_go_and_are_owner_only(client, me, other):
    goal = ok(client.post(f"{MONEY}/goals", json=GOAL, headers=me.headers), 201)["goal"]
    changed = ok(client.patch(f"{MONEY}/goals/{goal['id']}", json={"saved_cents": 90000}, headers=me.headers))["goal"]
    assert changed["lines"] == ["Done: you've put it all aside."]
    for call in (lambda: client.patch(f"{MONEY}/goals/{goal['id']}", json={"saved_cents": 0}, headers=other.headers),
                 lambda: client.delete(f"{MONEY}/goals/{goal['id']}", headers=other.headers)):
        r = call()
        assert r.status_code == 404 and r.get_json()["code"] == "MONEY_GOAL_NOT_FOUND"
    assert ok(client.get(f"{MONEY}/plan", headers=other.headers))["goals"] == []
    ok(client.delete(f"{MONEY}/goals/{goal['id']}", headers=me.headers))
    assert ok(client.get(f"{MONEY}/plan", headers=me.headers))["goals"] == []


@pytest.mark.parametrize("change", [
    {"label": ""}, {"label": "   "}, {"label": "x" * 81}, {"label": "Fee\nsplit"}, {"amount_cents": 0},
    {"amount_cents": "900"}, {"due_on": "2025-12-31"}, {"due_on": "2028-06-01"}, {"due_on": "31-03-2026"},
    {"saved_cents": 100000}, {"saved_cents": -1}, {"from_university": "yes"}, {"user_id": "someone-else"},
])
def test_odd_goals_are_refused(client, me, change):
    assert client.post(f"{MONEY}/goals", json=GOAL | change, headers=me.headers).status_code == 422


def test_a_goal_change_cannot_save_more_than_the_goal(client, me):
    goal = ok(client.post(f"{MONEY}/goals", json=GOAL, headers=me.headers), 201)["goal"]
    assert client.patch(f"{MONEY}/goals/{goal['id']}", json={"amount_cents": 10000}, headers=me.headers).status_code == 422
    assert client.patch(f"{MONEY}/goals/{goal['id']}", json={}, headers=me.headers).status_code == 422


def test_at_most_ten_goals(client, me):
    for i in range(10):
        ok(client.post(f"{MONEY}/goals", json=GOAL | {"label": f"Goal {i}"}, headers=me.headers), 201)
    assert client.post(f"{MONEY}/goals", json=GOAL, headers=me.headers).status_code == 422


def test_goals_are_in_the_export(client, me):
    ok(client.post(f"{MONEY}/goals", json=GOAL | {"from_university": True}, headers=me.headers), 201)
    export = ok(client.get("/api/v1/me/export", headers=me.headers))
    assert [g["label"] for g in export["money"]["goals"]] == ["Registration fee"]
    assert export["money"]["goals"][0]["from_university"] is True


def test_pots_crud_and_payday_plan_priorities(client, me):
    set_up(client, me)
    # Family pot: monthly amount, no date
    fam = ok(client.post(f"{MONEY}/goals", json={
        "label": "Family support", "kind": "family", "amount_cents": 30000, "saved_cents": 10000,
    }, headers=me.headers), 201)["goal"]
    assert fam["kind"] == "family"
    assert fam["due_on"] is None
    assert fam["due_day"] is None
    assert fam["lines"] == ["R300 monthly support for family: R100 aside so far, R200 still to find."]

    # Stokvel pot: monthly contribution, no date
    stok = ok(client.post(f"{MONEY}/goals", json={
        "label": "Groceries stokvel", "kind": "stokvel", "amount_cents": 20000,
    }, headers=me.headers), 201)["goal"]
    assert stok["kind"] == "stokvel"
    assert stok["due_on"] is None
    assert stok["lines"] == ["R200 a month for your stokvel contribution."]

    # Buffer pot: emergency target, no date
    buf = ok(client.post(f"{MONEY}/goals", json={
        "label": "Emergency buffer", "kind": "buffer", "amount_cents": 50000,
    }, headers=me.headers), 201)["goal"]
    assert buf["kind"] == "buffer"
    assert buf["due_on"] is None
    assert buf["per_week_cents"] is None
    assert buf["lines"] == ["R500 emergency buffer to keep aside."]

    # Big purchase with stokvel funding
    bp = ok(client.post(f"{MONEY}/goals", json={
        "label": "New laptop", "kind": "big_purchase", "amount_cents": 90000, "due_on": "2026-03-31",
        "stokvel_funded": True,
    }, headers=me.headers), 201)["goal"]
    assert bp["kind"] == "big_purchase"
    assert bp["stokvel_funded"] is True
    assert "Paying through a stokvel." in bp["lines"][0]

    # Check payday plan order: Essentials -> Family -> Stokvel -> Buffer -> Big purchase
    plan = ok(client.get(f"{MONEY}/plan", headers=me.headers))
    pot_labels = [p["label"] for p in plan["payday"]["pots"]]
    assert pot_labels == ["Essentials", "Family support", "Groceries stokvel", "Emergency buffer", "New laptop"]

    # Update family pot
    updated_fam = ok(client.patch(f"{MONEY}/goals/{fam['id']}", json={"saved_cents": 30000}, headers=me.headers))["goal"]
    assert updated_fam["lines"] == ["Done: you've set aside your family support for this month."]

    # Delete buffer
    ok(client.delete(f"{MONEY}/goals/{buf['id']}", headers=me.headers))
    goals_after = ok(client.get(f"{MONEY}/plan", headers=me.headers))["goals"]
    assert not any(g["id"] == buf["id"] for g in goals_after)


@pytest.mark.parametrize("bad_body", [
    {"label": "Test", "kind": "unknown", "amount_cents": 10000},
    {"label": "Family", "kind": "family", "amount_cents": 10000, "due_on": "2026-03-31"},
    {"label": "Stokvel", "kind": "stokvel", "amount_cents": 10000, "due_on": "2026-03-31"},
    {"label": "Buffer", "kind": "buffer", "amount_cents": 10000, "due_on": "2026-03-31"},
    {"label": "Goal", "kind": "goal", "amount_cents": 10000},  # missing due_on
    {"label": "Big purchase", "kind": "big_purchase", "amount_cents": 10000},  # missing due_on
    {"label": "Family", "kind": "family", "amount_cents": 10000, "stokvel_funded": True},
    {"label": "Goal", "kind": "goal", "amount_cents": 10000, "due_on": "2026-03-31", "stokvel_funded": True},
    {"label": "Family", "kind": "family", "amount_cents": 10000, "from_university": True},
    {"label": "Family", "kind": "family", "amount_cents": -5000},
    {"label": "Family", "kind": "family", "amount_cents": 10**11},
    {"label": "Family", "kind": "family", "amount_cents": 10000, "saved_cents": 20000},
    {"label": "Family", "kind": "family", "amount_cents": 10000, "extra_field": "disallowed"},
])
def test_hostile_pot_inputs_are_refused(client, me, bad_body):
    set_up(client, me)
    assert client.post(f"{MONEY}/goals", json=bad_body, headers=me.headers).status_code == 422


def test_pots_are_owner_only_on_idor(client, me, other):
    fam = ok(client.post(f"{MONEY}/goals", json={
        "label": "Family support", "kind": "family", "amount_cents": 30000,
    }, headers=me.headers), 201)["goal"]
    # Other student trying to patch or delete answers 404
    r_patch = client.patch(f"{MONEY}/goals/{fam['id']}", json={"amount_cents": 40000}, headers=other.headers)
    assert r_patch.status_code == 404 and r_patch.get_json()["code"] == "MONEY_GOAL_NOT_FOUND"

    r_del = client.delete(f"{MONEY}/goals/{fam['id']}", headers=other.headers)
    assert r_del.status_code == 404 and r_del.get_json()["code"] == "MONEY_GOAL_NOT_FOUND"
