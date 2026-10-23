"""API and integration tests for Weekly Money Check-in and Fixed Costs (Task G4).

Tests:
- Authentication & IDOR isolation (404 on other student's resources)
- Strict validation (unknown fields refused, integer cents, day_of_month 1-31, checkin_day)
- Fixed costs CRUD (add, list, update, delete)
- Integration with runway, safe-to-spend, and payday plan
- Weekly check-in submission (spending distributed over 7 days, or skipped)
- Non-shaming weekly streaks
- Next steps nudge on check-in day
- POPIA export and erasure
"""
from __future__ import annotations

import uuid
from datetime import date

import pytest
from student_helpers import MONEY, PROFILE, student

from src.domains.identity.accounts.models.user import User
from src.domains.student.money.services import money_service

TODAY = date(2026, 10, 18)  # Sunday
SETTINGS = {
    "balance_cents": 100_000,
    "balance_on": "2026-10-18",
    "essentials_per_day_cents": 4_000,
    "life_fund_reserve_cents": 10_000,
    "checkin_day": "sunday",
}


@pytest.fixture(autouse=True)
def on_sunday(monkeypatch):
    monkeypatch.setattr(money_service, "_today", lambda: TODAY)


@pytest.fixture
def me(client, outbox):
    return student(client, outbox, "checkin_me@example.com")


@pytest.fixture
def other(client, outbox):
    return student(client, outbox, "checkin_other@example.com")


def ok(r, status=200):
    assert r.status_code == status, r.get_json()
    return r.get_json()["data"]


# ------------------------------------------------------------- authentication


@pytest.mark.parametrize(
    "method, path",
    [
        ("get", "/fixed-costs"),
        ("post", "/fixed-costs"),
        ("put", f"/fixed-costs/{uuid.uuid4()}"),
        ("delete", f"/fixed-costs/{uuid.uuid4()}"),
        ("get", "/checkin"),
        ("post", "/checkin"),
    ],
)
def test_checkin_routes_require_token(client, method, path):
    assert getattr(client, method)(f"{MONEY}{path}", json={}).status_code == 401


# ---------------------------------------------------------------- fixed costs


def test_fixed_costs_crud_and_ordering(client, me):
    # Setup initial money settings
    ok(client.put(f"{MONEY}/settings", json=SETTINGS, headers=me.headers))

    # Add rent on the 1st
    r1 = ok(
        client.post(
            f"{MONEY}/fixed-costs",
            json={"label": "Rent", "amount_cents": 250_000, "day_of_month": 1},
            headers=me.headers,
        ),
        201,
    )
    assert r1["fixed_cost"]["label"] == "Rent"
    assert r1["fixed_cost"]["amount_cents"] == 250_000
    assert r1["fixed_cost"]["day_of_month"] == 1
    rent_id = r1["fixed_cost"]["id"]

    # Add data bundle on the 25th
    r2 = ok(
        client.post(
            f"{MONEY}/fixed-costs",
            json={"label": "Data bundle", "amount_cents": 15_000, "day_of_month": 25},
            headers=me.headers,
        ),
        201,
    )
    assert r2["fixed_cost"]["day_of_month"] == 25

    # Add transport on the 15th
    r3 = ok(
        client.post(
            f"{MONEY}/fixed-costs",
            json={"label": "Train pass", "amount_cents": 45_000, "day_of_month": 15},
            headers=me.headers,
        ),
        201,
    )
    assert r3["fixed_cost"]["day_of_month"] == 15

    # List fixed costs - must be ordered by day_of_month (1, 15, 25)
    listing = ok(client.get(f"{MONEY}/fixed-costs", headers=me.headers))
    days = [c["day_of_month"] for c in listing["fixed_costs"]]
    assert days == [1, 15, 25]

    # Update rent amount
    up = ok(
        client.put(
            f"{MONEY}/fixed-costs/{rent_id}",
            json={"label": "Rent (Shared)", "amount_cents": 260_000, "day_of_month": 1},
            headers=me.headers,
        )
    )
    assert up["fixed_cost"]["label"] == "Rent (Shared)"
    assert up["fixed_cost"]["amount_cents"] == 260_000

    # Delete transport
    ok(client.delete(f"{MONEY}/fixed-costs/{r3['fixed_cost']['id']}", headers=me.headers))
    remaining = ok(client.get(f"{MONEY}/fixed-costs", headers=me.headers))
    assert len(remaining["fixed_costs"]) == 2
    assert [c["day_of_month"] for c in remaining["fixed_costs"]] == [1, 25]


