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
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from campus_engine.checkin import checkin_streak, checkin_window, is_checkin_day, week_ending_date
from campus_engine.config import load_config
from campus_engine.forecast import forecast_runway, spending_pace
from campus_engine.lifefund import life_fund_signal
from campus_engine.money_health import check_money_health
from campus_engine.money_plan import Goal, afford, goal_pace, payday_plan, pot_pace
from campus_engine.runway import ExpectedPayment as Arrival, FixedCost as EngineFixedCost
from campus_engine.runway import RunwayResult, project_runway, safe_to_spend
from campus_engine.text import long_day, rand
from src.core.exceptions import NotFoundError, ValidationError
from src.domains.catalogue.universities.services import university_service as catalogue
from src.domains.classes.events.services import week_service
from src.domains.student.profile.services import profile_service as profile
from src.extensions import db

from ..constants import (
    CHECKIN_DAYS,
    DEFAULT_CHECKIN_DAY,
    FIXED_COST_LABEL_MAX,
    GOAL_DAYS_AHEAD,
    MAX_CENTS,
    MAX_DAYS_BACK,
    MAX_FIXED_COSTS,
    MAX_GOALS,
    MAX_SOURCES,
    PACE_DAYS,
    PAST_DAYS,
    TIMEZONE,
    UNIVERSITY_DATES_AHEAD,
)
from ..models import (
    ExpectedPayment,
    FixedCost,
    IncomeSource,
    MoneyGoal,
    MoneySettings,
    SpendingEntry,
    WeeklyCheckin,
)
from ..repositories import money_repository as repo

ISO_DAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")
LATE_PRONE = ("sometimes_late", "often_late")
WEEK_NOT_YET = "Your week isn't part of this yet: tests and exams count once you've joined your classes."
NO_CAMPUS = "Choose your university and campus in your profile to see what's near you."
NOTHING_NEAR = "Nothing near your campus is listed yet: we only list places whose prices we've found on their own pages."


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
    if "checkin_day" in body and body["checkin_day"] not in CHECKIN_DAYS:
        raise _field_error("checkin_day", "Choose a valid day of the week.")
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


@dataclass
class _Projection:
    rows: list[ExpectedPayment]
    arrivals: list[Arrival]
    balance: int
    balance_lines: list[str]
    runway: RunwayResult
    earliest: date | None
    latest: date | None
    runway_lines: list[str]
    pace_out: dict
    fixed_costs: list[EngineFixedCost]


def _project(user, settings: MoneySettings, today: date, late_days: int, cfg: dict) -> _Projection:
    """The balance now and how long it lasts: from the spending pace once there's enough of it,
    from the student's essentials estimate until then."""
    runway_cfg = cfg["runway"]
    rows = _payments(user.id, today)
    arrivals = [Arrival(p.source.label, p.expected_on, p.amount_cents, p.received_on is not None) for p in rows]
    balance, balance_lines = _balance(user.id, settings, today)
    history = [(e.spent_on, e.amount_cents) for e in repo.spending_since(user.id, today - timedelta(days=PACE_DAYS))]
    pace = spending_pace(history, cfg)
    costs = repo.fixed_costs_for(user.id)
    engine_fixed_costs = [
        EngineFixedCost(label=c.label, amount_cents=c.amount_cents, day_of_month=c.day_of_month)
        for c in costs
    ]
    earliest = latest = None
    if pace is not None:
        forecast = forecast_runway(
            balance, today, arrivals, pace, late_days, runway_cfg["horizon_days"], fixed_costs=engine_fixed_costs
        )
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
        runway = project_runway(
            balance, today, arrivals, essentials, late_days, runway_cfg["horizon_days"], fixed_costs=engine_fixed_costs
        )
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
    return _Projection(
        rows, arrivals, balance, balance_lines, runway, earliest, latest, runway_lines, pace_out, engine_fixed_costs
    )


