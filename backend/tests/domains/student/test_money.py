"""
My money end to end: settings, income sources becoming expected payments,
"received?" taps, one spending number per day, a balance that stays current,
and the summary the engine makes of it all, including the brief's M3 checks
with the fictional demo personas. Today is fixed at the personas' date.
"""
from __future__ import annotations

import uuid
from datetime import date

import pytest
from student_helpers import MONEY, set_up_persona, student

from src.domains.student.money.services import money_service

TODAY = date(2026, 10, 12)


@pytest.fixture(autouse=True)
def on_12_october(monkeypatch):
    monkeypatch.setattr(money_service, "_today", lambda: TODAY)


@pytest.fixture
def me(client, outbox):
    return student(client, outbox, "naledi@example.com")


def get(client, who, path, **query):
    r = client.get(f"{MONEY}{path}", headers=who.headers, query_string=query)
    assert r.status_code == 200, r.get_json()
    return r.get_json()["data"]


SETTINGS = {"balance_cents": 100000, "balance_on": "2026-10-12", "essentials_per_day_cents": 4000, "life_fund_reserve_cents": 10000}


@pytest.mark.parametrize(
    "method, path",
    [
        ("get", "/settings"), ("put", "/settings"), ("get", "/income-sources"), ("post", "/income-sources"),
        ("put", f"/income-sources/{uuid.uuid4()}"), ("delete", f"/income-sources/{uuid.uuid4()}"),
        ("get", "/payments"), ("patch", f"/payments/{uuid.uuid4()}"), ("get", "/spending"),
        ("put", "/spending/2026-10-11"), ("delete", "/spending/2026-10-11"), ("get", "/summary"),
    ],
)
def test_every_money_route_needs_a_token(client, method, path):
    assert getattr(client, method)(f"{MONEY}{path}", json={}).status_code == 401


def test_settings_round_trip(client, me):
    assert get(client, me, "/settings") == {"settings": None}
    r = client.put(f"{MONEY}/settings", json=SETTINGS, headers=me.headers)
    assert r.status_code == 200 and r.get_json()["data"]["settings"] == SETTINGS
    assert get(client, me, "/settings")["settings"] == SETTINGS


def test_a_monthly_source_becomes_a_payment_each_month_to_the_horizon(client, me):
    body = {"label": "Living allowance", "amount_cents": 150000, "day_of_month": 31, "reliability": "sometimes_late"}
    r = client.post(f"{MONEY}/income-sources", json=body, headers=me.headers)
    assert r.status_code == 201
    payments = get(client, me, "/payments")["payments"]
    # From a month back to 120 days ahead; the 31st is each month's last day.
    assert [p["expected_on"] for p in payments] == ["2026-09-30", "2026-10-31", "2026-11-30", "2026-12-31", "2027-01-31"]
    assert payments[0]["overdue"] is True and payments[1]["overdue"] is False
    assert {p["label"] for p in payments} == {"Living allowance"}
    assert len(get(client, me, "/payments")["payments"]) == 5  # reading again makes nothing twice


def test_received_taps_and_moved_payments(client, me):
    client.post(f"{MONEY}/income-sources", json={"label": "Allowance", "amount_cents": 150000, "day_of_month": 25}, headers=me.headers)
    first, second = get(client, me, "/payments")["payments"][:2]
    r = client.patch(f"{MONEY}/payments/{first['id']}", json={"received": True}, headers=me.headers)
    assert r.get_json()["data"]["payment"]["received_on"] == "2026-10-12"
    r = client.patch(f"{MONEY}/payments/{second['id']}", json={"expected_on": "2026-10-28", "amount_cents": 140000}, headers=me.headers)
    moved = r.get_json()["data"]["payment"]
    assert (moved["scheduled_on"], moved["expected_on"], moved["amount_cents"]) == ("2026-10-25", "2026-10-28", 140000)
    after = get(client, me, "/payments")["payments"]
    assert [p["expected_on"] for p in after][:2] == ["2026-09-25", "2026-10-28"]  # the moved one isn't made again


def test_changing_a_source_remakes_its_unreceived_payments(client, me):
    body = {"label": "Allowance", "amount_cents": 150000, "day_of_month": 25}
    source = client.post(f"{MONEY}/income-sources", json=body, headers=me.headers).get_json()["data"]["income_source"]
    received = get(client, me, "/payments")["payments"][0]
    client.patch(f"{MONEY}/payments/{received['id']}", json={"received": True}, headers=me.headers)
    body = {"label": "Allowance", "amount_cents": 160000, "day_of_month": 1}
    assert client.put(f"{MONEY}/income-sources/{source['id']}", json=body, headers=me.headers).status_code == 200
    payments = get(client, me, "/payments")["payments"]
    assert payments[0]["id"] == received["id"] and payments[0]["received"] is True  # history stays
    assert [p["expected_on"] for p in payments[1:]] == ["2026-10-01", "2026-11-01", "2026-12-01", "2027-01-01", "2027-02-01"]
    assert {p["amount_cents"] for p in payments[1:]} == {160000}


def test_deleting_a_source_deletes_its_payments(client, me):
    body = {"label": "Wage", "amount_cents": 50000, "expected_on": "2026-10-20"}
    source = client.post(f"{MONEY}/income-sources", json=body, headers=me.headers).get_json()["data"]["income_source"]
    assert len(get(client, me, "/payments")["payments"]) == 1
    assert client.delete(f"{MONEY}/income-sources/{source['id']}", headers=me.headers).status_code == 200
    assert get(client, me, "/payments")["payments"] == [] and get(client, me, "/income-sources")["income_sources"] == []


