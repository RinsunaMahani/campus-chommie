"""
Your week in review: at the end of the student's week (the week their money check-in uses, ending on their check-in
day), what's behind them, what's coming, how their marks moved and how their spending compares with their usual.
Gathered from each feature's own service and put into words by the engine (campus_engine.weekly_review). Nothing is
stored; everything read is the student's own.

  review(user, week)   week "this", "last" or "auto" (this week on the check-in day, last week for the two days
                       after it, this week otherwise)
  daily_ready(user)    registered as a daily check: on the check-in day, one "Your week in review" alert, when the
                       week has something to show
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from campus_engine.config import load_config
from campus_engine.weekly_review import Facts, Item, MarkEntered, ModuleMarks, weekly_review
from src.domains.classes.events.services import week_service
from src.domains.student.academics.services import academics_service as academics
from src.domains.student.money.services import money_service as money
from src.domains.student.saved_funding.services import saved_funding_service as saved_funding
from src.domains.student.timetable.services import exam_service
from src.shared.notifications.notification_types import NotificationEvent
from src.shared.notifications.notifications import publish_notification

from ..constants import TIMEZONE

#: Days after the check-in day on which Home still offers last week's review.
READY_DAYS_AFTER = 2
SUPPORT_LINE = "If a mark knocked you this week, your campus's tutoring and counselling are there to help."
_OPEN = ("open", "closing_soon", "late_open")


def _today() -> date:
    return datetime.now(ZoneInfo(TIMEZONE)).date()


def _iso(value: str | None) -> date | None:
    try:
        return date.fromisoformat(value) if value else None
    except ValueError:
        return None


def _bounds(first: date, last: date) -> tuple[datetime, datetime]:
    """The student's days, first to last, as moments (SAST midnight to the end of the last day)."""
    tz = ZoneInfo(TIMEZONE)
    return datetime.combine(first, time.min, tz), datetime.combine(last, time.max, tz)


def _week(user, today: date, week: str) -> tuple[date, bool, dict]:
    """(the week's last day, whether Home offers it today, the check-in status)."""
    status = money.get_checkin_status(user, today)
    this_end = date.fromisoformat(status["week_end"])
    last_end = this_end - timedelta(days=7)
    on_checkin_day = today == this_end
    just_after = 0 < (today - last_end).days <= READY_DAYS_AFTER
    if week == "auto":
        week = "last" if just_after and not on_checkin_day else "this"
    end = this_end if week == "this" else last_end
    ready = (week == "this" and on_checkin_day) or (week == "last" and just_after)
    return end, ready, status


def _dated(user, start: date, until: date, today: date, cfg: dict) -> tuple[list[Item], list[Item]]:
    """(behind, coming): class events, exams, saved funders closing and goals' dates. Behind: in the week, before
    today (today too once the week is ending). Coming: from today to `coming_days` ahead, not already behind."""
    ahead = today + timedelta(days=cfg["coming_days"])
    items: list[Item] = []
    for w in week_service.loads(user, start, 4):
        for e in w.events:
            if e.cancelled:
                continue
            at = None if e.starts.time() in (time(0, 0), time(23, 59)) else e.starts.strftime("%H:%M")
            items.append(Item(e.kind, f"{e.module or ''} {e.title}".strip(), e.starts.date(), at))
    for x in exam_service.mine(user)["exams"]:
        on = _iso(x["on"])
        if on:
            items.append(Item("exam", f"{x['module']} {x.get('paper') or 'exam'}".strip(), on, x.get("starts")))
    for c in saved_funding.mine(user)["funders"]:
        closes = _iso(c.get("closes"))
        if closes and (closes < today or c.get("status") in _OPEN):
            items.append(Item("funding", c.get("short_name") or c["name"], closes))
    for g in money.plan(user)["goals"]:
        due = _iso(g.get("due_on"))
        if due:
            items.append(Item("goal", g["label"], due))

    behind_until = min(until, today if today >= until else today - timedelta(days=1))
    behind = [i for i in items if start <= i.on <= behind_until]
    coming = [i for i in items if today <= i.on <= ahead and i not in behind]
    return behind, coming


def _facts(user, today: date, end: date, status: dict, cfg: dict) -> Facts:
    start = end - timedelta(days=6)
    behind, coming = _dated(user, start, end, today, cfg)
    entered, modules = academics.week_marks(user, *_bounds(start, min(end, today)))
    weeks = money.weekly_spending(user, end, 1 + cfg["compare_weeks"])
    checked = end.isoformat() in {c["week_end"] for c in status["recent_checkins"] if not c["skipped"]}
    return Facts(
        week_start=start,
        week_end=end,
        today=today,
        behind=behind,
        coming=coming,
        marks=[MarkEntered(module, name, mark) for module, name, mark in entered],
        modules=[ModuleMarks(code, target, before, after, out) for code, target, before, after, out in modules],
        checked_in=checked,
        # The streak is counted up to the current week: shown on this week's review only.
        streak_weeks=status["streak"]["weeks"] if checked and end.isoformat() == status["week_end"] else 0,
        spent_cents=weeks[0],
        earlier_weeks_cents=weeks[1:],
    )


def review(user, week: str = "auto", today: date | None = None) -> dict:
    today = today or _today()
    cfg = load_config()["weekly_review"]
    end, ready, status = _week(user, today, week)
    r = weekly_review(_facts(user, today, end, status, cfg), cfg)
    s = r.spending
    return {
        "today": today.isoformat(),
        "week": "this" if end >= today else "last",
        "week_start": r.week_start.isoformat(),
        "week_end": r.week_end.isoformat(),
        "finished": r.finished,
        "ready": ready,
        "headline": r.headline,
        "done": [{"text": d.text, "kind": d.kind} for d in r.done],
        "coming": [{"text": c.text, "kind": c.kind} for c in r.coming],
        "marks": [{"code": m.code, "before": m.before, "after": m.after, "direction": m.direction, "text": m.text}
                  for m in r.marks],
        "spending": {"spent_cents": s.spent_cents, "usual_cents": s.usual_cents, "days": s.days,
                     "weeks_compared": s.weeks_compared, "direction": s.direction, "text": s.text, "weeks": s.weeks},
        "support": SUPPORT_LINE if r.support else None,
    }


def _has_something(r: dict) -> bool:
    return bool(r["done"] or r["coming"] or r["marks"] or r["spending"]["spent_cents"] is not None)


def daily_ready(user) -> None:
    """Registered as a daily check (src/__init__.py): on the student's check-in day, one alert for the week, when
    there's something to show (a new account with nothing in it isn't nudged)."""
    today = _today()
    if not money.get_checkin_status(user, today)["is_checkin_day"]:
        return  # every other day costs one small read, not a whole review
    r = review(user, "this", today)
    if not _has_something(r):
        return
    publish_notification(
        NotificationEvent(
            recipient_user_id=user.id,
            template="review.ready",
            dedupe_key=f"review:{r['week_end']}",
            params={},
            link_type="review",
            link_id=r["week_end"],
        )
    )