def runway_for(user, today: date) -> RunwayResult | None:
    """How long the money lasts with the next payment on time, for the alerts; None before the student
    has entered their balance."""
    settings = repo.settings_for(user.id)
    if settings is None:
        return None
    return _project(user, settings, today, 0, load_config()).runway


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

    p = _project(user, settings, today, late_days, cfg)
    rows, arrivals, balance, balance_lines = p.rows, p.arrivals, p.balance, p.balance_lines
    runway, earliest, latest, runway_lines, pace_out = p.runway, p.earliest, p.latest, p.runway_lines, p.pace_out
    if late:
        runway_lines.insert(0, f"If your next payment arrives {late_days} days late:")

    safe = safe_to_spend(
        balance, today, arrivals, settings.essentials_per_day_cents, settings.life_fund_reserve_cents,
        late_days=late_days, fixed_costs=p.fixed_costs,
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
            "fixed_costs_cents": safe.fixed_costs_cents,
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


# ------------------------------------------------------------ looking ahead

NO_SETTINGS = "Add your balance and what you spend on essentials each day first."


def _need_settings(user) -> MoneySettings:
    settings = repo.settings_for(user.id)
    if settings is None:
        raise _field_error("money", NO_SETTINGS)
    return settings


def can_i_afford(user, amount_cents: int) -> dict:
    """What buying something for `amount_cents` today does to how long the money lasts. Nothing is stored or
    logged: the price is used once and dropped."""
    today = _today()
    cfg = load_config()
    settings = _need_settings(user)
    p = _project(user, settings, today, 0, cfg)
    a = afford(amount_cents, p.balance, today, p.arrivals, p.runway.daily_spend_cents,
               settings.essentials_per_day_cents, settings.life_fund_reserve_cents, cfg["runway"]["horizon_days"],
               fixed_costs=p.fixed_costs)
    return {
        "verdict": a.verdict,
        "days_before": a.days_before,
        "days_after": a.days_after,
        "wait_until": a.wait_until.isoformat() if a.wait_until else None,
        "lines": a.lines,
    }


def _goal(g: MoneyGoal, today: date) -> dict:
    per_week, line = pot_pace(g.kind, g.amount_cents, g.saved_cents, g.due_on, today, g.stokvel_funded)
    return {
        "id": str(g.id),
        "label": g.label,
        "kind": g.kind,
        "amount_cents": g.amount_cents,
        "saved_cents": g.saved_cents,
        "due_on": g.due_on.isoformat() if g.due_on else None,
        "due_day": long_day(g.due_on) if g.due_on else None,
        "from_university": g.from_university,
        "stokvel_funded": g.stokvel_funded,
        "per_week_cents": per_week,
        "lines": [line],
    }


def university_dates(user, today: date) -> list[dict]:
    """The student's university's own fee dates coming up (dates only: amounts always come from the student)."""
    university, _campus = profile.place_of(user)
    uni = catalogue.packs().get(university) if university else None
    if uni is None:
        return []
    sources = {s.id: s for s in uni.sources}
    ahead = today + timedelta(days=UNIVERSITY_DATES_AHEAD)
    out = []
    for f in sorted(uni.funding_cycles, key=lambda f: f.when):
        if f.funder == "university" and f.kind in ("fee_due", "discount_deadline") and today <= f.when <= ahead:
            source = sources.get(f.source)
            out.append({"name": f.name, "kind": f.kind, "on": f.when.isoformat(), "day": long_day(f.when),
                        "source_url": source.url if source else None})
    return out


def plan(user) -> dict:
    """Looking ahead: the payday plan for the next payment, the student's goals and pots, fixed costs, and their university's fee dates
    coming up (to turn into goals)."""
    today = _today()
    settings = repo.settings_for(user.id)
    goals = repo.goals_for(user.id)
    costs = repo.fixed_costs_for(user.id)
    engine_fixed_costs = [
        EngineFixedCost(label=c.label, amount_cents=c.amount_cents, day_of_month=c.day_of_month)
        for c in costs
    ]
    out = {
        "goals": [_goal(g, today) for g in goals],
        "fixed_costs": [_fixed_cost(c) for c in costs],
        "university_dates": university_dates(user, today),
        "payday": None,
    }
    if settings is None:
        return out | {"lines": [NO_SETTINGS]}
    rows = _payments(user.id, today)
    arrivals = [Arrival(p.source.label, p.expected_on, p.amount_cents, p.received_on is not None) for p in rows]
    cfg = load_config()
    buffer_paydays = cfg.get("money_pots", {}).get("buffer_paydays", 1)
    pp = payday_plan(
        arrivals,
        today,
        settings.essentials_per_day_cents,
        [
            Goal(
                g.label,
                max(0, g.amount_cents - g.saved_cents),
                g.due_on,
                kind=g.kind,
                stokvel_funded=g.stokvel_funded,
                amount_cents=g.amount_cents,
            )
            for g in goals
        ],
        buffer_paydays=buffer_paydays,
        fixed_costs=engine_fixed_costs,
    )
    if pp is None:
        return out | {"lines": ["Add the money you expect (an allowance, a transfer, a wage) to plan your next payday."]}
    out["payday"] = {
        "lands_on": pp.lands_on.isoformat(),
        "day": long_day(pp.lands_on),
        "amount_cents": pp.amount_cents,
        "pots": [{"label": x.label, "cents": x.cents, "why": x.why} for x in pp.pots],
        "free_cents": pp.free_cents,
    }
    return out | {"lines": pp.lines}


def _check_goal_day(due_on: date, today: date) -> None:
    if not today <= due_on <= today + timedelta(days=GOAL_DAYS_AHEAD):
        raise _field_error("due_on", "Choose a date from today up to two years ahead.")


def _my_goal(user, goal_id: uuid.UUID) -> MoneyGoal:
    row = repo.goal(user.id, goal_id)
    if row is None:
        raise NotFoundError("That goal isn't one of yours.", code="MONEY_GOAL_NOT_FOUND")
    return row


def _clean_goal(fields: dict) -> dict:
    out = dict(fields)
    if "label" in out:
        out["label"] = " ".join(out["label"].split())
    return out


def add_goal(user, body: dict) -> dict:
    today = _today()
    kind = body.get("kind", "goal")
    if kind in ("goal", "big_purchase"):
        if not body.get("due_on"):
            raise _field_error("due_on", "Choose a date for this goal.")
        _check_goal_day(body["due_on"], today)
    else:
        if body.get("due_on") is not None:
            raise _field_error("due_on", "This pot does not use a date.")
    if repo.count_goals(user.id) >= MAX_GOALS:
        raise _field_error("goals", f"You can keep up to {MAX_GOALS} goals.")
    row = repo.add_goal(user.id, _clean_goal(body))
    db.session.commit()
    return {"goal": _goal(row, today)}


def change_goal(user, goal_id: uuid.UUID, body: dict) -> dict:
    today = _today()
    row = _my_goal(user, goal_id)
    clean = _clean_goal(body)
    new_kind = clean.get("kind", row.kind)
    if "due_on" in clean:
        if clean["due_on"] is not None:
            if new_kind not in ("goal", "big_purchase"):
                raise _field_error("due_on", "This pot does not use a date.")
            _check_goal_day(clean["due_on"], today)
        elif new_kind in ("goal", "big_purchase"):
            raise _field_error("due_on", "Choose a date for this goal.")
    elif "kind" in clean and clean["kind"] != row.kind:
        if clean["kind"] in ("goal", "big_purchase") and row.due_on is None:
            raise _field_error("due_on", "Choose a date for this goal.")
        if clean["kind"] in ("family", "stokvel", "buffer") and row.due_on is not None:
            row.due_on = None
    for key, value in clean.items():
        setattr(row, key, value)
    if row.saved_cents > row.amount_cents:
        db.session.rollback()
        raise _field_error("saved_cents", "That's more than the goal itself.")
    db.session.commit()
    return {"goal": _goal(row, today)}


def delete_goal(user, goal_id: uuid.UUID) -> dict:
    db.session.delete(_my_goal(user, goal_id))
    db.session.commit()
    return {}


# ------------------------------------------------------------ cheap things


def cheap_things(user) -> dict:
    """The data pack's cheap things to do near the student's campus, each with its cost note, its
    source, and when a person last checked it (None: not checked yet)."""
    university, campus = profile.place_of(user)
    uni = catalogue.packs().get(university) if university else None
    if uni is None:
        return {"university": None, "campus": None, "cheap_things": [], "lines": [NO_CAMPUS]}
    sources = {s.id: s for s in uni.sources}
    places = [c for c in uni.cheap_things if not c.campuses or campus in c.campuses]
    return {
        "university": {"id": uni.university, "name": uni.name, **catalogue.confirmation(uni)},
        "campus": campus,
        "cheap_things": [_cheap_thing(c, sources.get(c.source)) for c in places],
        "lines": [] if places else [NOTHING_NEAR],
    }


def _cheap_thing(c, source) -> dict:
    return {
        "name": c.name,
        "category": c.category,
        "cost_note": c.cost_note,
        "address": c.address,
        "hours": c.hours,
        "source_url": source.url if source else None,
        "read_on": source.retrieved.isoformat() if source and source.retrieved else None,
        "last_verified": source.last_verified.isoformat() if source and source.last_verified else None,
    }


# --------------------------------------------------------- export, erasing


def export_for(user) -> dict:
    """POPIA export: every money record the student entered, history included."""
    settings = repo.settings_for(user.id)
    today = _today()
    return {
        "settings": _settings(settings) if settings else None,
        "income_sources": [_source(s) for s in repo.sources_for(user.id)],
        "payments": [_payment(p, today) for p in repo.all_payments(user.id)],
        "spending": [_spending(e) for e in repo.all_spending(user.id)],
        "goals": [_goal(g, today) for g in repo.goals_for(user.id)],
        "fixed_costs": [_fixed_cost(c) for c in repo.all_fixed_costs(user.id)],
        "weekly_checkins": [_checkin_entry(c) for c in repo.all_checkins(user.id)],
    }


def erase_all_for(user) -> None:
    """Every money record of this student, deleted for real: the demo's daily reset (and DELETE /me's later)."""
    repo.erase_all(user.id)
    db.session.commit()


# ------------------------------------------------------------- fixed costs


def _fixed_cost(c: FixedCost) -> dict:
    return {
        "id": str(c.id),
        "label": c.label,
        "amount_cents": c.amount_cents,
        "day_of_month": c.day_of_month,
    }


def _clean_fixed_cost(fields: dict) -> dict:
    out = dict(fields)
    if "label" in out:
        out["label"] = " ".join(out["label"].split())
    return out


def list_fixed_costs(user) -> dict:
    return {"fixed_costs": [_fixed_cost(c) for c in repo.fixed_costs_for(user.id)]}


def add_fixed_cost(user, body: dict) -> dict:
    if repo.count_fixed_costs(user.id) >= MAX_FIXED_COSTS:
        raise _field_error("fixed_costs", f"You can keep up to {MAX_FIXED_COSTS} fixed costs.")
    clean = _clean_fixed_cost(body)
    row = repo.add_fixed_cost(user.id, clean)
    db.session.commit()
    return {"fixed_cost": _fixed_cost(row)}


def replace_fixed_cost(user, cost_id: uuid.UUID, body: dict) -> dict:
    row = repo.fixed_cost(user.id, cost_id)
    if row is None:
        raise NotFoundError("That fixed cost isn't one of yours.", code="FIXED_COST_NOT_FOUND")
    clean = _clean_fixed_cost(body)
    for key, value in clean.items():
        setattr(row, key, value)
    db.session.commit()
    return {"fixed_cost": _fixed_cost(row)}


def delete_fixed_cost(user, cost_id: uuid.UUID) -> dict:
    row = repo.fixed_cost(user.id, cost_id)
    if row is None:
        raise NotFoundError("That fixed cost isn't one of yours.", code="FIXED_COST_NOT_FOUND")
    repo.delete(row)
    db.session.commit()
    return {}


# ----------------------------------------------------------- weekly checkin


def _checkin_entry(c: WeeklyCheckin) -> dict:
    return {
        "id": str(c.id),
        "week_end": c.week_end.isoformat(),
        "amount_cents": c.amount_cents,
        "skipped": c.skipped,
    }


def get_checkin_status(user, today: date | None = None) -> dict:
    today = today or _today()
    settings = repo.settings_for(user.id)
    checkin_day = (
        getattr(settings, "checkin_day", DEFAULT_CHECKIN_DAY) or DEFAULT_CHECKIN_DAY
        if settings
        else DEFAULT_CHECKIN_DAY
    )
    curr_week_end = week_ending_date(today, checkin_day)
    start_date, end_date = checkin_window(curr_week_end)
    is_today_checkin = is_checkin_day(today, checkin_day)
    checkins = repo.checkins_for(user.id)
    checked_dates = [c.week_end for c in checkins]
    checked_this_week = curr_week_end in set(checked_dates)
    this_week_checkin = next((c for c in checkins if c.week_end == curr_week_end), None)
    streak = checkin_streak(checked_dates, today, checkin_day)
    return {
        "checkin_day": checkin_day,
        "is_checkin_day": is_today_checkin,
        "checked_in_this_week": checked_this_week,
        "week_start": start_date.isoformat(),
        "week_end": curr_week_end.isoformat(),
        "this_week": _checkin_entry(this_week_checkin) if this_week_checkin else None,
        "streak": {
            "weeks": streak.weeks,
            "line": streak.line,
        },
        "recent_checkins": [_checkin_entry(c) for c in checkins[:10]],
    }


def submit_checkin(user, body: dict) -> dict:
    today = _today()
    settings = repo.settings_for(user.id)
    checkin_day = (
        getattr(settings, "checkin_day", DEFAULT_CHECKIN_DAY) or DEFAULT_CHECKIN_DAY
        if settings
        else DEFAULT_CHECKIN_DAY
    )
    week_end = body.get("week_end") or week_ending_date(today, checkin_day)
    _check_day("week_end", week_end, today, back=MAX_DAYS_BACK, ahead=6)

    skipped = body.get("skipped", False)
    amount_cents = body.get("amount_cents")
    if skipped and amount_cents is not None:
        raise _field_error("amount_cents", "Leave amount empty when skipping check-in.")
    if not skipped and amount_cents is None:
        raise _field_error("amount_cents", "Enter this week's total spending or choose skip.")

    repo.add_or_update_checkin(user.id, week_end, amount_cents, skipped)

    if not skipped and amount_cents is not None:
        start_date, _ = checkin_window(week_end)
        daily = amount_cents // 7
        remainder = amount_cents % 7
        for i in range(7):
            day_date = start_date + timedelta(days=i)
            day_amount = daily + (remainder if i == 6 else 0)
            entry = repo.spending_on(user.id, day_date) or SpendingEntry(user_id=user.id, spent_on=day_date)
            entry.amount_cents = day_amount
            repo.add(entry)

    db.session.commit()
    return get_checkin_status(user, today)


def get_money_health(user, today: date | None = None) -> dict:
    """The student's five money health checks, strictly non-shaming and actionable."""
    today = today or _today()
    cfg = load_config()
    settings = repo.settings_for(user.id)
    raw_goals = repo.goals_for(user.id)
    engine_goals = [
        Goal(
            g.label,
            left_cents=max(0, g.amount_cents - g.saved_cents),
            due_on=g.due_on,
            kind=g.kind,
            stokvel_funded=g.stokvel_funded,
            amount_cents=g.amount_cents,
            saved_cents=g.saved_cents,
        )
        for g in raw_goals
    ]

    checkin_st = get_checkin_status(user, today)
    checked_in_this_week = checkin_st["checked_in_this_week"]
    streak_weeks = checkin_st["streak"]["weeks"]

    if settings is not None:
        p = _project(user, settings, today, 0, cfg)
        runway = p.runway
        safe = safe_to_spend(
            p.balance,
            today,
            p.arrivals,
            settings.essentials_per_day_cents,
            settings.life_fund_reserve_cents,
            fixed_costs=p.fixed_costs,
        )
        safe_daily = safe.per_day_cents
        plan = payday_plan(
            p.arrivals,
            today,
            p.runway.daily_spend_cents,
            engine_goals,
            fixed_costs=p.fixed_costs,
            buffer_paydays=cfg.get("money_pots", {}).get("buffer_paydays", 1),
        )
        checkin_day = (
            getattr(settings, "checkin_day", DEFAULT_CHECKIN_DAY) or DEFAULT_CHECKIN_DAY
        )
        curr_week_end = week_ending_date(today, checkin_day)
        start_date, _ = checkin_window(curr_week_end)
        this_week_spend = repo.spending_between(user.id, start_date - timedelta(days=1), today)
    else:
        runway = None
        safe_daily = None
        plan = None
        this_week_spend = None

    health = check_money_health(
        today=today,
        runway=runway,
        goals=engine_goals,
        this_week_spend_cents=this_week_spend,
        safe_per_day_cents=safe_daily,
        plan=plan,
        checked_in_this_week=checked_in_this_week,
        streak_weeks=streak_weeks,
        min_buffer_cents=cfg.get("money_health", {}).get("min_buffer_cents", 1),
    )

    return {
        "checks": [
            {
                "id": c.id,
                "title": c.title,
                "status": c.status,
                "line": c.line,
                "action": c.action,
                "target": c.target,
            }
            for c in health.checks
        ],
        "done_count": health.done_count,
        "total_count": health.total_count,
        "line": health.line,
    }


# ------------------------------------------------------------- what's sent


def _settings(s: MoneySettings) -> dict:
    return {
        "balance_cents": s.balance_cents,
        "balance_on": s.balance_on.isoformat(),
        "essentials_per_day_cents": s.essentials_per_day_cents,
        "life_fund_reserve_cents": s.life_fund_reserve_cents,
        "checkin_day": getattr(s, "checkin_day", DEFAULT_CHECKIN_DAY) or DEFAULT_CHECKIN_DAY,
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
