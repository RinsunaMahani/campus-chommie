"""
Saved funding: a student saves funders (UniApplyForMe's bookmark), sees each with today's status,
and hears when one opens after they saved it and as its closing date comes near, once each.
Owner-only, nothing kept but the funder and the day, and odd requests refused.
"""
from __future__ import annotations

from datetime import date

import pytest
from sqlalchemy import text
from student_helpers import on_day, student

from src.domains.student.saved_funding.services import saved_funding_service
from src.extensions import db
from src.shared.cache import cache as cache_module
from src.shared.queue.queue import wait_until_idle
from src.shared.rate_limit.limiter import limiter

API = "/api/v1"
SAVED = f"{API}/me/funding"
NOTIFICATIONS = f"{API}/me/notifications"


@pytest.fixture(autouse=True)
def on_12_october(monkeypatch):
    on_day(monkeypatch, date(2026, 10, 12))


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


def saved_ids(client, who) -> list[str]:
    return [f["id"] for f in ok(client.get(SAVED, headers=who.headers))["funders"]]


def first_poll_of(client, who, monkeypatch, day: date) -> list[dict]:
    """The student's first poll on `day` (which runs the daily checks), then their funding alerts."""
    on_day(monkeypatch, day)
    cache_module.cache.clear()  # a new day: the daily checks run again
    ok(client.get(f"{NOTIFICATIONS}/unread", headers=who.headers))
    wait_until_idle(timeout=10)
    alerts = ok(client.get(NOTIFICATIONS, headers=who.headers))["notifications"]
    return [a for a in alerts if a["kind"].startswith("funding.")]


# ------------------------------------------------------------------ the list


def test_save_see_and_unsave(client, lerato):
    nsfas = ok(client.put(f"{SAVED}/nsfas", headers=lerato.headers))["funder"]
    assert (nsfas["id"], nsfas["saved_on"], nsfas["status"], nsfas["days"]) == ("nsfas", "2026-10-12", "open", 19)
    assert ok(client.put(f"{SAVED}/nsfas", headers=lerato.headers))["funder"]["saved_on"] == "2026-10-12"  # again: fine
    ok(client.put(f"{SAVED}/thuthuka", json={}, headers=lerato.headers))
    ok(client.put(f"{SAVED}/funza_lushaka", headers=lerato.headers))

    data = ok(client.get(SAVED, headers=lerato.headers))
    assert data["today"] == "2026-10-12"
    assert data["summary"] == "3 funding options: 2 open now."
    assert [f["id"] for f in data["funders"]] == ["nsfas", "funza_lushaka", "thuthuka"]  # open first, soonest closing first
    assert all(f["saved_on"] == "2026-10-12" for f in data["funders"])
    assert (data["confirmed"], data["notice"]) == (False, "Not yet confirmed by the team.")

    assert ok(client.delete(f"{SAVED}/nsfas", headers=lerato.headers)) == {}
    assert saved_ids(client, lerato) == ["funza_lushaka", "thuthuka"]
    r = client.delete(f"{SAVED}/nsfas", headers=lerato.headers)
    assert r.status_code == 404 and r.get_json()["code"] == "SAVED_FUNDER_NOT_FOUND"


def test_a_funder_the_pack_doesnt_list_is_a_404_and_nothing_is_kept(app, client, lerato):
    for funder_id in ("hogwarts", "NSFAS", "nsfas'--", "x" * 300):
        r = client.put(f"{SAVED}/{funder_id}", headers=lerato.headers)
        assert r.status_code == 404 and r.get_json()["code"] == "FUNDER_NOT_FOUND"
        assert funder_id not in r.get_data(as_text=True)
    with app.app_context():
        assert db.session.execute(text("SELECT count(*) FROM student.saved_funders")).scalar() == 0


def test_each_student_sees_only_their_own(client, lerato, sipho):
    ok(client.put(f"{SAVED}/nsfas", headers=lerato.headers))
    assert saved_ids(client, sipho) == []
    r = client.delete(f"{SAVED}/nsfas", headers=sipho.headers)  # Sipho never saved it: Lerato's stays
    assert r.status_code == 404
    assert saved_ids(client, lerato) == ["nsfas"]


def test_saving_needs_an_account(client):
    assert client.get(SAVED).status_code == 401
    assert client.put(f"{SAVED}/nsfas").status_code == 401
    assert client.delete(f"{SAVED}/nsfas").status_code == 401


@pytest.mark.parametrize(
    "send",
    [
        {"query_string": {"status": "open"}},
        {"json": {"income": 350000}},  # never anything about the student
        {"json": {"race": "any"}},
        {"json": [1, 2]},
        {"json": "nsfas"},
        {"data": "not json", "content_type": "text/plain"},
    ],
)
def test_nothing_else_is_accepted(client, lerato, send):
    assert client.put(f"{SAVED}/nsfas", headers=lerato.headers, **send).status_code == 422
    assert saved_ids(client, lerato) == []


