"""
My money: the student's records, and the summary the engine makes of them.
Services call the engine; routes never do. Every function takes the
signed-in student and touches only their rows: another student's row is the
same 404 as one that doesn't exist.

The balance stays current without retyping it: the one the student entered,
less the spending they've logged since, plus the payments they've marked
received since. Monthly income becomes expected payments for the runway's
horizon, made once per occurrence however often the list is read.
"""
from __future__ import annotations

import calendar
import re
import uuid
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from campus_engine.config import load_config
from campus_engine.forecast import forecast_runway, spending_pace
from campus_engine.lifefund import life_fund_signal
from campus_engine.runway import ExpectedPayment as Arrival
from campus_engine.runway import RunwayResult, project_runway, safe_to_spend
from campus_engine.text import long_day, rand
from src.core.exceptions import NotFoundError, ValidationError
from src.domains.classes.events.services import week_service
from src.extensions import db

from ..constants import MAX_DAYS_BACK, MAX_SOURCES, PACE_DAYS, PAST_DAYS, TIMEZONE
from ..models import ExpectedPayment, IncomeSource, MoneySettings, SpendingEntry
from ..repositories import money_repository as repo

ISO_DAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")
LATE_PRONE = ("sometimes_late", "often_late")
WEEK_NOT_YET = "Your week isn't part of this yet: tests and exams count once you've joined your classes."


def _today() -> date:
    """Today in South Africa: every student's day."""
    return datetime.now(ZoneInfo(TIMEZONE)).date()


def _field_error(field: str, message: str) -> ValidationError:
    return ValidationError("Please check the highlighted fields.", errors=[{field: [message]}])


def _check_day(field: str, day: date, today: date, *, back: int, ahead: int) -> None:
    if day > today + timedelta(days=ahead):
        raise _field_error(field, "That date can't be in the future." if ahead == 0 else "That date is too far ahead.")
    if day < today - timedelta(days=back):
        raise _field_error(field, "That date is too long ago.")


def _parse_day(field: str, text: str) -> date:
    try:
        if ISO_DAY.match(text):
            return date.fromisoformat(text)
    except ValueError:
        pass
    raise _field_error(field, "Use a date like 2026-10-12.")


# ------------------------------------------------------------------ settings


def get_settings(user) -> dict:
    row = repo.settings_for(user.id)
    return {"settings": _settings(row) if row else None}


def put_settings(user, body: dict) -> dict:
    _check_day("balance_on", body["balance_on"], _today(), back=MAX_DAYS_BACK, ahead=0)
    row = repo.save_settings(user.id, body)
    db.session.commit()
    return {"settings": _settings(row)}


# ------------------------------------------------------------ income sources


def list_sources(user) -> dict:
    return {"income_sources": [_source(s) for s in repo.sources_for(user.id)]}


def add_source(user, body: dict) -> dict:
    today = _today()
    if repo.count_sources(user.id) >= MAX_SOURCES:
        raise _field_error("income_sources", f"You can keep up to {MAX_SOURCES} income sources.")
    if body["expected_on"] is not None:
        _check_day("expected_on", body["expected_on"], today, back=PAST_DAYS, ahead=MAX_DAYS_BACK)
    row = IncomeSource(user_id=user.id, **body)
    repo.add(row)
    db.session.flush()
    _materialize(user.id, today)
    db.session.commit()
    return {"income_source": _source(row)}


def replace_source(user, source_id: uuid.UUID, body: dict) -> dict:
    """A changed source makes its unreceived payments again, from its new schedule and amount."""
    row = _my_source(user, source_id)
    today = _today()
    if body["expected_on"] is not None:
        _check_day("expected_on", body["expected_on"], today, back=PAST_DAYS, ahead=MAX_DAYS_BACK)
    for key, value in body.items():
        setattr(row, key, value)
    repo.clear_upcoming(row.id, today - timedelta(days=PAST_DAYS))
    db.session.flush()
    _materialize(user.id, today)
    db.session.commit()
    return {"income_source": _source(row)}


def delete_source(user, source_id: uuid.UUID) -> dict:
    """The source goes, with its payments."""
    repo.delete(_my_source(user, source_id))
    db.session.commit()
    return {}


def _my_source(user, source_id: uuid.UUID) -> IncomeSource:
    row = repo.source(user.id, source_id)
    if row is None:
        raise NotFoundError("We couldn't find that income source.", code="INCOME_SOURCE_NOT_FOUND")
    return row


# ---------------------------------------------------------------- payments


def _occurrences(source: IncomeSource, start: date, end: date) -> list[date]:
    """A one-off source's date, or a monthly source's days from start to end (the 31st is a month's last day)."""
    if source.expected_on is not None:
        return [source.expected_on]
    out, year, month = [], start.year, start.month
    while True:
        when = date(year, month, min(source.day_of_month, calendar.monthrange(year, month)[1]))
        if when > end:
            return out
        if when >= start:
            out.append(when)
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)


