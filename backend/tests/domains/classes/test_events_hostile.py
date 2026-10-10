"""
Class events against someone trying things: odd announcements and
confirmations (unknown fields, a "verified" flag, impossible times, dates a
year out), a rep's role carried into a class where they're only a student,
other classes' candidates and events (the same 404 as ones that don't
exist), floods, and the clean-up of old announcement text and flags.
"""
from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta

import pytest
from class_helpers import API, CLASSES, announce, join, make_class, student, verified_event

from src.domains.classes.classes.services import class_service
from src.domains.classes.events.jobs import forget_old_announcements
from src.domains.classes.events.models import Announcement, ClassEvent, EventCandidate, EventFlag
from src.domains.classes.events.services import events_service, week_service
from src.extensions import db
from src.shared.rate_limit.limiter import limiter

TODAY = date(2026, 10, 12)
TEST_2 = "ANA201 Test 2 on 20 Oct at 08:00, LT 3, worth 20%"
NEW_EVENT = {"kind": "test", "title": "Test 2", "on": "2026-10-20", "at": "08:00", "venue": "LT 3", "weighting": 20}


@pytest.fixture(autouse=True)
def on_12_october(monkeypatch):
    for module in (class_service, events_service, week_service):
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


def post_confirm(client, who, candidate_id, body):
    return client.post(f"{API}/candidates/{candidate_id}/confirm", json=body, headers=who.headers)


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"text": ""},
        {"text": "   "},
        {"text": "x" * 2001},
        {"text": 42},
        {"text": "ANA201 test", "sent_on": "2026-10-13"},  # the future
        {"text": "ANA201 test", "sent_on": "2026-08-12"},  # more than 60 days back
        {"text": "ANA201 test", "sent_on": "12/10/2026"},
        {"text": "ANA201 test", "status": "confirmed"},
        {"text": "ANA201 test", "verified": True},
        {"text": "ANA201 test", "submitted_by": str(uuid.uuid4())},
    ],
)
def test_odd_announcements_are_refused(client, classmate, anatomy, body):
    assert client.post(f"{CLASSES}/{anatomy['id']}/announcements", json=body, headers=classmate.headers).status_code == 422


@pytest.mark.parametrize(
    "change",
    [
        {"change": "postponed"},
        {"kind": "lecture"},
        {"kind": None},
        {"on": None},
        {"on": "20/10/2026"},
        {"on": "2027-10-21"},  # more than a year away
        {"on": "2026-09-10"},  # more than 31 days ago
        {"at": "8am"},
        {"at": "24:00"},
        {"at": "10:60"},
        {"at": "10:00:00"},
        {"weighting": 0},
        {"weighting": 101},
        {"weighting": "20"},
        {"weighting": True},
        {"title": "   "},
        {"title": "x" * 81},
        {"venue": "x" * 81},
        {"module": "PHY121"},  # the class says the module
        {"verified_by": str(uuid.uuid4())},
        {"event_id": str(uuid.uuid4())},  # a new event changes nothing
        {"event_id": "not-a-uuid"},
    ],
)
def test_odd_confirmations_are_refused(client, rep, anatomy, change):
    candidate = announce(client, rep, anatomy["id"], TEST_2)
    assert post_confirm(client, rep, candidate["id"], NEW_EVENT | change).status_code == 422


@pytest.mark.parametrize("body", [{}, {"reason": "spam"}, {"reason": "wrong_date", "note": "it's Tuesday"}, {"reason": 1}])
def test_odd_flags_are_refused(client, rep, classmate, anatomy, body):
    event = verified_event(client, rep, anatomy["id"], TEST_2)
    assert client.post(f"{API}/events/{event['id']}/flag", json=body, headers=classmate.headers).status_code == 422


@pytest.mark.parametrize(
    "path",
    [
        "/candidates?all=1",
        "/events?from=yesterday",
        "/events?from=2026-10-20&to=2026-10-19",
        "/events?from=2026-01-01&to=2027-06-01",  # more than 366 days
        "/events?user_id=1",
    ],
)
def test_odd_class_queries_are_refused(client, classmate, anatomy, path):
    assert client.get(f"{CLASSES}/{anatomy['id']}{path}", headers=classmate.headers).status_code == 422


