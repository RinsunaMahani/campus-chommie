"""
Notifications against someone trying things: odd ids, pages and bodies,
and limits counted per user.
"""
from __future__ import annotations

import pytest

from notification_helpers import BASE, student
from src.shared.rate_limit.limiter import limiter


@pytest.fixture
def me(client, outbox):
    return student(client, outbox, "lindiwe@example.com")


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
    "query,status",
    [
        ({"limit": "10000"}, 422),
        ({"limit": "0"}, 422),
        ({"limit": "ten"}, 422),
        ({"before": "not-a-uuid"}, 422),
        ({"user_id": "someone-else"}, 422),
        ({"tab": "inbox"}, 422),  # no such thing any more: unknown, refused
        ({"limit": "5\x00"}, 400),
    ],
)
def test_odd_list_queries_are_refused(client, me, query, status):
    assert client.get(BASE, headers=me.headers, query_string=query).status_code == status


def test_a_bad_id_is_a_404(client, me):
    assert client.post(f"{BASE}/not-a-uuid/read", headers=me.headers).status_code == 404


@pytest.mark.parametrize("body", [{"tab": "all"}, {"ids": ["x"]}, {"user_id": "someone-else"}])
def test_read_all_takes_no_fields(client, me, body):
    assert client.post(f"{BASE}/read-all", headers=me.headers, json=body).status_code == 422


def test_deep_json_is_refused(client, me):
    deep: dict = {}
    node = deep
    for _ in range(200):
        node["x"] = {}
        node = node["x"]
    assert client.post(f"{BASE}/read-all", headers=me.headers, json=deep).status_code in (400, 422)


def test_the_poll_is_limited_per_user(client, outbox, me, limits_on):
    other = student(client, outbox, "sipho@example.com")
    codes = [client.get(f"{BASE}/unread", headers=me.headers).status_code for _ in range(121)]
    assert codes[:120] == [200] * 120 and codes[120] == 429
    assert client.get(f"{BASE}/unread", headers=other.headers).status_code == 200