def _materialize(user_id: uuid.UUID, today: date) -> None:
    """Every expected payment from a month ago to the runway's horizon, made once."""
    horizon = load_config()["runway"]["horizon_days"]
    start, end = today - timedelta(days=PAST_DAYS), today + timedelta(days=horizon)
    repo.ensure_payments(
        [
            {
                "user_id": user_id,
                "income_source_id": s.id,
                "scheduled_on": when,
                "expected_on": when,
                "amount_cents": s.amount_cents,
                "received_on": None,
            }
            for s in repo.sources_for(user_id)
            for when in _occurrences(s, start, end)
        ]
    )


def _payments(user_id: uuid.UUID, today: date) -> list[ExpectedPayment]:
    _materialize(user_id, today)
    db.session.commit()
    return repo.payments_for(user_id, today - timedelta(days=PAST_DAYS))


def list_payments(user) -> dict:
    today = _today()
    return {"payments": [_payment(p, today) for p in _payments(user.id, today)]}


def update_payment(user, payment_id: uuid.UUID, body: dict) -> dict:
    row = repo.payment(user.id, payment_id)
    if row is None:
        raise NotFoundError("We couldn't find that payment.", code="PAYMENT_NOT_FOUND")
    today = _today()
    if "expected_on" in body:
        _check_day("expected_on", body["expected_on"], today, back=PAST_DAYS, ahead=MAX_DAYS_BACK)
        row.expected_on = body["expected_on"]
    if "amount_cents" in body:
        row.amount_cents = body["amount_cents"]
    if "received" in body:
        row.received_on = today if body["received"] else None
    db.session.commit()
    return {"payment": _payment(row, today)}


# ---------------------------------------------------------------- spending


def list_spending(user, days: int) -> dict:
    """The last `days` days' entries, newest first."""
    rows = repo.spending_since(user.id, _today() - timedelta(days=days - 1))
    return {"spending": [_spending(e) for e in reversed(rows)]}


def put_spending(user, spent_on_text: str, amount_cents: int) -> dict:
    """One number per day: logging a day again replaces it."""
    spent_on = _parse_day("spent_on", spent_on_text)
    _check_day("spent_on", spent_on, _today(), back=MAX_DAYS_BACK, ahead=0)
    row = repo.spending_on(user.id, spent_on) or SpendingEntry(user_id=user.id, spent_on=spent_on)
    row.amount_cents = amount_cents
    repo.add(row)
    db.session.commit()
    return {"spending": _spending(row)}


def delete_spending(user, spent_on_text: str) -> dict:
    row = repo.spending_on(user.id, _parse_day("spent_on", spent_on_text))
    if row is None:
        raise NotFoundError("Nothing is logged for that day.", code="SPENDING_NOT_FOUND")
    repo.delete(row)
    db.session.commit()
    return {}


# ----------------------------------------------------------------- summary


def _balance(user_id: uuid.UUID, settings: MoneySettings, today: date) -> tuple[int, list[str]]:
    spent = repo.spending_between(user_id, settings.balance_on, today)
    received = repo.received_between(user_id, settings.balance_on, today)
    balance = settings.balance_cents - spent + received
    lines = [f"Your balance: about {rand(balance)}."]
    if settings.balance_on < today:
        lines.append(
            f"You entered {rand(settings.balance_cents)} on {long_day(settings.balance_on)}. Since then you've logged "
            f"{rand(spent)} of spending and marked {rand(received)} received."
        )
    return balance, lines


