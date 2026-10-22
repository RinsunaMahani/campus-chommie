"""
Announcements to verified events, end to end, on Mon 12 Oct 2026. A member
pastes an announcement and gets back what we read, with what to check; only
a rep's confirmation makes it a verified event, and a student's stays
unverified until then. "Moved" and "cancelled" messages update the event and
record each change. Students flag events; reps see how many, never who. The
week strip scores verified events and shows the university's calendar, and
the brief's M3 check closes: the self-funded persona's heavy week makes his
life fund amber.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime

import pytest
from class_helpers import API, CLASSES, announce, confirm, join, make_class, personas, set_up_persona, student, verified_event

from src.domains.classes.classes.services import class_service
from src.domains.classes.events.models import Announcement, ClassEvent, EventChange
from src.domains.classes.events.services import events_service, week_service
from src.domains.student.money.services import money_service

TODAY = date(2026, 10, 12)  # a Monday


@pytest.fixture(autouse=True)
def on_12_october(monkeypatch):
    for module in (class_service, events_service, week_service, money_service):
        monkeypatch.setattr(module, "_today", lambda: TODAY)


@pytest.fixture
def rep(client, outbox):
    return student(client, outbox, "thabo@example.com")


@pytest.fixture
def classmate(client, outbox):
    return student(client, outbox, "naledi@example.com")


@pytest.fixture
def anatomy(client, rep, classmate):
    made = make_class(client, rep)
    join(client, classmate, made["invite_code"])
    return made


def events_of(client, who, class_id, **query) -> list[dict]:
    r = client.get(f"{CLASSES}/{class_id}/events", headers=who.headers, query_string=query)
    assert r.status_code == 200, r.get_json()
    return r.get_json()["data"]["events"]


def candidates_of(client, who, class_id) -> list[dict]:
    r = client.get(f"{CLASSES}/{class_id}/candidates", headers=who.headers)
    assert r.status_code == 200, r.get_json()
    return r.get_json()["data"]["candidates"]


TEST_2 = "ANA201 Test 2 on 20 Oct at 08:00, LT 3, worth 20%"


@pytest.mark.parametrize(
    "method, path",
    [
        ("post", f"/classes/{uuid.uuid4()}/announcements"), ("get", f"/classes/{uuid.uuid4()}/candidates"),
        ("post", f"/candidates/{uuid.uuid4()}/confirm"), ("post", f"/candidates/{uuid.uuid4()}/discard"),
        ("get", f"/classes/{uuid.uuid4()}/events"), ("post", f"/events/{uuid.uuid4()}/flag"),
        ("delete", f"/events/{uuid.uuid4()}/flag"), ("get", "/week"),
    ],
)
def test_every_events_route_needs_a_token(client, method, path):
    assert getattr(client, method)(f"{API}{path}", json={}).status_code == 401


def test_a_reps_announcement_goes_live_only_when_confirmed(client, rep, classmate, anatomy):
    candidate = announce(client, rep, anatomy["id"], TEST_2)
    assert candidate["confirmable"] is True and candidate["from_rep"] is True and candidate["yours"] is True
    assert candidate["read_as"] == {
        "kind": "test", "title": "Test 2", "module": "ANA201", "on": "2026-10-20", "at": "08:00",
        "venue": "LT 3", "weighting": 20.0, "change": None,
    }
    assert candidate["needs_check"] == []
    assert candidate["lines"] == ["We read this as: Test 2 for ANA201 on Tue 20 Oct 2026 at 08:00, LT 3, worth 20% of the mark."]
    assert events_of(client, classmate, anatomy["id"]) == []  # nothing is live yet

    done = confirm(client, rep, candidate)
    event = done["event"]
    assert (event["title"], event["on"], event["at"], event["venue"], event["verified"], event["version"]) == (
        "Test 2", "2026-10-20", "08:00", "LT 3", True, 1)
    assert done["lines"] == ["Test 2 on Tue 20 Oct 2026 at 08:00 is now a verified event for ANA201."]
    assert [e["id"] for e in events_of(client, classmate, anatomy["id"])] == [event["id"]]
    assert candidates_of(client, rep, anatomy["id"]) == []


def test_a_students_announcement_stays_unverified_until_a_rep_confirms(client, app, rep, classmate, anatomy, outbox):
    candidate = announce(client, classmate, anatomy["id"], "Guys the ANA201 quiz is on Friday 16 Oct")
    assert candidate["confirmable"] is False and candidate["yours"] is True
    assert candidate["lines"][-1] == events_service.WAITING_FOR_REP

    other = student(client, outbox, "lerato@example.com")
    join(client, other, anatomy["invite_code"])
    assert candidates_of(client, other, anatomy["id"]) == []  # a student sees only their own
    assert [c["id"] for c in candidates_of(client, classmate, anatomy["id"])] == [candidate["id"]]
    seen_by_rep = candidates_of(client, rep, anatomy["id"])
    assert [(c["id"], c["from_rep"], c["confirmable"], c["yours"]) for c in seen_by_rep] == [(candidate["id"], False, True, False)]
    assert seen_by_rep[0]["text"] == "Guys the ANA201 quiz is on Friday 16 Oct"

    own = candidate["proposed"] | {"event_id": None}
    r = client.post(f"{API}/candidates/{candidate['id']}/confirm", json=own, headers=classmate.headers)
    assert r.status_code == 403 and r.get_json()["code"] == "REP_ONLY"
    r = client.post(f"{API}/candidates/{candidate['id']}/confirm", json={"kind": "quiz", "on": "2026-10-16"}, headers=other.headers)
    assert r.status_code == 404  # not theirs to see
    assert events_of(client, classmate, anatomy["id"]) == []  # still unverified

    confirm(client, rep, seen_by_rep[0], title="Quiz 3", at="10:00")
    assert [(e["title"], e["at"]) for e in events_of(client, classmate, anatomy["id"])] == [("Quiz 3", "10:00")]
    assert candidates_of(client, classmate, anatomy["id"]) == []
    with app.app_context():
        assert Announcement.query.one().status == "confirmed"


def test_a_moved_message_updates_the_event_and_records_each_change(client, app, rep, classmate, anatomy):
    event = verified_event(client, rep, anatomy["id"], TEST_2)
    candidate = announce(client, rep, anatomy["id"], "ANA201 Test 2 moved to Thursday 22 Oct, 10:00, Room B4")
    assert candidate["read_as"]["change"] == "moved"
    assert candidate["changes_event"]["id"] == event["id"]
    assert candidate["lines"][0] == "We read this as: Test 2 on Tue 20 Oct 2026 moves to Thu 22 Oct 2026 at 10:00, Room B4."
    assert candidate["proposed"] | {"weighting": None} == {
        "change": "moved", "event_id": event["id"], "kind": "test", "title": "Test 2",
        "on": "2026-10-22", "at": "10:00", "venue": "Room B4", "weighting": None,
    }

    done = confirm(client, rep, candidate)
    assert done["lines"] == [
        "Moved from Tue 20 Oct 2026 to Thu 22 Oct 2026.",
        "Time changed from 08:00 to 10:00.",
        "Venue changed from LT 3 to Room B4.",
    ]
    moved = done["event"]
    assert (moved["id"], moved["on"], moved["at"], moved["venue"], moved["version"]) == (event["id"], "2026-10-22", "10:00", "Room B4", 2)
    seen = events_of(client, classmate, anatomy["id"])[0]
    assert [c["line"] for c in seen["changes"]] == done["lines"]
    assert [(c["field"], c["old"], c["new"]) for c in seen["changes"]] == [
        ("on", "2026-10-20", "2026-10-22"), ("at", "08:00", "10:00"), ("venue", "LT 3", "Room B4")]

    with app.app_context():
        rows = EventChange.query.order_by(EventChange.field).all()
        assert [(r.field, r.old, r.new) for r in rows] == [
            ("at", "08:00", "10:00"), ("on", "2026-10-20", "2026-10-22"), ("venue", "LT 3", "Room B4")]
        assert all(str(r.changed_by) == rep.id and r.announcement_id is not None for r in rows)
        assert ClassEvent.query.count() == 1  # changed, not doubled


def test_a_cancelled_message_cancels_the_event(client, app, rep, classmate, anatomy):
    event = verified_event(client, rep, anatomy["id"], TEST_2)
    candidate = announce(client, rep, anatomy["id"], "ANA201 test 2 has been cancelled")
    assert candidate["lines"][0] == "We read this as: Test 2 on Tue 20 Oct 2026 is cancelled."
    done = confirm(client, rep, candidate)
    assert done["lines"] == ["Cancelled."]
    assert (done["event"]["cancelled"], done["event"]["version"]) == (True, 2)
    with app.app_context():
        change = EventChange.query.one()
        assert (change.field, change.old, change.new) == ("cancelled", "no", "yes")

    week = client.get(f"{API}/week", headers=classmate.headers).get_json()["data"]["weeks"]
    assert all(w["events"] == [] for w in week)  # a cancelled event doesn't count
    again = announce(client, rep, anatomy["id"], "ANA201 test 2 moved to 23 Oct")
    r = client.post(f"{API}/candidates/{again['id']}/confirm",
                    json={"change": "moved", "event_id": event["id"], "kind": "test", "on": "2026-10-23"}, headers=rep.headers)
    assert r.status_code == 422 and r.get_json()["errors"][0]["event_id"] == ["That event is already cancelled."]


def test_a_change_that_names_no_event_waits_for_the_rep_to_choose(client, rep, anatomy):
    candidate = announce(client, rep, anatomy["id"], "The test has been postponed to 30 Oct")
    assert candidate["changes_event"] is None and candidate["proposed"]["event_id"] is None
    assert candidate["lines"][0] == "We read this as a change to an event, but couldn't tell which one: choose it before confirming."
    body = {"change": "moved", "kind": "test", "on": "2026-10-30"}
    r = client.post(f"{API}/candidates/{candidate['id']}/confirm", json=body, headers=rep.headers)
    assert r.status_code == 422 and "event_id" in r.get_json()["errors"][0]
    r = client.post(f"{API}/candidates/{candidate['id']}/confirm", json=body | {"event_id": str(uuid.uuid4())}, headers=rep.headers)
    assert r.status_code == 422 and r.get_json()["errors"][0]["event_id"] == ["Choose an event from this class."]

    event = verified_event(client, rep, anatomy["id"], TEST_2)
    same = {"change": "moved", "event_id": event["id"], "on": "2026-10-20", "at": "08:00", "venue": "LT 3"}
    r = client.post(f"{API}/candidates/{candidate['id']}/confirm", json=same, headers=rep.headers)
    assert r.status_code == 422 and "Nothing changes" in r.get_json()["errors"][0]["on"][0]
    done = confirm(client, rep, candidate | {"proposed": same | {"on": "2026-10-30"}})
    assert done["lines"] == ["Moved from Tue 20 Oct 2026 to Fri 30 Oct 2026."]


def test_a_rep_discards_and_a_student_takes_back(client, app, rep, classmate, anatomy, outbox):
    theirs = announce(client, classmate, anatomy["id"], "ANA201 test on 20 Oct")
    other = student(client, outbox, "lerato@example.com")
    join(client, other, anatomy["invite_code"])
    assert client.post(f"{API}/candidates/{theirs['id']}/discard", headers=other.headers).status_code == 404
    assert client.post(f"{API}/candidates/{theirs['id']}/discard", headers=rep.headers).status_code == 200
    taken_back = announce(client, classmate, anatomy["id"], "ANA201 quiz on 21 Oct")
    assert client.post(f"{API}/candidates/{taken_back['id']}/discard", headers=classmate.headers).status_code == 200
    assert candidates_of(client, rep, anatomy["id"]) == []
    assert client.post(f"{API}/candidates/{theirs['id']}/discard", headers=rep.headers).status_code == 404
    with app.app_context():
        assert sorted(a.status for a in Announcement.query) == ["discarded", "discarded"]


def test_flags_show_reps_how_many_and_why_never_who(client, rep, classmate, anatomy, outbox):
    event = verified_event(client, rep, anatomy["id"], TEST_2)
    other = student(client, outbox, "lerato@example.com")
    join(client, other, anatomy["invite_code"])

    r = client.post(f"{API}/events/{event['id']}/flag", json={"reason": "wrong_date"}, headers=classmate.headers)
    assert r.status_code == 200 and r.get_json()["data"]["event"]["your_flag"] == "wrong_date"
    assert "flags" not in r.get_json()["data"]["event"]  # counts are for reps
    client.post(f"{API}/events/{event['id']}/flag", json={"reason": "wrong_venue"}, headers=classmate.headers)  # changed mind
    client.post(f"{API}/events/{event['id']}/flag", json={"reason": "wrong_venue"}, headers=other.headers)

    seen = events_of(client, rep, anatomy["id"])[0]
    assert seen["flags"] == {"count": 2, "reasons": {"wrong_venue": 2}}
    assert classmate.id not in str(seen) and other.id not in str(seen)

    r = client.delete(f"{API}/events/{event['id']}/flag", headers=classmate.headers)
    assert r.status_code == 200 and r.get_json()["data"]["event"]["your_flag"] is None
    r = client.delete(f"{API}/events/{event['id']}/flag", headers=classmate.headers)
    assert r.status_code == 404 and r.get_json()["code"] == "FLAG_NOT_FOUND"


def test_the_events_window(client, rep, classmate, anatomy):
    verified_event(client, rep, anatomy["id"], TEST_2)
    verified_event(client, rep, anatomy["id"], "ANA201 exam on 9 Nov 2026 at 09:00")
    assert len(events_of(client, classmate, anatomy["id"])) == 2  # a week back to four months ahead
    assert [e["title"] for e in events_of(client, classmate, anatomy["id"], **{"from": "2026-11-01"})] == ["Exam"]
    assert events_of(client, classmate, anatomy["id"], **{"from": "2026-10-01", "to": "2026-10-19"}) == []


def test_the_week_strip(client, rep, classmate, anatomy):
    assert client.put(f"{API}/me/profile", json={"university": "up", "campus": "hatfield"}, headers=classmate.headers).status_code == 200
    verified_event(client, rep, anatomy["id"], "ANA201 quiz on Wed 14 Oct, 10:00, worth 5%")
    verified_event(client, rep, anatomy["id"], TEST_2)
    verified_event(client, rep, anatomy["id"], "ANA201 assignment 3 due 23/10 at 23:59, worth 15%")

    data = client.get(f"{API}/week", headers=classmate.headers).get_json()["data"]
    weeks = data["weeks"]
    assert (data["today"], data["classes"], data["notes"], len(weeks)) == ("2026-10-12", 1, [], 8)
    uni = data["university"]
    assert (uni["id"], uni["name"], uni["confirmed"]) == ("up", "University of Pretoria", False)
    assert uni["notice"].startswith("From the University of Pretoria's own documents, last read on ")
    first, second = weeks[0], weeks[1]
    assert (first["week_start"], first["week_end"], first["this_week"], first["load"]) == ("2026-10-12", "2026-10-18", True, "Manageable")
    assert [e["title"] for e in first["events"]] == ["Quiz"]
    assert (second["load"], second["colour"], second["this_week"]) == ("Busy", "amber", False)
    assert second["reason"] == "Busy: 1 test and 1 assignment."
    # The calendar is Hatfield's, beside the score and never in it.
    names = [c["name"] for c in first["calendar"]]
    assert "Test week 2, semester 2" in names and "Semester 2 lectures" in names
    assert any(c["name"].startswith("Exams: semester 2") for c in weeks[3]["calendar"])  # 2 to 8 Nov
    assert all(c["source_url"].startswith("https://") for w in weeks for c in w["calendar"])

    later = client.get(f"{API}/week?weeks=2&from=2026-11-09", headers=classmate.headers).get_json()["data"]["weeks"]
    assert [w["week_start"] for w in later] == ["2026-11-09", "2026-11-16"]


def test_the_week_says_whats_missing(client, classmate):
    data = client.get(f"{API}/week", headers=classmate.headers).get_json()["data"]
    assert data["notes"] == [week_service.NO_CLASSES, week_service.NO_UNIVERSITY]
    assert data["university"] is None
    assert all(w["load"] == "Manageable" and w["reason"] == "Nothing due this week." for w in data["weeks"])


def _persona_week(client, outbox, who, persona_id, university, campus):
    """The persona's classes, made by a classmate who's their rep, and each event confirmed by that rep."""
    _, people = personas()
    p = people[persona_id]
    assert client.put(f"{API}/me/profile", json={"university": university, "campus": campus}, headers=who.headers).status_code == 200
    rep = student(client, outbox, f"rep-{persona_id}@example.com")
    classes = {}
    for event in p["events"]:
        if event["module"] not in classes:
            made = make_class(client, rep, university=university, campus=campus, module_code=event["module"])
            join(client, who, made["invite_code"])
            classes[event["module"]] = made["id"]
        starts = datetime.strptime(event["starts"], "%Y-%m-%d %H:%M")
        candidate = announce(client, rep, classes[event["module"]], f"{event['module']} {event['title']}")
        confirm(client, rep, candidate, change=None, kind=event["kind"], title=event["title"],
                on=starts.date().isoformat(), at=f"{starts:%H:%M}", weighting=event["weighting"], venue=None)


def test_the_self_funded_personas_heavy_week_makes_his_life_fund_amber(client, outbox):
    """The brief's M3 check, which needed M4's week: Sipho (fictional) has his money in hand, but two
    tests' worth of work lands within two days of each other."""
    sipho = student(client, outbox, "sipho@example.com")
    set_up_persona(client, sipho, "sipho")
    _persona_week(client, outbox, sipho, "sipho", "up", "hatfield")

    summary = client.get(f"{API}/money/summary", headers=sipho.headers).get_json()["data"]
    assert summary["life_fund"]["state"] == "amber"
    assert summary["life_fund"]["reason"] == "Go easy: it's a heavy week."
    assert summary["this_week"]["colour"] == "red"
    assert money_service.WEEK_NOT_YET not in summary["notes"]
    assert summary["runway"]["short_before_next"] is False  # the money itself is fine
    week = client.get(f"{API}/week", headers=sipho.headers).get_json()["data"]["weeks"]
    assert week[0]["load"] == "Heavy" and len(week[0]["events"]) == 3


def test_the_allowance_funded_persona_has_a_heavy_week_ahead(client, outbox):
    naledi = student(client, outbox, "naledi@example.com")
    set_up_persona(client, naledi, "naledi")
    _persona_week(client, outbox, naledi, "naledi", "smu", "ga_rankuwa")
    week = client.get(f"{API}/week", headers=naledi.headers).get_json()["data"]["weeks"]
    assert [w["load"] for w in week[:2]] == ["Manageable", "Heavy"]
    assert any(c["period"] == "exam" for c in week[0]["calendar"])  # SMU's exams run from 12 Oct
    summary = client.get(f"{API}/money/summary", headers=naledi.headers).get_json()["data"]
    assert summary["life_fund"]["state"] == "paused"  # short money comes first
