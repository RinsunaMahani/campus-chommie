"""
OWASP A10 (mishandling of exceptional conditions), for every route at once: broken, oddly shaped or badly encoded
input gets a refusal in our envelope with a stable code, never a crash. Read from the app's own URL map, so a new
route is covered the day it's added (security sweep 3, docs/SECURITY.md).

The testing config re-raises unhandled errors, so a route that would answer 500 in production fails here with its
traceback. Ids in paths are random, so nothing real is found, changed or deleted; the student is signed in so the
hostile input reaches the code behind auth_required.
"""
from __future__ import annotations

import re
import uuid

import pytest

from tests.domains.platform.notification_helpers import student

#: Bodies no client of ours sends: (label, raw bytes, content type).
BODIES = [
    ("broken JSON", b'{"label": ', "application/json"),
    ("a list", b"[1, 2, 3]", "application/json"),
    ("null", b"null", "application/json"),
    ("a bare string", b'"x"', "application/json"),
    ("a bare number", b"1e400", "application/json"),
    ("not UTF-8", b'{"label": "\xff\xfe"}', "application/json"),
    ("a lone surrogate", b'{"label": "\\ud800", "title": "\\ud800", "name": "\\udfff", "email": "\\ud800@x.test"}', "application/json"),
    ("operator objects", b'{"email": {"$ne": null}, "password": {"$gt": ""}, "id": {"$where": "1"}}', "application/json"),
    ("every field the wrong type", b'{"amount_cents": [], "weekday": {}, "starts": 9, "on": true, "code": null}', "application/json"),
    ("form-encoded", b"email=a%40b.c&password=x", "application/x-www-form-urlencoded"),
    ("plain text", b"hello", "text/plain"),
    ("XML", b'<?xml version="1.0"?><!DOCTYPE x [<!ENTITY e SYSTEM "file:///etc/passwd">]><x>&e;</x>', "application/xml"),
]

#: Query strings no client of ours sends, for the routes that read one.
QUERIES = [
    "week=%ED%A0%80",  # a lone surrogate, UTF-8 encoded
    "week=%FF%FE",  # not UTF-8
    "limit=99999999999999999999999999&offset=-1",
    "since=2026-02-30&until=not-a-date",
    "q=" + "x" * 5000,
    "field=%27%20OR%201%3D1%20--&university=../../etc/passwd",
    "a[]=1&a[]=2&a[$ne]=x",
]

SKIP = {"/static/<path:filename>"}


#: Text ids no client of ours sends, for the routes whose id is any string.
ODD_IDS = ["x%00y", "%ED%A0%80", "%FF%FE", "..%2F..%2Fetc%2Fpasswd", "x" * 3000, "2026-02-30", "%27%20OR%201%3D1%20--"]


def _path(rule, odd: str = "nope") -> str:
    """The rule with every variable filled: a random UUID where one is expected, `odd` where any string goes. The
    default is merely unknown, so the body and query tests reach the code behind the route."""

    def fill(m: re.Match) -> str:
        if m.group(1) == "uuid":
            return str(uuid.uuid4())
        return "2026-10-01" if m.group(2) == "spent_on" and odd == "nope" else odd

    return re.sub(r"<(?:(\w+):)?(\w+)>", fill, rule.rule)


def _routes(app):
    for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
        if rule.rule in SKIP:
            continue
        for method in sorted(rule.methods - {"HEAD", "OPTIONS"}):
            yield method, rule


def _try(client, failures: list, what: str, path: str, **kw) -> None:
    """One request; anything but a refusal in our envelope (status, success false, a stable code) is a failure."""
    try:
        r = client.open(path, **kw)
    except Exception as e:  # the testing config re-raises what production would answer with a 500
        failures.append(f"{what} -> crashed: {type(e).__name__}: {str(e)[:120]}")
        return
    if r.status_code >= 500:
        failures.append(f"{what} -> {r.status_code}")
    elif r.status_code >= 400 and r.mimetype == "application/json":
        body = r.get_json(silent=True) or {}
        if body.get("success") is not False or not body.get("code"):
            failures.append(f"{what} -> {r.status_code} without a stable code: {str(body)[:120]}")


