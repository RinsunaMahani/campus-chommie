"""Tests for GET /api/v1/money/health (Task G5: Money health five checks)."""
from datetime import date

import pytest
from student_helpers import student


API = "/api/v1"
TODAY = date(2026, 10, 18)


@pytest.fixture
def me(client, outbox):
    return student(client, outbox, "lerato@example.com")


@pytest.fixture
def other(client, outbox):
    return student(client, outbox, "sipho@example.com")


def test_health_requires_auth(client):
    r = client.get(f"{API}/money/health")
    assert r.status_code == 401


def test_health_refuses_query_parameters(client, me):
    r = client.get(f"{API}/money/health?extra=1", headers=me.headers)
    assert r.status_code == 422


def test_health_empty_student_returns_five_checks(client, me):
    r = client.get(f"{API}/money/health", headers=me.headers)
    assert r.status_code == 200
    data = r.get_json()["data"]
    assert "checks" in data
    assert len(data["checks"]) == 5
    assert data["total_count"] == 5
    assert data["done_count"] == 0
    assert "0 of 5 checks done" in data["line"]

    check_ids = [c["id"] for c in data["checks"]]
    assert check_ids == ["runway", "buffer", "spending", "goals", "checkin"]

    for c in data["checks"]:
        assert c["status"] in ("can't tell", "not yet")
        assert c["action"] is not None
        assert c["target"] is not None
        # Tone check: never shaming words
        assert "unhealthy" not in c["line"].lower()
        assert "risk" not in c["line"].lower()
        assert "fail" not in c["line"].lower()


def test_health_reflects_student_actions(client, me):
    # 1. Set settings
    s = client.put(
        f"{API}/money/settings",
        json={
            "balance_cents": 100_000,
            "balance_on": TODAY.isoformat(),
            "essentials_per_day_cents": 4_000,
            "life_fund_reserve_cents": 10_000,
            "checkin_day": "sunday",
        },
        headers=me.headers,
    )
    assert s.status_code == 200

    # 2. Add an expected payment
    p = client.post(
        f"{API}/money/income-sources",
        json={
            "label": "NSFAS",
            "amount_cents": 150_000,
            "expected_on": date(2026, 11, 1).isoformat(),
            "reliability": "on_time",
        },
        headers=me.headers,
    )
    assert p.status_code == 201

    # 3. Add a funded buffer pot
    g = client.post(
        f"{API}/money/goals",
        json={
            "label": "Emergency Fund",
            "kind": "buffer",
            "amount_cents": 50_000,
            "saved_cents": 25_000,
        },
        headers=me.headers,
    )
    assert g.status_code == 201

    # 4. Check in this week
    c = client.post(
        f"{API}/money/checkin",
        json={"amount_cents": 10_000},
        headers=me.headers,
    )
    assert c.status_code == 200

    # 5. Fetch health
    r = client.get(f"{API}/money/health", headers=me.headers)
    assert r.status_code == 200
    data = r.get_json()["data"]

    checks = {chk["id"]: chk for chk in data["checks"]}
    assert checks["runway"]["status"] == "done"
    assert checks["buffer"]["status"] == "done"
    assert checks["spending"]["status"] == "done"
    assert checks["goals"]["status"] == "done"  # No dated goals, so covered
    assert checks["checkin"]["status"] == "done"
    assert data["done_count"] == 5
    assert data["line"] == "5 of 5 checks done"


def test_health_is_owner_only(client, me, other):
    # Setup me with buffer pot
    client.post(
        f"{API}/money/goals",
        json={"label": "My Buffer", "kind": "buffer", "amount_cents": 50_000, "saved_cents": 20_000},
        headers=me.headers,
    )

    # other should see no buffer
    r = client.get(f"{API}/money/health", headers=other.headers)
    assert r.status_code == 200
    data = r.get_json()["data"]
    buffer_check = next(c for c in data["checks"] if c["id"] == "buffer")
    assert buffer_check["status"] == "not yet"
