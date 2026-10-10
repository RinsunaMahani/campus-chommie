"""
Class updates as alerts. When a rep confirms a new, moved or cancelled
event, every other member of the class gets one alert, the rep who
confirmed it none, and nobody outside the class anything. The wording is
fixed: the module, the kind and the dates, never who and never what
someone typed (a title or a venue). A student can switch class updates
off, and back on; security alerts have no switch.
"""
from __future__ import annotations

from datetime import date

import pytest
from class_helpers import API, CLASSES, announce, confirm, join, make_class, student, verified_event
from sqlalchemy import text

from src.domains.classes.classes.services import class_service
from src.domains.classes.events.services import events_service
from src.domains.platform.notifications.templates import LINK_TYPES, TEMPLATES
from src.extensions import db
from src.shared.queue.queue import wait_until_idle

TODAY = date(2026, 10, 12)
NOTIFICATIONS = f"{API}/me/notifications"
SWITCHES = f"{NOTIFICATIONS}/switches"
TEST_2 = "ANA201 Test 2 on 20 Oct at 08:00, LT 3, worth 20%"


@pytest.fixture(autouse=True)
def on_12_october(monkeypatch):
    for module in (class_service, events_service):
        monkeypatch.setattr(module, "_today", lambda: TODAY)


@pytest.fixture
def rep(client, outbox):
    return student(client, outbox, "thabo@example.com")


@pytest.fixture
def classmate(client, outbox):
    return student(client, outbox, "naledi@example.com")


@pytest.fixture
def outsider(client, outbox):
    return student(client, outbox, "sipho@example.com")


@pytest.fixture
def anatomy(client, rep, classmate):
    made = make_class(client, rep)
    join(client, classmate, made["invite_code"])
    return made


def alerts(client, who) -> list[dict]:
    wait_until_idle(timeout=10)
    r = client.get(NOTIFICATIONS, headers=who.headers)
    assert r.status_code == 200, r.get_json()
    return [n for n in r.get_json()["data"]["notifications"] if n["kind"].startswith("class.")]


def test_classmates_hear_about_a_new_event_and_the_rep_doesnt(client, rep, classmate, outsider, anatomy):
    verified_event(client, rep, anatomy["id"], TEST_2)
    got = alerts(client, classmate)
    assert [(a["kind"], a["title"], a["body"]) for a in got] == [
        ("class.event_new", "New date from your class", "ANA201: a new test on Tue 20 Oct 2026 at 08:00.")]
    assert got[0]["link"] == {"type": "class", "id": anatomy["id"]} and got[0]["icon"] == "calendar"
    assert alerts(client, rep) == [] and alerts(client, outsider) == []


def test_an_assignment_is_due(client, rep, classmate, anatomy):
    verified_event(client, rep, anatomy["id"], "ANA201 assignment 3 due 23/10 at 23:59")
    assert alerts(client, classmate)[0]["body"] == "ANA201: a new assignment due Fri 23 Oct 2026 at 23:59."


def test_a_moved_event_says_from_when_to_when(client, rep, classmate, anatomy):
    verified_event(client, rep, anatomy["id"], TEST_2)
    confirm(client, rep, announce(client, rep, anatomy["id"], "ANA201 Test 2 moved to Thursday 22 Oct, 10:00, Room B4"))
    newest = alerts(client, classmate)[0]
    assert (newest["kind"], newest["title"]) == ("class.event_moved", "A class date moved")
    assert newest["body"] == "ANA201: the test on Tue 20 Oct 2026 at 08:00 is now on Thu 22 Oct 2026 at 10:00."


def test_a_new_venue_alone_never_names_the_venue(client, rep, classmate, anatomy):
    event = verified_event(client, rep, anatomy["id"], TEST_2)
    candidate = announce(client, rep, anatomy["id"], "Venue change: the ANA201 test 2 moves to Room B4")
    confirm(client, rep, candidate, change="moved", event_id=event["id"], on="2026-10-20", at="08:00", venue="Room B4")
    newest = alerts(client, classmate)[0]
    assert newest["kind"] == "class.event_changed"
    assert newest["body"] == "ANA201: the test on Tue 20 Oct 2026 at 08:00 has a change. Check where and when."
    assert "Room B4" not in newest["body"] and "LT 3" not in newest["body"]