@pytest.mark.parametrize("query", ["weeks=0", "weeks=17", "weeks=abc", "from=2028-01-01", "from=12-10-2026", "class_id=x"])
def test_odd_week_queries_are_refused(client, classmate, query):
    assert client.get(f"{API}/week?{query}", headers=classmate.headers).status_code == 422


def test_odd_discard_bodies_are_refused(client, rep, anatomy):
    candidate = announce(client, rep, anatomy["id"], TEST_2)
    r = client.post(f"{API}/candidates/{candidate['id']}/discard", json={"reason": "spam"}, headers=rep.headers)
    assert r.status_code == 422


def test_another_classes_candidates_and_events_are_not_found(client, rep, classmate, outsider, anatomy):
    """The outsider is a rep too, of their own class: being a rep somewhere opens nothing elsewhere."""
    physiology = make_class(client, outsider, module_code="PHY121")
    event = verified_event(client, rep, anatomy["id"], TEST_2)
    candidate = announce(client, classmate, anatomy["id"], "ANA201 quiz on 16 Oct")

    r = client.post(f"{CLASSES}/{anatomy['id']}/announcements", json={"text": "ANA201 test"}, headers=outsider.headers)
    assert r.status_code == 404 and r.get_json()["code"] == "CLASS_NOT_FOUND"
    assert client.get(f"{CLASSES}/{anatomy['id']}/candidates", headers=outsider.headers).status_code == 404
    assert client.get(f"{CLASSES}/{anatomy['id']}/events", headers=outsider.headers).status_code == 404
    r = post_confirm(client, outsider, candidate["id"], {"kind": "quiz", "on": "2026-10-16"})
    assert r.status_code == 404 and r.get_json()["code"] == "CANDIDATE_NOT_FOUND"
    assert client.post(f"{API}/candidates/{candidate['id']}/discard", headers=outsider.headers).status_code == 404
    r = client.post(f"{API}/events/{event['id']}/flag", json={"reason": "other"}, headers=outsider.headers)
    assert r.status_code == 404 and r.get_json()["code"] == "EVENT_NOT_FOUND"
    assert client.delete(f"{API}/events/{event['id']}/flag", headers=outsider.headers).status_code == 404

    # Their own class can't reach into this one either.
    own = announce(client, outsider, physiology["id"], "PHY121 test 1 moved to 23 Oct")
    r = post_confirm(client, outsider, own["id"], {"change": "moved", "event_id": event["id"], "on": "2026-10-23"})
    assert r.status_code == 422 and r.get_json()["errors"][0]["event_id"] == ["Choose an event from this class."]
    week = client.get(f"{API}/week", headers=outsider.headers).get_json()["data"]["weeks"]
    assert all(w["events"] == [] for w in week)

    # ...and nothing here changed.
    assert [(e["title"], e["on"], e["cancelled"]) for e in client.get(
        f"{CLASSES}/{anatomy['id']}/events", headers=classmate.headers).get_json()["data"]["events"]] == [("Test 2", "2026-10-20", False)]


def test_a_reps_role_stays_in_their_own_class(client, rep, outsider):
    physiology = make_class(client, outsider, module_code="PHY121")
    join(client, rep, physiology["invite_code"])  # a rep elsewhere, a student here
    own = announce(client, rep, physiology["id"], "PHY121 test 1 on 23 Oct")
    assert own["confirmable"] is False
    r = post_confirm(client, rep, own["id"], {"kind": "test", "on": "2026-10-23"})
    assert r.status_code == 403 and r.get_json()["code"] == "REP_ONLY"
    r = client.post(f"{CLASSES}/{physiology['id']}/reps", headers=rep.headers)
    assert r.status_code == 403


def test_leaving_a_class_closes_it(client, rep, classmate, anatomy):
    event = verified_event(client, rep, anatomy["id"], TEST_2)
    client.delete(f"{CLASSES}/{anatomy['id']}/membership", headers=classmate.headers)
    assert client.get(f"{CLASSES}/{anatomy['id']}/events", headers=classmate.headers).status_code == 404
    assert client.post(f"{API}/events/{event['id']}/flag", json={"reason": "other"}, headers=classmate.headers).status_code == 404