def test_fixed_costs_idor_isolation(client, me, other):
    ok(client.put(f"{MONEY}/settings", json=SETTINGS, headers=me.headers))
    ok(client.put(f"{MONEY}/settings", json=SETTINGS, headers=other.headers))

    r = ok(
        client.post(
            f"{MONEY}/fixed-costs",
            json={"label": "Gym", "amount_cents": 20_000, "day_of_month": 5},
            headers=me.headers,
        ),
        201,
    )
    cost_id = r["fixed_cost"]["id"]

    # Other student trying to update or delete gets 404 (IDOR rule)
    res_put = client.put(
        f"{MONEY}/fixed-costs/{cost_id}",
        json={"label": "Hacked", "amount_cents": 100, "day_of_month": 5},
        headers=other.headers,
    )
    assert res_put.status_code == 404

    res_del = client.delete(f"{MONEY}/fixed-costs/{cost_id}", headers=other.headers)
    assert res_del.status_code == 404


def test_fixed_costs_validation_hostile(client, me):
    ok(client.put(f"{MONEY}/settings", json=SETTINGS, headers=me.headers))

    # Unknown field
    r = client.post(
        f"{MONEY}/fixed-costs",
        json={"label": "Rent", "amount_cents": 20_000, "day_of_month": 1, "extra": "evil"},
        headers=me.headers,
    )
    assert r.status_code == 422

    # Zero or negative amount
    assert client.post(
        f"{MONEY}/fixed-costs",
        json={"label": "Rent", "amount_cents": 0, "day_of_month": 1},
        headers=me.headers,
    ).status_code == 422

    assert client.post(
        f"{MONEY}/fixed-costs",
        json={"label": "Rent", "amount_cents": -500, "day_of_month": 1},
        headers=me.headers,
    ).status_code == 422

    # Invalid day of month
    assert client.post(
        f"{MONEY}/fixed-costs",
        json={"label": "Rent", "amount_cents": 20_000, "day_of_month": 0},
        headers=me.headers,
    ).status_code == 422

    assert client.post(
        f"{MONEY}/fixed-costs",
        json={"label": "Rent", "amount_cents": 20_000, "day_of_month": 32},
        headers=me.headers,
    ).status_code == 422

    # Float amount
    assert client.post(
        f"{MONEY}/fixed-costs",
        json={"label": "Rent", "amount_cents": 1250.50, "day_of_month": 1},
        headers=me.headers,
    ).status_code == 422


def test_fixed_costs_reflected_in_plan_and_safe_to_spend(client, me):
    ok(client.put(f"{MONEY}/settings", json=SETTINGS, headers=me.headers))
    ok(
        client.post(
            f"{MONEY}/income-sources",
            json={"label": "Allowance", "amount_cents": 150_000, "expected_on": "2026-10-30", "reliability": "on_time"},
            headers=me.headers,
        ),
        201,
    )
    # Add a fixed cost occurring on the 25th (before next payment on the 30th)
    ok(
        client.post(
            f"{MONEY}/fixed-costs",
            json={"label": "Data", "amount_cents": 10_000, "day_of_month": 25},
            headers=me.headers,
        ),
        201,
    )

    # Check /money/summary: safe_to_spend should account for fixed_costs_cents
    summ = ok(client.get(f"{MONEY}/summary", headers=me.headers))
    safe = summ["safe_to_spend"]
    assert "fixed_costs_cents" in safe
    assert safe["fixed_costs_cents"] == 10_000

    # Check /money/plan: fixed_costs should be listed
    p = ok(client.get(f"{MONEY}/plan", headers=me.headers))
    assert len(p["fixed_costs"]) == 1
    assert p["fixed_costs"][0]["label"] == "Data"


# ------------------------------------------------------------ check-in streak


def test_settings_checkin_day(client, me):
    ok(client.put(f"{MONEY}/settings", json=SETTINGS, headers=me.headers))

    # Check default
    s = ok(client.get(f"{MONEY}/settings", headers=me.headers))["settings"]
    assert s["checkin_day"] == "sunday"

    # Update to friday
    updated = ok(
        client.put(
            f"{MONEY}/settings",
            json={**SETTINGS, "checkin_day": "friday"},
            headers=me.headers,
        )
    )["settings"]
    assert updated["checkin_day"] == "friday"

    # Reject invalid day
    res_bad = client.put(
        f"{MONEY}/settings",
        json={**SETTINGS, "checkin_day": "funday"},
        headers=me.headers,
    )
    assert res_bad.status_code == 422


