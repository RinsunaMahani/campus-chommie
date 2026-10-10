"""
Notifications: an alert published anywhere lands once for its owner; the
list, the unread count and read state; nobody else's alerts; the 90-day
clean-up; the templates themselves.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from notification_helpers import BASE, listed, publish, student, unread
from src.domains.platform.notifications.jobs import cleanup_old
from src.domains.platform.notifications.models import Notification
from src.domains.platform.notifications.templates import TEMPLATES, placeholders, render
from src.extensions import db


@pytest.fixture
def me(client, outbox):
    return student(client, outbox, "lindiwe@example.com")


@pytest.fixture
def other(client, outbox):
    return student(client, outbox, "sipho@example.com")


def rows(app, who) -> list[Notification]:
    with app.app_context():
        return Notification.query.filter_by(user_id=uuid.UUID(who.id)).all()


# ------------------------------------------------------------------ access


@pytest.mark.parametrize(
    "method,path",
    [("get", BASE), ("get", f"{BASE}/unread"), ("post", f"{BASE}/{uuid.uuid4()}/read"), ("post", f"{BASE}/read-all")],
)
def test_every_route_needs_a_token(client, method, path):
    assert getattr(client, method)(path, json={}).status_code == 401


# ------------------------------------------------------------- publishing


def test_an_alert_lands_once(app, client, me):
    publish(me, "account.locked", dedupe="account:x:locked:1", link=("security", None), minutes=15)
    publish(me, "account.locked", dedupe="account:x:locked:1", link=("security", None), minutes=15)  # a retry
    publish(me, "account.new_phone", dedupe="account:x:phone:1")
    assert sorted(n.kind for n in rows(app, me)) == ["account.locked", "account.new_phone"]


@pytest.mark.parametrize(
    "template,params,link",
    [
        ("account.made_up", {}, None),  # no such template
        ("account.locked", {}, None),  # a param missing
        ("account.new_phone", {}, ("somewhere", "1")),  # a link the app can't open
    ],
)
def test_a_broken_alert_is_dropped_not_half_written(app, client, me, template, params, link):
    publish(me, template, link=link, **params)
    assert rows(app, me) == []


# ------------------------------------------------------------------ reading


def test_the_list_is_newest_first_rendered_and_paged(app, client, me):
    for minutes in (10, 20, 30, 40, 50):
        publish(me, "account.locked", dedupe=f"locked:{minutes}", link=("security", None), minutes=minutes)
    first = listed(client, me, limit=2)
    items = first["notifications"]
    assert [n["body"] for n in items] == [
        "Sign-in is paused for 50 minutes to keep your account safe. If that wasn't you, change your password.",
        "Sign-in is paused for 40 minutes to keep your account safe. If that wasn't you, change your password.",
    ]
    assert items[0]["title"] == "Account locked" and items[0]["icon"] == "alert-triangle"
    assert items[0]["link"] == {"type": "security", "id": None} and items[0]["read_at"] is None
    second = listed(client, me, limit=2, before=first["next_before"])
    third = listed(client, me, limit=2, before=second["next_before"])
    assert [n["body"].split()[4] for n in second["notifications"] + third["notifications"]] == ["30", "20", "10"]
    assert third["next_before"] is None


def test_the_unread_count_and_the_newest_id(client, me):
    assert unread(client, me) == {"count": 0, "latest_id": None}
    publish(me, "account.new_phone")
    publish(me, "account.password_changed")
    u = unread(client, me)
    assert u["count"] == 2 and u["latest_id"] == listed(client, me)["notifications"][0]["id"]


def test_reading_one_is_once_and_says_the_new_count(client, me):
    publish(me, "account.new_phone")
    n = listed(client, me)["notifications"][0]
    r = client.post(f"{BASE}/{n['id']}/read", headers=me.headers)
    body = r.get_json()["data"]
    assert r.status_code == 200 and body["notification"]["read_at"] and body["unread"]["count"] == 0
    again = client.post(f"{BASE}/{n['id']}/read", headers=me.headers).get_json()["data"]
    assert again["notification"]["read_at"] == body["notification"]["read_at"]


def test_read_all(client, me):
    publish(me, "account.new_phone")
    publish(me, "account.password_changed")
    r = client.post(f"{BASE}/read-all", headers=me.headers)
    assert r.status_code == 200 and r.get_json()["data"]["unread"]["count"] == 0


# --------------------------------------------------------------------- IDOR


def test_nobody_else_sees_or_marks_my_alerts(client, me, other):
    publish(me, "account.new_phone")
    mine = listed(client, me)["notifications"][0]
    assert listed(client, other)["notifications"] == []
    assert unread(client, other) == {"count": 0, "latest_id": None}
    assert client.post(f"{BASE}/{mine['id']}/read", headers=other.headers).status_code == 404
    assert client.get(BASE, headers=other.headers, query_string={"before": mine["id"]}).status_code == 404
    client.post(f"{BASE}/read-all", headers=other.headers)
    assert unread(client, me)["count"] == 1


# --------------------------------------------------------------- clean-up


def test_alerts_older_than_90_days_are_deleted(app, client, me):
    publish(me, "account.new_phone", dedupe="old")
    publish(me, "account.password_changed", dedupe="new")
    with app.app_context():
        old = Notification.query.filter_by(dedupe_key="old").one()
        old.created_at = datetime.now(timezone.utc) - timedelta(days=91)
        db.session.commit()
        result = cleanup_old.run()
    assert result.success and result.count == 1
    assert [n.dedupe_key for n in rows(app, me)] == ["new"]


# --------------------------------------------------------------- templates


SAMPLE = {"minutes": 15, "module": "ANA201", "kind": "test", "when": "on Tue 20 Oct 2026 at 08:00", "was": "on Mon 19 Oct 2026"}


@pytest.mark.parametrize("kind", sorted(TEMPLATES))
def test_every_template_renders_with_its_params(kind):
    title, body = render(kind, SAMPLE)
    assert title and body and "{" not in body and "{" not in title
    assert placeholders(TEMPLATES[kind]) <= {k.removesuffix("_cents") for k in SAMPLE}


def test_no_template_can_carry_an_ip_email_phone_or_personal_details():
    for kind, t in TEMPLATES.items():
        assert "{" not in t.title, kind  # titles are fixed text
        for name in placeholders(t):
            for banned in ("ip", "email", "phone", "address", "street", "name", "note", "device", "mark", "amount"):
                assert banned not in name.lower(), (kind, name)


def test_the_locked_alert_never_says_why():
    t = TEMPLATES["account.locked"]
    text = (t.title + " " + t.body).lower()
    assert "password 5" not in text and "wrong" not in text and "times" not in text


def test_a_stored_alert_whose_params_went_missing_still_renders(app, client, me):
    publish(me, "account.locked", minutes=15)
    with app.app_context():
        n = Notification.query.one()
        n.params = {}
        db.session.commit()
    body = listed(client, me)["notifications"][0]["body"]
    assert body == "Sign-in is paused for  minutes to keep your account safe. If that wasn't you, change your password."
    assert json.dumps(body)
