"""
Making the demo accounts and re-basing their data. Every record goes in
through the owning feature's own service, as a student would enter it;
nothing here touches another feature's tables. The personas' dates are kept
at their distance from the file's "today", so on any day the demo looks the
way the personas were written: short money, a heavy week ahead, a heavy week
now, and a classmate's message waiting for the rep.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime, time, timedelta
from functools import lru_cache
from zoneinfo import ZoneInfo

import yaml

from src.domains.classes.classes.services import class_service
from src.domains.classes.events.services import events_service
from src.domains.identity.accounts.services import account_service
from src.domains.platform.notifications.services import notification_service
from src.domains.student.academics.services import academics_service
from src.domains.student.money.services import money_service
from src.domains.student.profile.services import profile_service
from src.domains.student.saved_funding.services import saved_funding_service
from src.domains.student.timetable.services import timetable_service
from src.extensions import db

from ..constants import PERSONAS_PATH, TIMEZONE
from ..repositories import demo_repository as repo


class DemoPasswordError(ValueError):
    """DEMO_PASSWORD doesn't meet the password rule everyone else meets."""


def _today() -> date:
    """Today in South Africa: every student's day."""
    return datetime.now(ZoneInfo(TIMEZONE)).date()


@lru_cache(maxsize=1)
def personas() -> dict:
    return yaml.safe_load(PERSONAS_PATH.read_text(encoding="utf-8"))


def seed(password: str, today: date | None = None) -> list[str]:
    """Make (or refresh) the demo accounts with the shared password, then build their data on today's
    date. Safe to run again. Returns the accounts' emails; never the password."""
    problems = account_service.check_demo_password(password)
    if problems:
        raise DemoPasswordError(
            "DEMO_PASSWORD needs 8 to 64 characters with a capital letter, a small letter, a number and a special character."
        )
    people = personas()["personas"]
    for p in people:
        user = account_service.ensure_demo_account(p["email"], password)
        repo.ensure(user.id, p["id"])
    db.session.commit()
    rebase(today or _today())
    return [p["email"] for p in people]


def due(today: date) -> bool:
    """Demo accounts exist and at least one hasn't been re-based today."""
    rows = repo.all_accounts()
    return bool(rows) and any(r.rebased_on is None or r.rebased_on < today for r in rows)


def rebase(today: date) -> int:
    """Forget what the demo accounts hold (anything a visitor changed included) and build it again from the
    personas, each date as far from today as it is from the personas' own "today". Returns how many
    accounts were built. Not one transaction: if it stops halfway, `rebased_on` isn't moved, so the next
    run builds everything again."""
    data = personas()
    shift = today - data["today"]
    rows = {r.persona: r for r in repo.all_accounts()}
    users = {pid: account_service.get(r.user_id) for pid, r in rows.items()}
    users = {pid: u for pid, u in users.items() if u is not None}
    if not users:
        return 0

    left = []
    for user in users.values():
        money_service.erase_all_for(user)
        academics_service.erase_all_for(user)
        saved_funding_service.erase_all_for(user)
        timetable_service.erase_all_for(user)
        events_service.erase_all_for(user)
        left += class_service.leave_all(user)
        profile_service.erase_for(user)
        notification_service.erase_all_for(user)  # the rebuilt classes tell their members afresh
    class_service.delete_if_empty(left)

    people = [p for p in data["personas"] if p["id"] in users]
    for p in people:
        _student(users[p["id"]], p, today, shift)
    classes: dict[tuple[str, str], str] = {}
    for p in people:
        _classes(users, p, today, shift, classes)
    for p in people:
        _waiting(users, p, shift, classes)

    for pid in users:
        rows[pid].rebased_on = today
    db.session.commit()
    return len(users)


def _student(user, p: dict, today: date, shift: timedelta) -> None:
    """Profile, money and marks, entered as the student would."""
    profile_service.update(user, p["university"], p["campus"])
    if "balance_cents" in p:
        money_service.put_settings(user, {
            "balance_cents": p["balance_cents"],
            "balance_on": today,
            "essentials_per_day_cents": p["essentials_per_day_cents"],
            "life_fund_reserve_cents": p["life_fund_reserve_cents"],
        })
        for pay in p.get("payments", []):
            money_service.add_source(user, {
                "label": pay["label"],
                "amount_cents": pay["amount_cents"],
                "day_of_month": None,
                "expected_on": pay["expected_on"] + shift,
                "reliability": pay.get("reliability", "not_sure"),
            })
        days = len(p.get("spending", []))
        for i, cents in enumerate(p.get("spending", [])):  # oldest first, ending yesterday
            money_service.put_spending(user, (today - timedelta(days=days - i)).isoformat(), cents)
    for c in p.get("timetable", []):
        timetable_service.add(user, {
            "module": c["module"], "kind": c["kind"], "weekday": c["weekday"], "title": c.get("title"),
            "starts": _time(c["starts"]), "ends": _time(c["ends"]), "venue": c.get("venue"),
        })
    for m in p.get("modules", []):
        module = academics_service.add_module(user, {"code": m["code"], "name": m.get("name"), "target": float(m["target"])})
        for a in m["assessments"]:
            mark = a.get("mark")
            academics_service.add_assessment(user, uuid.UUID(module["module"]["id"]), {
                "name": a["name"], "weight": float(a["weight"]), "mark": float(mark) if mark is not None else None,
            })


def _time(value: str):
    hours, minutes = value.split(":")
    return time(int(hours), int(minutes))


def _classes(users: dict, p: dict, today: date, shift: timedelta, classes: dict) -> None:
    """The persona's classes, made by their rep, with each event announced and confirmed by the rep."""
    if not p.get("events"):
        return
    rep, member = users[p["classes_by"]], users[p["id"]]
    names = {m["code"]: m.get("name") for m in p.get("modules", [])}
    for event in p["events"]:
        module = event["module"]
        if (p["id"], module) not in classes:
            made = class_service.create(rep, {
                "university": p["university"], "campus": p["campus"], "module_code": module,
                "module_name": names.get(module), "year": today.year,
            })["class"]
            if member is not rep:
                class_service.join(member, made["invite_code"])
            classes[(p["id"], module)] = made["id"]
        class_id = uuid.UUID(classes[(p["id"], module)])
        starts = datetime.strptime(event["starts"], "%Y-%m-%d %H:%M")
        candidate = events_service.announce(rep, class_id, {"text": f"{module} {event['title']}", "sent_on": today})
        events_service.confirm(rep, uuid.UUID(candidate["candidate"]["id"]), {
            "change": None, "event_id": None, "kind": event["kind"], "title": event["title"],
            "on": starts.date() + shift, "at": starts.time(), "venue": None,
            "weighting": float(event["weighting"]) if event.get("weighting") else None,
        })


def _waiting(users: dict, p: dict, shift: timedelta, classes: dict) -> None:
    """Announcements a classmate sent that wait for the rep to check them."""
    for w in p.get("waiting", []):
        class_id = uuid.UUID(classes[(w["from"], w["module"])])
        events_service.announce(users[w["from"]], class_id, {"text": w["text"], "sent_on": w["sent"] + shift})