def test_a_student_can_save_up_to_the_cap(client, lerato, monkeypatch):
    monkeypatch.setattr(saved_funding_service, "MAX_SAVED", 2)
    ok(client.put(f"{SAVED}/nsfas", headers=lerato.headers))
    ok(client.put(f"{SAVED}/thuthuka", headers=lerato.headers))
    assert client.put(f"{SAVED}/csir", headers=lerato.headers).status_code == 422
    ok(client.put(f"{SAVED}/nsfas", headers=lerato.headers))  # one already saved still answers


def test_saved_funding_is_limited_per_student(client, lerato, sipho, limits_on):
    codes = [client.get(SAVED, headers=lerato.headers).status_code for _ in range(121)]
    assert codes[:120] == [200] * 120 and codes[120] == 429
    assert client.get(SAVED, headers=sipho.headers).status_code == 200  # each student has their own count
    codes = [client.put(f"{SAVED}/nsfas", headers=lerato.headers).status_code for _ in range(61)]
    assert codes[:60] == [200] * 60 and codes[60] == 429


# ---------------------------------------------------------------- the alerts


def test_an_alert_when_saved_funding_opens(client, lerato, monkeypatch):
    on_day(monkeypatch, date(2026, 9, 28))
    ok(client.put(f"{SAVED}/funza_lushaka", headers=lerato.headers))  # it opens on 1 Oct
    assert first_poll_of(client, lerato, monkeypatch, date(2026, 9, 30)) == []
    (alert,) = first_poll_of(client, lerato, monkeypatch, date(2026, 10, 2))
    assert (alert["kind"], alert["icon"], alert["title"]) == ("funding.open", "award", "Funding you saved is open")
    assert alert["body"] == "Funza Lushaka: applications for 2027 funding are open now."
    assert alert["link"] == {"type": "funding", "id": "funza_lushaka"}
    assert len(first_poll_of(client, lerato, monkeypatch, date(2026, 10, 3))) == 1  # once


def test_no_open_alert_for_funding_already_open_when_saved(client, lerato, monkeypatch):
    ok(client.put(f"{SAVED}/nsfas", headers=lerato.headers))  # open since 18 Sep
    assert first_poll_of(client, lerato, monkeypatch, date(2026, 10, 13)) == []


def test_alerts_a_week_and_a_day_before_it_closes(client, lerato, monkeypatch):
    ok(client.put(f"{SAVED}/nsfas", headers=lerato.headers))
    assert first_poll_of(client, lerato, monkeypatch, date(2026, 10, 23)) == []  # 8 days to go
    (week,) = first_poll_of(client, lerato, monkeypatch, date(2026, 10, 24))
    assert (week["kind"], week["title"]) == ("funding.closing", "Funding you saved closes soon")
    assert week["body"] == "NSFAS: applications for 2027 funding close in 7 days, on Sat 31 Oct 2026 at 23:59."
    assert len(first_poll_of(client, lerato, monkeypatch, date(2026, 10, 27))) == 1  # the same week: no repeat
    day_before, _ = first_poll_of(client, lerato, monkeypatch, date(2026, 10, 30))  # newest first
    assert day_before["body"] == "NSFAS: applications for 2027 funding close tomorrow, Sat 31 Oct 2026 at 23:59."
    assert len(first_poll_of(client, lerato, monkeypatch, date(2026, 11, 1))) == 2  # closed: nothing more


def test_unsaved_or_switched_off_funding_stays_quiet(client, lerato, sipho, monkeypatch):
    ok(client.put(f"{SAVED}/nsfas", headers=lerato.headers))
    ok(client.put(f"{SAVED}/nsfas", headers=sipho.headers))
    ok(client.put(f"{NOTIFICATIONS}/switches", json={"funding_reminders": False}, headers=sipho.headers))
    ok(client.delete(f"{SAVED}/nsfas", headers=lerato.headers))
    assert first_poll_of(client, lerato, monkeypatch, date(2026, 10, 24)) == []
    assert first_poll_of(client, sipho, monkeypatch, date(2026, 10, 24)) == []


def test_an_alert_names_only_its_funder_and_dates(app, client, lerato, monkeypatch):
    ok(client.put(f"{SAVED}/nsfas", headers=lerato.headers))
    first_poll_of(client, lerato, monkeypatch, date(2026, 10, 24))
    with app.app_context():
        (params,) = db.session.execute(text("SELECT params FROM platform.notifications WHERE kind LIKE 'funding.%'")).scalars()
    assert params == {"funder": "NSFAS", "intake": 2027, "when": "in 7 days, on Sat 31 Oct 2026 at 23:59"}


# ---------------------------------------------------------------- POPIA


def test_the_export_has_the_saved_funding(client, lerato):  # closing the account: test_privacy.py
    ok(client.put(f"{SAVED}/funza_lushaka", headers=lerato.headers))
    data = ok(client.get(f"{API}/me/export", headers=lerato.headers))
    assert data["saved_funding"] == {"saved": [{"funder": "funza_lushaka", "name": "Funza Lushaka", "saved_on": "2026-10-12"}]}
