"""
GET /me/week-review: the signed-in student's week in review, from their own records only: what's behind them, what's
coming, how their marks moved with the marks they entered this week, and their spending against their usual. On their
check-in day it's ready (and one alert says so); for two days after, Home offers last week's. Signed out, odd and
repeated queries refused; nobody else's records ever show.
"""
from __future__ import annotations

from datetime import UTC, date, datetime

import pytest
from sqlalchemy import update
from student_helpers import MONEY, on_day, student

from src.domains.student.academics.models import Assessment
from src.extensions import db
from src.shared.cache import cache as cache_module
from src.shared.queue.queue import wait_until_idle

API = "/api/v1"
REVIEW = f"{API}/me/week-review"
NOTIFICATIONS = f"{API}/me/notifications"
SUNDAY = date(2026, 10, 25)  # the default check-in day: the week is Mon 19 to Sun 25 October


@pytest.fixture(autouse=True)
def on_sunday(monkeypatch):
    on_day(monkeypatch, SUNDAY)


@pytest.fixture
def me(client, outbox):
    return student(client, outbox, "lerato@example.com")


@pytest.fixture
def other(client, outbox):
    return student(client, outbox, "sipho@example.com")


def ok(r):
    assert r.status_code in (200, 201), r.get_json()
    return r.get_json()["data"]


def review(client, who, query: str = "") -> dict:
    return ok(client.get(REVIEW + query, headers=who.headers))


def marked_on(app, name: str, when: datetime) -> None:
    """When the mark was saved: the review reads which marks are new from it."""
    with app.app_context():
        db.session.execute(update(Assessment).where(Assessment.name == name).values(updated_at=when))
        db.session.commit()


def a_full_week(app, client, who) -> None:
    for exam in ({"module": "STK110", "on": "2026-10-21", "starts": "09:00", "minutes": 120, "paper": "Semester test"},
                 {"module": "STK110", "on": "2026-10-29", "starts": "08:30", "minutes": 180, "paper": "Exam"}):
        ok(client.post(f"{API}/me/exams", json=exam, headers=who.headers))
    module = ok(client.post(f"{API}/academics/modules", json={"code": "STK110", "target": 60}, headers=who.headers))["module"]
    for name, mark in (("Test 1", 50), ("Test 2", 70)):
        ok(client.post(f"{API}/academics/modules/{module['id']}/assessments", json={"name": name, "weight": 20, "mark": mark},
                       headers=who.headers))
    marked_on(app, "Test 1", datetime(2026, 10, 10, 9, tzinfo=UTC))
    marked_on(app, "Test 2", datetime(2026, 10, 22, 9, tzinfo=UTC))
    for day, cents in (("2026-10-20", 30_000), ("2026-10-22", 20_000), ("2026-10-13", 80_000), ("2026-10-06", 80_000)):
        ok(client.put(f"{MONEY}/spending/{day}", json={"amount_cents": cents}, headers=who.headers))
    ok(client.post(f"{MONEY}/checkin", json={"amount_cents": 50_000, "skipped": False}, headers=who.headers))


# ------------------------------------------------------------------ requests


def test_signed_out_and_odd_requests_are_refused(client, me):
    assert client.get(REVIEW).status_code == 401
    for query in ("?week=next", "?week=2026-10-18", "?user=x", "?week=this&week=last", "?week="):
        assert client.get(REVIEW + query, headers=me.headers).status_code == 422, query


# ------------------------------------------------------------------ the review


def test_a_new_student_gets_a_quiet_week_and_how_to_fill_it(client, me):
    r = review(client, me)
    assert (r["week"], r["week_start"], r["week_end"], r["finished"], r["ready"]) == ("this", "2026-10-19", "2026-10-25", True, True)
    assert r["headline"] == "A quiet week. Add your classes, marks and money to see more here."
    assert r["done"] == r["coming"] == r["marks"] == [] and r["support"] is None
    assert r["spending"]["direction"] == "unknown"