@pytest.fixture
def signed_in(client, outbox):
    return student(client, outbox, "a10@example.test")


def _still_signed_in(client, outbox, who):
    """A route can end the session (logout); a fresh student keeps the rest reaching the code behind the token."""
    if client.get("/api/v1/me", headers=who.headers).status_code == 401:
        who.headers = student(client, outbox, f"a10.{uuid.uuid4().hex[:8]}@example.test").headers


def test_hostile_bodies_never_crash_a_route(app, client, outbox, signed_in):
    tried, failures = 0, []
    for method, rule in _routes(app):
        if method == "GET":
            continue
        path = _path(rule)
        for label, raw, ctype in BODIES:
            _try(client, failures, f"{method} {rule.rule} with {label}", path, method=method, data=raw, content_type=ctype,
                 headers=signed_in.headers)
            tried += 1
        _still_signed_in(client, outbox, signed_in)
    assert not failures, "\n".join(failures)
    assert tried > 500  # the map was read: about 60 routes take a body


def test_hostile_query_strings_never_crash_a_route(app, client, outbox, signed_in):
    tried, failures = 0, []
    for method, rule in _routes(app):
        path = _path(rule)
        for query in QUERIES:
            _try(client, failures, f"{method} {rule.rule}?{query[:40]}", f"{path}?{query}", method=method, headers=signed_in.headers)
            tried += 1
        _still_signed_in(client, outbox, signed_in)
    assert not failures, "\n".join(failures)
    assert tried > 700


def test_hostile_ids_in_the_path_never_crash_a_route(app, client, outbox, signed_in):
    failures, tried = [], 0
    for method, rule in _routes(app):
        if "<" not in re.sub(r"<uuid:\w+>", "", rule.rule):
            continue  # no text id here (UUIDs only, or none): the router refuses anything else
        for odd in ODD_IDS:
            _try(client, failures, f"{method} {rule.rule} with {odd[:20]!r}", _path(rule, odd), method=method, headers=signed_in.headers)
            tried += 1
        _still_signed_in(client, outbox, signed_in)
    assert not failures, "\n".join(failures)
    assert tried > 90  # the map was read: 14 routes take a text id today


def test_hostile_headers_never_crash_a_route(app, client, outbox, signed_in):
    odd = [
        {"Authorization": "Bearer " + "A" * 10000},
        {"Authorization": "Basic YTpi"},
        {"Authorization": "Bearer \udcff".encode("utf-8", "surrogateescape").decode("latin-1")},
        {"X-Forwarded-For": "1.1.1.1, " * 200 + "not-an-ip"},
        {"Content-Length": "0", "Content-Type": "application/json; charset=utf-7"},
        {"Accept-Language": "zz-" + "q" * 2000},
    ]
    failures = []
    for method, rule in _routes(app):
        for headers in odd:
            _try(client, failures, f"{method} {rule.rule} with {list(headers)[0]}", _path(rule), method=method, headers=headers)
    assert not failures, "\n".join(failures)


@pytest.mark.parametrize("text", ["\\ud800", "a\\udfffb", "\\u0000"])
def test_unstorable_text_in_a_well_formed_body_is_refused(client, signed_in, text):
    """Found by this sweep: a lone surrogate in an otherwise good title passed the schema and crashed the insert."""
    raw = ('{"title": "%s", "kind": "other", "weekday": 1, "starts": "10:00", "ends": "11:00"}' % text).encode()
    r = client.post("/api/v1/me/activities", data=raw, content_type="application/json", headers=signed_in.headers)
    assert r.status_code == 400 and r.get_json()["code"] == "INVALID_CHARACTERS"
    assert client.get("/api/v1/me/activities", headers=signed_in.headers).get_json()["data"]["activities"] == []


@pytest.mark.parametrize("path", ["/api/v1/me/funding/x%00y", "/api/v1/me/activities/x%00y", "/api/v1/money/spending/2026-10-01%00"])
def test_a_nul_in_the_path_is_refused(client, signed_in, path):
    """Found by this sweep: a NUL in a text id reached the database and crashed the query."""
    r = client.delete(path, headers=signed_in.headers)
    assert r.status_code == 400 and r.get_json()["code"] == "INVALID_CHARACTERS"