def summary(user, late: bool) -> dict:
    """How long the money lasts, what's safe to spend, and the life fund, on today's date. With
    `late`, the next payment arrives two weeks late (the late days are set in config.yaml)."""
    today = _today()
    cfg = load_config()
    runway_cfg = cfg["runway"]
    late_days = runway_cfg["late_days"] if late else 0
    out = {"today": today.isoformat(), "late": late, "late_days": runway_cfg["late_days"]}
    settings = repo.settings_for(user.id)
    if settings is None:
        return out | {
            "ready": False,
            "lines": ["Add your balance and what you spend on essentials each day to see how long your money lasts."],
        }

    rows = _payments(user.id, today)
    arrivals = [Arrival(p.source.label, p.expected_on, p.amount_cents, p.received_on is not None) for p in rows]
    balance, balance_lines = _balance(user.id, settings, today)
    history = [(e.spent_on, e.amount_cents) for e in repo.spending_since(user.id, today - timedelta(days=PACE_DAYS))]
    pace = spending_pace(history, cfg)
    earliest = latest = None
    if pace is not None:
        forecast = forecast_runway(balance, today, arrivals, pace, late_days, runway_cfg["horizon_days"])
        runway: RunwayResult = forecast.likely
        earliest, latest = forecast.earliest.runs_out_on, forecast.latest.runs_out_on
        runway_lines = [forecast.explanation]
        pace_out = {
            "from": "spending",
            "daily_cents": pace.daily_cents,
            "low_cents": pace.low_cents,
            "high_cents": pace.high_cents,
            "days_logged": pace.days_of_history,
            "lines": [pace.explanation],
        }
    else:
        essentials = settings.essentials_per_day_cents
        runway = project_runway(balance, today, arrivals, essentials, late_days, runway_cfg["horizon_days"])
        runway_lines = [runway.explanation]
        pace_out = {
            "from": "essentials",
            "daily_cents": essentials,
            "low_cents": None,
            "high_cents": None,
            "days_logged": len(history),
            "lines": [
                f"Log at least {cfg['forecast']['min_days_of_history']} days of spending for a forecast. "
                f"Until then this uses your essentials: {rand(essentials)} a day."
            ],
        }
    if late:
        runway_lines.insert(0, f"If your next payment arrives {late_days} days late:")

    safe = safe_to_spend(
        balance, today, arrivals, settings.essentials_per_day_cents, settings.life_fund_reserve_cents,
        late_days=late_days,
    )
    week = week_service.this_week(user, today)
    fund = life_fund_signal(runway, week, today, runway_cfg["buffer_days"])
    notes = [WEEK_NOT_YET] if week is None else []
    nxt = runway.next_payment
    next_out = None
    if nxt is not None:
        next_out = {
            "label": nxt.label,
            "expected_on": nxt.expected_on.isoformat(),
            "lands_on": runway.next_payment_on.isoformat() if runway.next_payment_on else None,
            "amount_cents": nxt.amount_cents,
        }
        source = next((p.source for p in rows if p.received_on is None and p.expected_on == nxt.expected_on
                       and p.source.label == nxt.label), None)
        if source is not None and source.reliability in LATE_PRONE and not late:
            notes.append(f"You said {nxt.label} can arrive late: switch on \"late\" to plan for it.")

    return out | {
        "ready": True,
        "balance": {
            "cents": balance,
            "entered_cents": settings.balance_cents,
            "entered_on": settings.balance_on.isoformat(),
            "lines": balance_lines,
        },
        "pace": pace_out,
        "runway": {
            "scenario": runway.scenario,
            "runs_out_on": runway.runs_out_on.isoformat() if runway.runs_out_on else None,
            "days": runway.days,
            "earliest_on": earliest.isoformat() if earliest else None,
            "latest_on": latest.isoformat() if latest else None,
            "short_before_next": runway.short_before_next,
            "lines": runway_lines,
        },
        "safe_to_spend": {
            "per_day_cents": safe.per_day_cents,
            "days_until_next": safe.days_until_next,
            "essentials_cents": safe.essentials_cents,
            "reserve_cents": safe.reserve_cents,
            "lines": [safe.explanation],
        },
        "life_fund": {
            "state": fund.state,
            "reason": fund.reason,
            "resume_hint": fund.resume_hint,
            "reserve_cents": settings.life_fund_reserve_cents,
        },
        "this_week": {"colour": week.colour, "reason": week.reason} if week is not None else None,
        "next_payment": next_out,
        "notes": notes,
    }


# ----------------------------------------------------------------- erasing


def erase_all_for(user) -> None:
    """Every money record of this student, deleted for real: the demo's daily reset (and DELETE /me's later)."""
    repo.erase_all(user.id)
    db.session.commit()


# ------------------------------------------------------------- what's sent


def _settings(s: MoneySettings) -> dict:
    return {
        "balance_cents": s.balance_cents,
        "balance_on": s.balance_on.isoformat(),
        "essentials_per_day_cents": s.essentials_per_day_cents,
        "life_fund_reserve_cents": s.life_fund_reserve_cents,
    }


def _source(s: IncomeSource) -> dict:
    return {
        "id": str(s.id),
        "label": s.label,
        "amount_cents": s.amount_cents,
        "day_of_month": s.day_of_month,
        "expected_on": s.expected_on.isoformat() if s.expected_on else None,
        "reliability": s.reliability,
    }


def _payment(p: ExpectedPayment, today: date) -> dict:
    return {
        "id": str(p.id),
        "income_source_id": str(p.income_source_id),
        "label": p.source.label,
        "scheduled_on": p.scheduled_on.isoformat(),
        "expected_on": p.expected_on.isoformat(),
        "amount_cents": p.amount_cents,
        "received": p.received_on is not None,
        "received_on": p.received_on.isoformat() if p.received_on else None,
        "overdue": p.received_on is None and p.expected_on < today,
    }


def _spending(e: SpendingEntry) -> dict:
    return {"spent_on": e.spent_on.isoformat(), "amount_cents": e.amount_cents}