def test_weekly_checkin_and_streak(client, me):
    ok(client.put(f"{MONEY}/settings", json=SETTINGS, headers=me.headers))

    # Initial checkin status on Sunday (checkin day)
    st = ok(client.get(f"{MONEY}/checkin", headers=me.headers))
    assert st["checkin_day"] == "sunday"
    assert st["is_checkin_day"] is True
    assert st["checked_in_this_week"] is False
    assert st["streak"]["weeks"] == 0
    assert "Welcome back" in st["streak"]["line"]

    # Submit spending check-in for this week (R700 = 70_000 cents)
    post_res = ok(
        client.post(
            f"{MONEY}/checkin",
            json={"amount_cents": 70_000, "skipped": False},
            headers=me.headers,
        )
    )
    assert post_res["checked_in_this_week"] is True
    assert post_res["streak"]["weeks"] == 1
    assert post_res["streak"]["line"] == "Welcome back: 1 week in a row."
    assert post_res["this_week"]["amount_cents"] == 70_000
    assert post_res["this_week"]["skipped"] is False

    # Verify that spending entries were spread over the 7 days (70_000 // 7 = 10_000 cents per day)
    spending = ok(client.get(f"{MONEY}/spending?days=7", headers=me.headers))["spending"]
    assert len(spending) == 7
    for entry in spending:
        assert entry["amount_cents"] == 10_000


def test_weekly_checkin_skip(client, me):
    ok(client.put(f"{MONEY}/settings", json=SETTINGS, headers=me.headers))

    # Skip this week
    res = ok(
        client.post(
            f"{MONEY}/checkin",
            json={"skipped": True},
            headers=me.headers,
        )
    )
    assert res["checked_in_this_week"] is True
    assert res["this_week"]["skipped"] is True
    assert res["this_week"]["amount_cents"] is None
    assert res["streak"]["weeks"] == 1

    # Verify no spending entries created
    spending = ok(client.get(f"{MONEY}/spending?days=7", headers=me.headers))["spending"]
    assert len(spending) == 0


def test_weekly_checkin_validation_hostile(client, me):
    ok(client.put(f"{MONEY}/settings", json=SETTINGS, headers=me.headers))

    # Both skipped and amount provided -> 422
    assert client.post(
        f"{MONEY}/checkin",
        json={"skipped": True, "amount_cents": 10_000},
        headers=me.headers,
    ).status_code == 422

    # Not skipped and amount missing -> 422
    assert client.post(
        f"{MONEY}/checkin",
        json={"skipped": False},
        headers=me.headers,
    ).status_code == 422

    # Negative amount -> 422
    assert client.post(
        f"{MONEY}/checkin",
        json={"skipped": False, "amount_cents": -500},
        headers=me.headers,
    ).status_code == 422

    # Unknown field -> 422
    assert client.post(
        f"{MONEY}/checkin",
        json={"skipped": True, "extra": "bad"},
        headers=me.headers,
    ).status_code == 422


def test_popia_export_and_erase(client, me):
    ok(client.put(f"{MONEY}/settings", json=SETTINGS, headers=me.headers))
    ok(
        client.post(
            f"{MONEY}/fixed-costs",
            json={"label": "Rent", "amount_cents": 200_000, "day_of_month": 1},
            headers=me.headers,
        ),
        201,
    )
    ok(
        client.post(
            f"{MONEY}/checkin",
            json={"amount_cents": 50_000, "skipped": False},
            headers=me.headers,
        )
    )

    # Export
    with client.application.app_context():
        from src.extensions import db
        user = db.session.get(User, uuid.UUID(me.id))
        exported = money_service.export_for(user)
        assert "fixed_costs" in exported
        assert len(exported["fixed_costs"]) == 1
        assert exported["fixed_costs"][0]["label"] == "Rent"
        assert "weekly_checkins" in exported
        assert len(exported["weekly_checkins"]) == 1

        # Erase
        money_service.erase_all_for(user)
    assert len(ok(client.get(f"{MONEY}/fixed-costs", headers=me.headers))["fixed_costs"]) == 0
    st = ok(client.get(f"{MONEY}/checkin", headers=me.headers))
    assert st["checked_in_this_week"] is False
    assert st["streak"]["weeks"] == 0


def test_forget_old_spending_job_deletes_old_checkins_and_spending(client, me):
    ok(client.put(f"{MONEY}/settings", json=SETTINGS, headers=me.headers))
    from datetime import timedelta
    from src.domains.student.money.jobs import forget_old_spending
    from src.domains.student.money.models import WeeklyCheckin
    from src.extensions import db

    old_date = TODAY - timedelta(days=400)
    with client.application.app_context():
        old_checkin = WeeklyCheckin(user_id=uuid.UUID(me.id), week_end=old_date, amount_cents=10_000, skipped=False)
        db.session.add(old_checkin)
        db.session.commit()

    ok(client.post(f"{MONEY}/checkin", json={"skipped": True}, headers=me.headers))

    with client.application.app_context():
        res = forget_old_spending.run()
        assert res.success is True
        assert res.count >= 1
        assert WeeklyCheckin.query.filter_by(week_end=old_date).first() is None
        assert WeeklyCheckin.query.filter_by(user_id=uuid.UUID(me.id), week_end=TODAY).first() is not None
