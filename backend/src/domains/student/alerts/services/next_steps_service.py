"""
"Do this next" for Home: everything the app knows about the signed-in student, gathered from each feature's own
service (money, the week, exams, saved bursaries, goals, the timetable), ranked by the engine
(campus_engine.next_steps) into at most three steps. Nothing is stored; everything read is the student's own.
"""
from __future__ import annotations

from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from campus_engine.config import load_config
from campus_engine.next_steps import Closing, Due, Facts, GoalDue, next_steps
from src.domains.classes.events.services import week_service
from src.domains.student.money.services import money_service as money
from src.domains.student.saved_funding.services import saved_funding_service as saved_funding
from src.domains.student.timetable.services import exam_service, timetable_service

from ..constants import TIMEZONE


def _today() -> date:
    """Today in South Africa: every student's day."""
    return datetime.now(ZoneInfo(TIMEZONE)).date()


def _iso(value: str | None) -> date | None:
    try:
        return date.fromisoformat(value) if value else None
    except ValueError:
        return None


def facts(user, today: date) -> Facts:
    cfg = load_config()["next_steps"]
    weeks = week_service.loads(user, today, max(2, cfg["heavy_weeks_ahead"]))
    due = [
        Due(e.module or "", e.title, e.starts.date(),
            None if e.starts.time() in (time(0, 0), time(23, 59)) else e.starts.strftime("%H:%M"),
            e.weighting, e.kind == "exam")
        for w in weeks for e in w.events if not e.cancelled and e.starts.date() >= today
    ]
    for x in exam_service.mine(user)["exams"]:
        on = _iso(x["on"])
        if on and on >= today:
            due.append(Due(x["module"], x.get("paper") or "exam", on, x["starts"], None, True))
    closing = []
    for c in saved_funding.mine(user)["funders"]:
        closes = _iso(c.get("closes"))
        if closes and c.get("status") in ("open", "closing_soon", "late_open"):
            closing.append(Closing(c.get("short_name") or c["name"], closes))
    plan = money.plan(user)
    goals = [GoalDue(g["label"], date.fromisoformat(g["due_on"]), max(0, g["amount_cents"] - g["saved_cents"]),
                     g["per_week_cents"]) for g in plan["goals"]]
    return Facts(today, money.runway_for(user, today), weeks, due, closing, goals,
                 len(timetable_service.mine(user)["entries"]))


def mine(user) -> dict:
    """At most three steps, most urgent first, each with why, one action and where it leads."""
    today = _today()
    steps = next_steps(facts(user, today), load_config()["next_steps"])
    return {
        "today": today.isoformat(),
        "steps": [{"kind": s.kind, "line": s.line, "why": s.why, "action": s.action, "target": s.target,
                   "tone": s.tone} for s in steps],
    }
