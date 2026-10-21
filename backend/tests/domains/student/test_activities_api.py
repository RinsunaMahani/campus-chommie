"""
A student's own activities: weekly or once, flagged when they clash with a class or another plan, owner-only,
in the export, and "Find a time" around classes, exams and plans. Hostile bodies are refused.
"""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from student_helpers import student

from src.domains.student.timetable.services import activity_service

API = "/api/v1"
ACT = f"{API}/me/activities"
NOW = datetime(2026, 10, 26, 6, 0, tzinfo=ZoneInfo("Africa/Johannesburg"))  # Monday, early
GROCERIES = {"title": "Groceries", "kind": "errands", "weekday": 5, "starts": "09:00", "ends": "10:00", "place": "Shoprite"}


@pytest.fixture(autouse=True)
def monday_morning(monkeypatch):
    monkeypatch.setattr(activity_service, "_now", lambda: NOW)


@pytest.fixture
def lerato(client, outbox):
    return student(client, outbox, "lerato@example.com")


@pytest.fixture
def sipho(client, outbox):
    return student(client, outbox, "sipho@example.com")


def ok(r, status=200):
    assert r.status_code == status, r.get_json()
    return r.get_json()["data"]


def test_weekly_and_one_off_plans_read_back(client, lerato):
    first = ok(client.post(ACT, json=GROCERIES, headers=lerato.headers), 201)
    assert first["activity"] | {"id": "x"} == {
        "id": "x", "title": "Groceries", "kind": "errands", "weekday": 5, "on": None, "day": "Saturday",
        "starts": "09:00", "ends": "10:00", "place": "Shoprite", "clashes": False,
    }
    data = ok(client.post(ACT, json={"title": "Date night", "kind": "social", "on": "2026-10-30", "starts": "19:00",
                                     "ends": "22:30"}, headers=lerato.headers), 201)
    assert [(a["title"], a["day"]) for a in data["activities"]] == [("Groceries", "Saturday"), ("Date night", "Fri 30 Oct 2026")]
    assert data["lines"] == ["1 every week, 1 one-off."]


def test_a_plan_over_a_class_is_marked(client, lerato):
    ok(client.post(f"{API}/me/timetable", json={"module": "ANA201", "kind": "lecture", "weekday": 0, "starts": "08:00",
                                                "ends": "09:40"}, headers=lerato.headers), 201)
    data = ok(client.post(ACT, json=GROCERIES | {"weekday": 0, "starts": "09:00"}, headers=lerato.headers), 201)
    assert data["activities"][0]["clashes"] is True
    assert data["lines"][-1] == "Some of your plans clash with a class or another plan: they're marked."


def test_changing_between_weekly_and_once_and_removing(client, lerato):
    a = ok(client.post(ACT, json=GROCERIES, headers=lerato.headers), 201)["activity"]
    moved = ok(client.patch(f"{ACT}/{a['id']}", json={"weekday": None, "on": "2026-10-31"}, headers=lerato.headers))
    assert (moved["activity"]["weekday"], moved["activity"]["on"]) == (None, "2026-10-31")
    assert client.patch(f"{ACT}/{a['id']}", json={"ends": "08:00"}, headers=lerato.headers).status_code == 422
    assert client.patch(f"{ACT}/{a['id']}", json={"weekday": 2}, headers=lerato.headers).status_code == 422  # both set
    assert ok(client.delete(f"{ACT}/{a['id']}", headers=lerato.headers))["activities"] == []


def test_another_students_plan_is_a_404(client, lerato, sipho):
    a = ok(client.post(ACT, json=GROCERIES, headers=lerato.headers), 201)["activity"]
    for r in (client.patch(f"{ACT}/{a['id']}", json={"title": "Mine now"}, headers=sipho.headers),
              client.delete(f"{ACT}/{a['id']}", headers=sipho.headers)):
        assert r.status_code == 404 and r.get_json()["code"] == "ACTIVITY_NOT_FOUND"
    assert ok(client.get(ACT, headers=sipho.headers))["activities"] == []
    assert client.delete(f"{ACT}/not-a-uuid", headers=lerato.headers).status_code == 404


@pytest.mark.parametrize("change", [
    {"title": ""}, {"title": "   "}, {"title": "x" * 61}, {"title": "Gym\nnow"}, {"kind": "religion"},
    {"kind": "church"}, {"weekday": 7}, {"weekday": "5"}, {"weekday": None}, {"on": "2026-10-30"},
    {"starts": "9:00"}, {"starts": "09:03"}, {"ends": "08:00"}, {"ends": "24:00"}, {"place": "x" * 81},
    {"user_id": "someone-else"}, {"weekday": None, "on": "2028-01-01"},
])
def test_odd_plans_are_refused(client, lerato, change):
    assert client.post(ACT, json=GROCERIES | change, headers=lerato.headers).status_code == 422


def test_signed_out_and_query_strings_are_refused(client, lerato):
    assert client.get(ACT).status_code == 401
    assert client.post(ACT, json=GROCERIES).status_code == 401
    assert client.post(f"{ACT}/find-time", json={"minutes": 60}).status_code == 401
    assert client.get(f"{ACT}?user=x", headers=lerato.headers).status_code == 422


def test_find_a_time_goes_round_classes_and_plans(client, lerato):
    ok(client.post(f"{API}/me/timetable", json={"module": "ANA201", "kind": "lecture", "weekday": 0, "starts": "07:00",
                                                "ends": "16:00"}, headers=lerato.headers), 201)
    ok(client.post(ACT, json={"title": "Shift", "kind": "work", "weekday": 0, "starts": "16:30", "ends": "19:00"},
                   headers=lerato.headers), 201)
    data = ok(client.post(f"{ACT}/find-time", json={"minutes": 60, "days": 2}, headers=lerato.headers))
    assert [(s["day"], s["starts"], s["ends"]) for s in data["slots"]] == [
        ("Mon 26 Oct 2026", "19:15", "20:15"), ("Tue 27 Oct 2026", "07:00", "08:00")]  # a free day: its first hour
    assert data["lines"][0].startswith("Free for 1 hour: Mon 26 Oct 2026, 19:15 to 20:15;")


@pytest.mark.parametrize("body", [
    {}, {"minutes": 10}, {"minutes": 481}, {"minutes": 62}, {"minutes": "60"}, {"minutes": 60, "days": 15},
    {"minutes": 60, "start": "26-10-2026"}, {"minutes": 60, "where": "campus"},
])
def test_odd_find_time_requests_are_refused(client, lerato, body):
    assert client.post(f"{ACT}/find-time", json=body, headers=lerato.headers).status_code == 422


def test_plans_are_in_the_export(client, lerato):
    ok(client.post(ACT, json=GROCERIES, headers=lerato.headers), 201)
    export = ok(client.get(f"{API}/me/export", headers=lerato.headers))
    assert export["timetable"]["activities"] == [{
        "title": "Groceries", "kind": "errands", "weekday": 5, "on": None, "day": "Saturday", "starts": "09:00",
        "ends": "10:00", "place": "Shoprite",
    }]