def test_one_spending_number_per_day(client, me):
    for day, cents in (("2026-10-10", 3000), ("2026-10-11", 4500), ("2026-10-11", 5200)):
        assert client.put(f"{MONEY}/spending/{day}", json={"amount_cents": cents}, headers=me.headers).status_code == 200
    assert get(client, me, "/spending")["spending"] == [
        {"spent_on": "2026-10-11", "amount_cents": 5200},
        {"spent_on": "2026-10-10", "amount_cents": 3000},
    ]
    assert get(client, me, "/spending", days=2)["spending"] == [{"spent_on": "2026-10-11", "amount_cents": 5200}]
    assert client.delete(f"{MONEY}/spending/2026-10-10", headers=me.headers).status_code == 200
    r = client.delete(f"{MONEY}/spending/2026-10-10", headers=me.headers)
    assert r.status_code == 404 and r.get_json()["code"] == "SPENDING_NOT_FOUND"


def test_the_balance_stays_current_without_retyping_it(client, me):
    client.put(f"{MONEY}/settings", json=dict(SETTINGS, balance_on="2026-10-09"), headers=me.headers)
    client.put(f"{MONEY}/spending/2026-10-09", json={"amount_cents": 9999}, headers=me.headers)  # already in the balance
    client.put(f"{MONEY}/spending/2026-10-10", json={"amount_cents": 5000}, headers=me.headers)
    client.put(f"{MONEY}/spending/2026-10-11", json={"amount_cents": 3000}, headers=me.headers)
    client.post(f"{MONEY}/income-sources", json={"label": "Wage", "amount_cents": 20000, "expected_on": "2026-10-11"}, headers=me.headers)
    wage = get(client, me, "/payments")["payments"][0]
    client.patch(f"{MONEY}/payments/{wage['id']}", json={"received": True}, headers=me.headers)
    balance = get(client, me, "/summary")["balance"]
    assert balance["cents"] == 100000 - 5000 - 3000 + 20000
    assert balance["lines"] == [
        "Your balance: about R1 120.",
        "You entered R1 000 on Fri 9 Oct 2026. Since then you've logged R80 of spending and marked R200 received.",
    ]


def test_the_summary_asks_for_settings_first(client, me):
    summary = get(client, me, "/summary")
    assert summary["ready"] is False and summary["lines"]


def test_without_five_logged_days_the_pace_is_the_essentials_estimate(client, me):
    client.put(f"{MONEY}/settings", json=SETTINGS, headers=me.headers)
    pace = get(client, me, "/summary")["pace"]
    assert (pace["from"], pace["daily_cents"], pace["days_logged"]) == ("essentials", 4000, 0)
    assert pace["lines"][0].startswith("Log at least 5 days of spending for a forecast.")


def test_m3_the_allowance_funded_persona_runs_short_and_the_life_fund_pauses(client, me):
    """The brief's M3 check: money runs out before the next payment, the life fund is paused, and the
    late toggle moves the payment 14 days."""
    set_up_persona(client, me, "naledi")
    summary = get(client, me, "/summary")
    assert summary["ready"] is True and summary["balance"]["cents"] == 61000
    assert summary["pace"]["from"] == "spending" and summary["pace"]["days_logged"] == 14
    runway = summary["runway"]
    assert (runway["runs_out_on"], runway["short_before_next"]) == ("2026-10-24", True)
    assert summary["next_payment"]["lands_on"] == "2026-10-30"
    assert summary["life_fund"]["state"] == "paused"
    assert summary["life_fund"]["reason"] == "Paused because your money may run out before the next payment."
    assert summary["safe_to_spend"]["per_day_cents"] == 0
    late = get(client, me, "/summary", late="true")
    assert late["late"] is True and late["next_payment"]["lands_on"] == "2026-11-13"
    assert late["runway"]["lines"][0] == "If your next payment arrives 14 days late:"


def test_m3_the_self_funded_persona_lasts_past_the_payment(client, outbox):
    """Sipho's money lasts past his transfer. The brief's "amber because of a heavy week" needs his
    week, which arrives with classes in M4: until then the summary says the week isn't included."""
    sipho = student(client, outbox, "sipho@example.com")
    set_up_persona(client, sipho, "sipho")
    summary = get(client, sipho, "/summary")
    assert summary["runway"]["short_before_next"] is False and summary["life_fund"]["state"] == "green"
    assert summary["notes"][0].startswith("Your week isn't part of this yet")
    late = get(client, sipho, "/summary", late="true")
    assert late["runway"]["short_before_next"] is True and late["life_fund"]["state"] == "paused"


def test_a_late_prone_payment_suggests_the_late_view(client, me):
    client.put(f"{MONEY}/settings", json=SETTINGS, headers=me.headers)
    body = {"label": "Bursary", "amount_cents": 150000, "expected_on": "2026-10-30", "reliability": "often_late"}
    client.post(f"{MONEY}/income-sources", json=body, headers=me.headers)
    notes = get(client, me, "/summary")["notes"]
    assert 'You said Bursary can arrive late: switch on "late" to plan for it.' in notes
    assert len(get(client, me, "/summary", late="true")["notes"]) == 1  # already planning for it
