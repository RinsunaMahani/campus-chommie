"""
My money against someone trying things: amounts that aren't whole cents
(floats, text, true, NaN), impossible dates, unknown fields (an ID or bank
number), another student's rows (the same 404 as rows that don't exist),
floods, and the yearly clean-up of old spending.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from student_helpers import MONEY, student

from src.domains.student.money.jobs import forget_old_spending
from src.domains.student.money.models import SpendingEntry
from src.domains.student.money.services import money_service
from src.extensions import db
from src.shared.rate_limit.limiter import limiter

TODAY = date(2026, 10, 12)
SETTINGS = {"balance_cents": 100000, "balance_on": "2026-10-12", "essentials_per_day_cents": 4000}
SOURCE = {"label": "Allowance", "amount_cents": 150000, "day_of_month": 25}


@pytest.fixture(autouse=True)
def on_12_october(monkeypatch):
    monkeypatch.setattr(money_service, "_today", lambda: TODAY)


@pytest.fixture
def me(client, outbox):
    return student(client, outbox, "naledi@example.com")


@pytest.fixture
def other(client, outbox):
    return student(client, outbox, "sipho@example.com")


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
    "change",
    [
        {"balance_cents": 1000.5},
        {"balance_cents": 1000.0},  # a float, even a round one
        {"balance_cents": "1000"},
        {"balance_cents": True},
        {"balance_cents": -1},
        {"balance_cents": 100_000_001},  # over R1 000 000
        {"balance_cents": 10**30},
        {"balance_cents": None},
        {"balance_on": "2026-10-13"},  # the future
        {"balance_on": "2025-10-10"},  # more than a year ago
        {"balance_on": "12/10/2026"},
        {"essentials_per_day_cents": -100},
        {"id_number": "0001015009087"},
        {"bank_account": "62000000000"},
    ],
)
def test_odd_settings_are_refused(client, me, change):
    assert client.put(f"{MONEY}/settings", json=SETTINGS | change, headers=me.headers).status_code == 422


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity", "1e400"])
def test_special_numbers_are_refused(client, me, value):
    raw = '{"balance_cents": ' + value + ', "balance_on": "2026-10-12", "essentials_per_day_cents": 4000}'
    r = client.put(f"{MONEY}/settings", data=raw, content_type="application/json", headers=me.headers)
    assert r.status_code in (400, 422)


@pytest.mark.parametrize(
    "change",
    [
        {"expected_on": "2026-10-30"},  # both a day of the month and a date
        {"day_of_month": None},  # neither
        {"day_of_month": 0},
        {"day_of_month": 32},
        {"day_of_month": "25"},
        {"amount_cents": 0},
        {"amount_cents": 15000.75},
        {"label": ""},
        {"label": "x" * 61},
        {"reliability": "never"},
        {"day_of_month": None, "expected_on": "2026-08-01"},  # more than a month overdue
        {"day_of_month": None, "expected_on": "2028-01-01"},  # more than a year ahead
        {"nsfas_password": "secret"},
    ],
)
def test_odd_income_sources_are_refused(client, me, change):
    assert client.post(f"{MONEY}/income-sources", json=SOURCE | change, headers=me.headers).status_code == 422


@pytest.mark.parametrize(
    "body",
    [{}, {"received": "true"}, {"received": 1}, {"amount_cents": 99.9}, {"expected_on": "2028-01-01"}, {"paid_to": "x"}],
)
def test_odd_payment_changes_are_refused(client, me, body):
    client.post(f"{MONEY}/income-sources", json=SOURCE, headers=me.headers)
    payment = client.get(f"{MONEY}/payments", headers=me.headers).get_json()["data"]["payments"][0]
    assert client.patch(f"{MONEY}/payments/{payment['id']}", json=body, headers=me.headers).status_code == 422


@pytest.mark.parametrize(
    "day, body",
    [
        ("2026-10-13", {"amount_cents": 100}),  # the future
        ("2025-10-01", {"amount_cents": 100}),  # more than a year ago
        ("2026-13-01", {"amount_cents": 100}),
        ("yesterday", {"amount_cents": 100}),
        ("20261011", {"amount_cents": 100}),
        ("2026-10-11", {"amount_cents": -1}),
        ("2026-10-11", {"amount_cents": 10.5}),
        ("2026-10-11", {}),
        ("2026-10-11", {"amount_cents": 100, "shop": "x"}),
    ],
)
def test_odd_spending_is_refused(client, me, day, body):
    assert client.put(f"{MONEY}/spending/{day}", json=body, headers=me.headers).status_code == 422


@pytest.mark.parametrize(
    "path",
    ["/settings?x=1", "/payments?all=1", "/income-sources?user_id=1", "/spending?days=0", "/spending?days=367", "/summary?late=maybe"],
)
def test_odd_queries_are_refused(client, me, path):
    assert client.get(f"{MONEY}{path}", headers=me.headers).status_code == 422


def test_another_students_rows_are_not_found(client, me, other):
    mine = client.post(f"{MONEY}/income-sources", json=SOURCE, headers=me.headers).get_json()["data"]["income_source"]
    payment = client.get(f"{MONEY}/payments", headers=me.headers).get_json()["data"]["payments"][0]
    client.put(f"{MONEY}/spending/2026-10-11", json={"amount_cents": 500}, headers=me.headers)

    r = client.put(f"{MONEY}/income-sources/{mine['id']}", json=SOURCE, headers=other.headers)
    assert r.status_code == 404 and r.get_json()["code"] == "INCOME_SOURCE_NOT_FOUND"
    assert client.delete(f"{MONEY}/income-sources/{mine['id']}", headers=other.headers).status_code == 404
    r = client.patch(f"{MONEY}/payments/{payment['id']}", json={"received": True}, headers=other.headers)
    assert r.status_code == 404 and r.get_json()["code"] == "PAYMENT_NOT_FOUND"
    assert client.delete(f"{MONEY}/spending/2026-10-11", headers=other.headers).status_code == 404
    for path in ("/income-sources", "/payments", "/spending"):
        listed = client.get(f"{MONEY}{path}", headers=other.headers).get_json()["data"]
        assert all(rows == [] for rows in listed.values())
    assert client.get(f"{MONEY}/settings", headers=other.headers).get_json()["data"]["settings"] is None
    # ...and nothing of mine changed.
    assert client.get(f"{MONEY}/payments", headers=me.headers).get_json()["data"]["payments"][0]["received"] is False
    assert client.get(f"{MONEY}/spending", headers=me.headers).get_json()["data"]["spending"] != []


def test_an_unknown_id_is_the_same_404(client, me):
    assert client.patch(f"{MONEY}/payments/{uuid.uuid4()}", json={"received": True}, headers=me.headers).status_code == 404
    assert client.delete(f"{MONEY}/income-sources/{uuid.uuid4()}", headers=me.headers).status_code == 404


def test_at_most_ten_income_sources(client, me):
    for i in range(10):
        assert client.post(f"{MONEY}/income-sources", json=SOURCE | {"label": f"Source {i}"}, headers=me.headers).status_code == 201
    r = client.post(f"{MONEY}/income-sources", json=SOURCE, headers=me.headers)
    assert r.status_code == 422 and "income_sources" in r.get_json()["errors"][0]


def test_changes_are_limited_per_student(client, me, other, limits_on):
    codes = [client.put(f"{MONEY}/spending/2026-10-11", json={"amount_cents": 100}, headers=me.headers).status_code for _ in range(61)]
    assert codes[:60] == [200] * 60 and codes[60] == 429
    assert client.put(f"{MONEY}/spending/2026-10-11", json={"amount_cents": 100}, headers=other.headers).status_code == 200


def test_spending_older_than_a_year_is_forgotten(app, me):
    today = datetime.now(ZoneInfo("Africa/Johannesburg")).date()  # the job's own today, not the fixed one
    with app.app_context():
        user_id = uuid.UUID(me.id)
        for days_ago in (400, 367, 365, 1):
            db.session.add(SpendingEntry(user_id=user_id, spent_on=today - timedelta(days=days_ago), amount_cents=100))
        db.session.commit()
        result = forget_old_spending.run()
        assert result.success and result.count == 2
        kept = sorted((today - e.spent_on).days for e in SpendingEntry.query.filter_by(user_id=user_id))
        assert kept == [1, 365]
