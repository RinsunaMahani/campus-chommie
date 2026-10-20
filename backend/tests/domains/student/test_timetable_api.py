"""
Timetable: a student adds, changes and removes the classes in their week and reads them back with what the
week adds up to. Owner-only (another student's class is a 404), strict bodies, in the export, and gone with
the account.
"""
from __future__ import annotations

import pytest
from student_helpers import student

from src.shared.rate_limit.limiter import limiter

API = "/api/v1"
TT = f"{API}/me/timetable"
LECTURE = {"module": "ana 201", "kind": "lecture", "weekday": 0, "starts": "08:00", "ends": "09:40", "venue": "Hall A"}


@pytest.fixture
def lerato(client, outbox):
    return student(client, outbox, "lerato@example.com")


@pytest.fixture
def sipho(client, outbox):
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


def ok(response, status=200):
    assert response.status_code == status, response.get_json()
    return response.get_json()["data"]


def test_an_empty_timetable_says_what_to_do(client, lerato):
    data = ok(client.get(TT, headers=lerato.headers))
    assert data == {"entries": [], "lines": ["Your timetable is empty. Add your classes to see your week."]}


def test_adding_classes_reads_back_the_week_and_any_clash(client, lerato):
    first = ok(client.post(TT, json=LECTURE, headers=lerato.headers), 201)
    assert first["entry"] | {"id": "x"} == {
        "id": "x", "module": "ANA 201", "title": None, "kind": "lecture", "weekday": 0, "day": "Monday",
        "starts": "08:00", "ends": "09:40", "venue": "Hall A", "clashes": False,
    }
    data = ok(client.post(TT, json={"module": "PHY121", "kind": "practical", "weekday": 0, "starts": "09:00",
                                    "ends": "11:00"}, headers=lerato.headers), 201)
    assert [e["clashes"] for e in data["entries"]] == [True, True]
    assert data["lines"][-1] == "1 clash to sort out: ANA 201 lecture and PHY121 practical overlap on Monday, 09:00 to 09:40."


def test_changing_and_removing_a_class(client, lerato):
    entry = ok(client.post(TT, json=LECTURE, headers=lerato.headers), 201)["entry"]
    changed = ok(client.patch(f"{TT}/{entry['id']}", json={"weekday": 3, "venue": "Hall B"}, headers=lerato.headers))
    assert (changed["entry"]["day"], changed["entry"]["venue"]) == ("Thursday", "Hall B")
    bad = client.patch(f"{TT}/{entry['id']}", json={"ends": "07:30"}, headers=lerato.headers)
    assert bad.status_code == 422  # ends before it starts
    assert ok(client.delete(f"{TT}/{entry['id']}", headers=lerato.headers))["entries"] == []


def test_another_students_class_is_a_404_and_stays_untouched(client, lerato, sipho):
    entry = ok(client.post(TT, json=LECTURE, headers=lerato.headers), 201)["entry"]
    for call in (lambda: client.patch(f"{TT}/{entry['id']}", json={"weekday": 1}, headers=sipho.headers),
                 lambda: client.delete(f"{TT}/{entry['id']}", headers=sipho.headers)):
        r = call()
        assert r.status_code == 404 and r.get_json()["code"] == "TIMETABLE_ENTRY_NOT_FOUND"
    assert ok(client.get(TT, headers=sipho.headers))["entries"] == []
    assert ok(client.get(TT, headers=lerato.headers))["entries"][0]["weekday"] == 0


def test_signed_out_is_refused(client):
    assert client.get(TT).status_code == 401
    assert client.post(TT, json=LECTURE).status_code == 401


@pytest.mark.parametrize("change", [
    {"module": ""}, {"module": "x" * 21}, {"module": "ANA;DROP"}, {"kind": "party"}, {"weekday": 7}, {"weekday": "0"},
    {"weekday": True}, {"starts": "8:00"}, {"starts": "08:03"}, {"starts": "05:00"}, {"ends": "23:00"},
    {"starts": 800}, {"ends": "08:00"}, {"venue": "x" * 81}, {"venue": "Hall\nA"}, {"title": "   "},
    {"student_number": "123"}, {"user_id": "someone-else"},
])
def test_odd_classes_are_refused(client, lerato, change):
    assert client.post(TT, json=LECTURE | change, headers=lerato.headers).status_code == 422


def test_odd_requests_are_refused(client, lerato):
    assert client.post(TT, data="not json", headers=lerato.headers).status_code == 422
    assert client.post(TT, json=[LECTURE], headers=lerato.headers).status_code == 422
    assert client.get(TT, query_string={"user": "x"}, headers=lerato.headers).status_code == 422
    entry = ok(client.post(TT, json=LECTURE, headers=lerato.headers), 201)["entry"]
    assert client.patch(f"{TT}/{entry['id']}", json={}, headers=lerato.headers).status_code == 422
    assert client.delete(f"{TT}/not-a-uuid", headers=lerato.headers).status_code == 404


def test_at_most_sixty_classes(client, lerato):
    for i in range(60):
        ok(client.post(TT, json=LECTURE | {"module": f"M{i}"}, headers=lerato.headers), 201)
    assert client.post(TT, json=LECTURE, headers=lerato.headers).status_code == 422


def test_the_export_has_the_timetable(client, lerato):
    ok(client.post(TT, json=LECTURE, headers=lerato.headers), 201)
    data = ok(client.get(f"{API}/me/export", headers=lerato.headers))
    assert data["timetable"]["classes"] == [{
        "module": "ANA 201", "title": None, "kind": "lecture", "weekday": 0, "day": "Monday",
        "starts": "08:00", "ends": "09:40", "venue": "Hall A",
    }]


def test_the_timetable_is_limited_per_student(client, lerato, limits_on):
    codes = [client.get(TT, headers=lerato.headers).status_code for _ in range(121)]
    assert codes[:120] == [200] * 120 and codes[120] == 429