def test_a_full_week_in_review(app, client, me):
    a_full_week(app, client, me)
    r = review(client, me)
    assert r["headline"] == "3 things done and 1 date in the next 7 days."
    assert [d["text"] for d in r["done"]] == [
        "STK110 Semester test (Wed 21 Oct at 09:00)",
        "You entered 1 mark: STK110 Test 2 (70%).",
        "You checked in on your money.",
    ]
    assert [c["text"] for c in r["coming"]] == ["STK110 Exam, in 4 days (Thu 29 Oct at 08:30)"]
    assert r["marks"] == [{"code": "STK110", "before": 50.0, "after": 60.0, "direction": "up",
                           "text": "STK110: your average went up from 50% to 60% with this week's marks."}]
    s = r["spending"]
    assert (s["spent_cents"], s["usual_cents"], s["direction"]) == (50_000, 80_000, "less")
    assert s["text"] == "You spent R500 this week, R300 less than your usual of about R800 (from the last 2 weeks)."
    assert s["weeks"] == [None, None, 80_000, 80_000, 50_000]
    assert r["support"] is None


def test_a_mark_that_went_down_points_to_support(app, client, me):
    module = ok(client.post(f"{API}/academics/modules", json={"code": "INF171", "target": 60}, headers=me.headers))["module"]
    for name, mark in (("Quiz 1", 80), ("Quiz 2", 40)):
        ok(client.post(f"{API}/academics/modules/{module['id']}/assessments", json={"name": name, "weight": 10, "mark": mark},
                       headers=me.headers))
    marked_on(app, "Quiz 1", datetime(2026, 10, 1, 9, tzinfo=UTC))
    marked_on(app, "Quiz 2", datetime(2026, 10, 23, 9, tzinfo=UTC))
    r = review(client, me)
    assert r["marks"][0]["direction"] == "down"
    assert r["support"] == "If a mark knocked you this week, your campus's tutoring and counselling are there to help."


def test_last_week_is_offered_for_two_days_after_the_check_in_day(app, client, me, monkeypatch):
    a_full_week(app, client, me)
    on_day(monkeypatch, date(2026, 10, 26))  # Monday
    r = review(client, me)
    assert (r["week"], r["week_end"], r["ready"]) == ("last", "2026-10-25", True)
    assert "STK110 Semester test (Wed 21 Oct at 09:00)" in [d["text"] for d in r["done"]]
    assert review(client, me, "?week=this")["week_end"] == "2026-11-01"

    on_day(monkeypatch, date(2026, 10, 28))  # Wednesday: three days on, the week under way instead
    r = review(client, me)
    assert (r["week"], r["week_end"], r["ready"], r["finished"]) == ("this", "2026-11-01", False, False)
    assert r["coming"][0]["text"] == "STK110 Exam, tomorrow (Thu 29 Oct at 08:30)"
    assert review(client, me, "?week=last")["week_end"] == "2026-10-25"


def test_nobody_elses_records_ever_show(app, client, me, other):
    a_full_week(app, client, me)
    r = review(client, other)
    assert r["done"] == r["coming"] == r["marks"] == []
    assert r["spending"]["spent_cents"] is None and "STK110" not in str(r)


# ------------------------------------------------------------------ the alert


def first_poll(client, who, monkeypatch, day: date) -> list[dict]:
    """The student's first poll on `day` (which runs the daily checks), then their week-in-review alerts."""
    on_day(monkeypatch, day)
    cache_module.cache.clear()  # a new day: the daily checks run again
    ok(client.get(f"{NOTIFICATIONS}/unread", headers=who.headers))
    wait_until_idle(timeout=10)
    return [a for a in ok(client.get(NOTIFICATIONS, headers=who.headers))["notifications"] if a["kind"] == "review.ready"]


def test_one_alert_on_the_check_in_day_when_the_week_has_something(app, client, me, monkeypatch):
    a_full_week(app, client, me)
    assert first_poll(client, me, monkeypatch, date(2026, 10, 24)) == []  # Saturday: not yet
    (alert,) = first_poll(client, me, monkeypatch, SUNDAY)
    assert alert["title"] == "Your week in review"
    assert alert["body"] == "See what you got done, what's coming up and how your money went this week."
    assert alert["link"] == {"type": "review", "id": "2026-10-25"}
    assert len(first_poll(client, me, monkeypatch, SUNDAY)) == 1  # once a week


def test_no_alert_for_an_empty_week_or_when_switched_off(app, client, me, other, monkeypatch):
    assert first_poll(client, other, monkeypatch, SUNDAY) == []  # nothing in it yet
    a_full_week(app, client, me)
    ok(client.put(f"{NOTIFICATIONS}/switches", json={"week_review": False}, headers=me.headers))
    assert first_poll(client, me, monkeypatch, SUNDAY) == []
