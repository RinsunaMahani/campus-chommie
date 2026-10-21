"""
GET /me/next-steps: "Do this next" for Home, from the signed-in student's own records only. Signed out and query
strings are refused; a new student is told what to set up; money running short comes first.
"""
from __future__ import annotations

from datetime import date

import pytest
from student_helpers import MONEY, student

from src.domains.student.alerts.services import next_steps_service
from src.domains.student.money.services import money_service

TODAY = date(2026, 10, 21)
NEXT = "/api/v1/me/next-steps"


@pytest.fixture(autouse=True)
def on_21_october(monkeypatch):
    monkeypatch.setattr(money_service, "_today", lambda: TODAY)
    monkeypatch.setattr(next_steps_service, "_today", lambda: TODAY)


@pytest.fixture
def me(client, outbox):
    return student(client, outbox, "lerato@example.com")


def test_signed_out_and_odd_requests_are_refused(client, me):
    assert client.get(NEXT).status_code == 401
    assert client.get(f"{NEXT}?user=x", headers=me.headers).status_code == 422


def test_a_new_student_is_told_what_to_set_up(client, me):
    data = client.get(NEXT, headers=me.headers).get_json()["data"]
    assert [s["kind"] for s in data["steps"]] == ["setup_classes", "setup_money"]
    assert data["steps"][0] | {"why": ""} == {
        "kind": "setup_classes", "line": "Add your classes, or import your timetable PDF.", "why": "",
        "action": "Add my classes", "target": "timetable", "tone": "normal",
    }


def test_money_running_short_comes_first(client, me):
    client.put(f"{MONEY}/settings", json={"balance_cents": 20000, "balance_on": "2026-10-21",
                                          "essentials_per_day_cents": 4000}, headers=me.headers)
    client.post(f"{MONEY}/income-sources", json={"label": "Allowance", "amount_cents": 150000,
                                                 "expected_on": "2026-11-08"}, headers=me.headers)
    steps = client.get(NEXT, headers=me.headers).get_json()["data"]["steps"]
    assert steps[0]["kind"] == "money" and steps[0]["tone"] == "attention"
    assert steps[0]["line"].startswith("Money runs out around Mon 26 Oct")