def test_unknown_ids_are_the_same_404(client, rep, anatomy):
    assert client.get(f"{CLASSES}/{uuid.uuid4()}/events", headers=rep.headers).status_code == 404
    assert post_confirm(client, rep, uuid.uuid4(), NEW_EVENT).status_code == 404
    assert client.post(f"{API}/candidates/{uuid.uuid4()}/discard", headers=rep.headers).status_code == 404
    assert client.post(f"{API}/events/{uuid.uuid4()}/flag", json={"reason": "other"}, headers=rep.headers).status_code == 404
    assert client.post(f"{API}/candidates/not-a-uuid/confirm", json=NEW_EVENT, headers=rep.headers).status_code == 404


def test_a_student_can_have_so_many_messages_waiting(client, rep, classmate, anatomy, monkeypatch):
    monkeypatch.setattr(events_service, "MAX_PENDING", 2)
    for text in ("ANA201 quiz on 16 Oct", "ANA201 test on 20 Oct"):
        announce(client, classmate, anatomy["id"], text)
    r = client.post(f"{CLASSES}/{anatomy['id']}/announcements", json={"text": "ANA201 prac on 22 Oct"}, headers=classmate.headers)
    assert r.status_code == 422 and "text" in r.get_json()["errors"][0]
    for text in ("ANA201 quiz on 16 Oct", "ANA201 test on 20 Oct", "ANA201 prac on 22 Oct"):
        announce(client, rep, anatomy["id"], text)  # a rep pasting the semester's dates isn't held back


def test_announcements_are_limited_per_student(client, app, rep, classmate, anatomy):
    limiter.enabled = True
    with app.app_context():
        limiter.reset()
    try:
        url = f"{CLASSES}/{anatomy['id']}/announcements"
        codes = [client.post(url, json={"text": ""}, headers=classmate.headers).status_code for _ in range(61)]
        assert codes[:60] == [422] * 60 and codes[60] == 429
        assert client.post(url, json={"text": TEST_2}, headers=rep.headers).status_code == 201
    finally:
        with app.app_context():
            limiter.reset()
        limiter.enabled = False


def test_old_text_undecided_announcements_and_old_flags_are_forgotten(app, rep, anatomy):
    now = datetime.now(UTC)  # the job's own clock
    with app.app_context():
        class_id, user_id = uuid.UUID(anatomy["id"]), uuid.UUID(rep.id)

        def add(status, *, decided=None, created=0):
            row = Announcement(
                class_id=class_id, submitted_by=user_id, raw_text=f"{status} {decided} {created}", sent_on=TODAY,
                status=status, decided_at=now - timedelta(days=decided) if decided is not None else None,
                created_at=now - timedelta(days=created),
            )
            db.session.add(row)
            return row

        old, recent = add("confirmed", decided=31), add("discarded", decided=29)
        stale, fresh = add("pending", created=61), add("pending", created=59)
        db.session.flush()
        db.session.add(EventCandidate(announcement_id=stale.id, class_id=class_id, from_rep=True, confidence={}, notes=[]))
        event = ClassEvent(class_id=class_id, kind="test", title="Test 1", module="ANA201", on_date=TODAY)
        db.session.add(event)
        db.session.flush()
        db.session.add(EventFlag(event_id=event.id, user_id=user_id, reason="other", updated_at=now - timedelta(days=366)))
        db.session.commit()
        ids = {"old": old.id, "recent": recent.id, "stale": stale.id, "fresh": fresh.id}

        result = forget_old_announcements.run()
        assert result.success and result.count == 3
        texts = {name: getattr(db.session.get(Announcement, i), "raw_text", "gone") for name, i in ids.items()}
        assert texts == {"old": None, "recent": "discarded 29 0", "stale": "gone", "fresh": "pending None 59"}
        assert EventCandidate.query.count() == 0 and EventFlag.query.count() == 0
