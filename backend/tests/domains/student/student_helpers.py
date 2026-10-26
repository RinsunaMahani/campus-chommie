"""
Shared by the student tests: signed-in students with their ids, and the
fictional demo personas (data/demo/personas.yaml) set up through the API,
the way a student would enter them. Also the demo accounts: a fixed day for
every service that asks for today, a password made fresh for each run (no
demo password ever sits in the repo), the seed, and signing in as a persona.
"""
from __future__ import annotations

import re
import secrets
from datetime import date, timedelta
from pathlib import Path

import yaml

from src.domains.classes.classes.services import class_service
from src.domains.classes.events.services import events_service, week_service
from src.domains.platform.demo.services import demo_service
from src.domains.student.alerts.services import alert_service, review_service
from src.domains.student.money.services import money_service
from src.domains.student.saved_funding.services import saved_funding_service

PASSWORD = "Campus2026!"
CONSENT = {"privacy_version": "0.1-draft", "terms_version": "0.1-draft", "confirmed_18_or_older": True}
PROFILE = "/api/v1/me/profile"
MONEY = "/api/v1/money"
PERSONAS = Path(__file__).resolve().parents[3] / "data" / "demo" / "personas.yaml"


class Student:
    def __init__(self, headers: dict, user_id: str):
        self.headers = headers
        self.id = user_id


def student(client, outbox, email: str) -> Student:
    client.post("/api/v1/auth/register", json={"email": email, "password": PASSWORD, "consent": CONSENT})
    code = re.search(r">(\d{6})<", outbox[-1]["html_body"]).group(1)
    token = client.post("/api/v1/auth/verify-email", json={"email": email, "code": code}).get_json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    me = client.get("/api/v1/me", headers=headers).get_json()["data"]
    return Student(headers, (me.get("user") or me)["id"])


def personas() -> tuple[date, dict]:
    data = yaml.safe_load(PERSONAS.read_text(encoding="utf-8"))
    return data["today"], {p["id"]: p for p in data["personas"]}


def set_up_persona(client, who: Student, persona_id: str) -> date:
    """Balance, essentials and reserve, each expected payment, and the last days' spending."""
    today, people = personas()
    p = people[persona_id]
    settings = {
        "balance_cents": p["balance_cents"],
        "balance_on": today.isoformat(),
        "essentials_per_day_cents": p["essentials_per_day_cents"],
        "life_fund_reserve_cents": p["life_fund_reserve_cents"],
    }
    assert client.put(f"{MONEY}/settings", json=settings, headers=who.headers).status_code == 200
    for pay in p["payments"]:
        body = {"label": pay["label"], "amount_cents": pay["amount_cents"], "expected_on": pay["expected_on"].isoformat()}
        assert client.post(f"{MONEY}/income-sources", json=body, headers=who.headers).status_code == 201
    days = len(p["spending"])
    for i, cents in enumerate(p["spending"]):  # oldest first, ending yesterday
        spent_on = (today - timedelta(days=days - i)).isoformat()
        assert client.put(f"{MONEY}/spending/{spent_on}", json={"amount_cents": cents}, headers=who.headers).status_code == 200
    return today


# ------------------------------------------------------------ demo accounts

DEMO_TODAY = date(2026, 10, 12)  # the personas' own "today", a Monday
DEMO_EMAILS = {"naledi": "naledi.demo@example.com", "sipho": "sipho.demo@example.com", "thabo": "thabo.demo@example.com"}
SERVICES_WITH_TODAY = (money_service, class_service, events_service, week_service, alert_service, demo_service, saved_funding_service,
                       review_service)


def on_day(monkeypatch, day: date) -> None:
    """Every service that asks for today gets `day`."""
    for module in SERVICES_WITH_TODAY:
        monkeypatch.setattr(module, "_today", lambda day=day: day)


def fresh_password() -> str:
    """Meets the password rule: letters, digits, a capital, a small letter and a special character."""
    return secrets.token_urlsafe(12) + "aZ7!"


def seed_demo(app, password: str, day: date = DEMO_TODAY) -> list[str]:
    with app.app_context():
        return demo_service.seed(password, today=day)


def sign_in_demo(client, persona: str, password: str) -> dict:
    r = client.post("/api/v1/auth/login", json={"email": DEMO_EMAILS[persona], "password": password})
    assert r.status_code == 200, r.get_json()
    return {"Authorization": f"Bearer {r.get_json()['data']['access_token']}"}