def test_a_cancelled_event(client, rep, classmate, anatomy):
    verified_event(client, rep, anatomy["id"], TEST_2)
    confirm(client, rep, announce(client, rep, anatomy["id"], "ANA201 test 2 has been cancelled"))
    newest = alerts(client, classmate)[0]
    assert (newest["kind"], newest["icon"]) == ("class.event_cancelled", "x-circle")
    assert newest["body"] == "ANA201: the test on Tue 20 Oct 2026 at 08:00 is cancelled."


def test_a_students_own_announcement_tells_them_once_a_rep_confirms(client, rep, classmate, anatomy):
    candidate = announce(client, classmate, anatomy["id"], "ANA201 quiz on 16 Oct at 10:00")
    assert alerts(client, classmate) == []  # waiting for a rep: nothing yet
    seen = client.get(f"{CLASSES}/{anatomy['id']}/candidates", headers=rep.headers).get_json()["data"]["candidates"]
    confirm(client, rep, seen[0])
    assert [a["body"] for a in alerts(client, classmate)] == ["ANA201: a new quiz on Fri 16 Oct 2026 at 10:00."]
    assert candidate["id"] == seen[0]["id"]


def test_alerts_never_say_who_or_repeat_typed_words(client, rep, classmate, anatomy):
    verified_event(client, rep, anatomy["id"], TEST_2, title="Test 2 (bring calculators, see Mr X)")
    text_of = str(alerts(client, classmate))
    assert "thabo" not in text_of and rep.id not in text_of
    assert "calculators" not in text_of and "LT 3" not in text_of


# ----------------------------------------------------------------- switches


def test_switches_start_on_and_can_be_turned_off_and_on(client, rep, classmate, anatomy):
    r = client.get(SWITCHES, headers=classmate.headers)
    assert r.status_code == 200
    assert r.get_json()["data"]["switches"] == [
        {"topic": "class_updates", "label": "New, moved and cancelled tests and deadlines from your class reps", "on": True}]

    r = client.put(SWITCHES, json={"class_updates": False}, headers=classmate.headers)
    assert r.status_code == 200 and r.get_json()["data"]["switches"][0]["on"] is False
    verified_event(client, rep, anatomy["id"], TEST_2)
    assert alerts(client, classmate) == []  # switched off: nothing

    client.put(SWITCHES, json={"class_updates": True}, headers=classmate.headers)
    verified_event(client, rep, anatomy["id"], "ANA201 quiz on 21 Oct at 10:00")
    assert [a["kind"] for a in alerts(client, classmate)] == ["class.event_new"]


def test_switching_off_is_mine_alone(client, rep, classmate, anatomy, outbox):
    other = student(client, outbox, "lerato@example.com")
    join(client, other, anatomy["invite_code"])
    client.put(SWITCHES, json={"class_updates": False}, headers=classmate.headers)
    verified_event(client, rep, anatomy["id"], TEST_2)
    assert alerts(client, classmate) == [] and len(alerts(client, other)) == 1


@pytest.mark.parametrize(
    "body",
    [None, {}, {"class_updates": 0}, {"class_updates": "false"}, {"class_updates": None}, {"security": False},
     {"class_updates": False, "marketing": True}],
)
def test_odd_switch_changes_are_refused(client, classmate, body):
    r = client.put(SWITCHES, json=body, headers=classmate.headers) if body is not None else client.put(
        SWITCHES, headers=classmate.headers)
    assert r.status_code == 422


def test_switch_routes_need_a_token_and_take_no_query(client, classmate):
    assert client.get(SWITCHES).status_code == 401
    assert client.put(SWITCHES, json={"class_updates": False}).status_code == 401
    assert client.get(f"{SWITCHES}?topic=class_updates", headers=classmate.headers).status_code == 422


def test_the_export_has_the_switches(client, classmate):
    client.put(SWITCHES, json={"class_updates": False}, headers=classmate.headers)
    data = client.get(f"{API}/me/export", headers=classmate.headers).get_json()["data"]
    assert data["alert_switches"] == {"class_updates": False}


def test_the_database_allows_every_template_and_link(app):
    """A new template or link type needs a migration: the alerts table checks both."""
    with app.app_context():
        rules = dict(db.session.execute(text(
            "SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint "
            "WHERE conname IN ('ck_notifications_kind', 'ck_notifications_link_type')"
        )).all())
    for kind in TEMPLATES:
        assert f"'{kind}'" in rules["ck_notifications_kind"], kind
    for link in LINK_TYPES:
        assert f"'{link}'" in rules["ck_notifications_link_type"], link
