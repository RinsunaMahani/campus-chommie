"""
What the funding pack tells learners and other features. The course finder reads it here,
never through the repository. Services call the engine; routes never do.

Public and stateless: the list, one funder in full, and the funding a course-finder choice
could look at. Nothing is stored or logged, and nothing about the learner is asked: who can
apply is shown in each funder's own words.

A pack nobody has checked yet is still served, with `confirmed: false` and a notice the app
shows next to it.
"""
from __future__ import annotations

from datetime import date

from campus_engine import funding as engine
from campus_engine.applications import Group, Guide, WindowStatus
from campus_engine.schemas import FIELDS, Funder, FundingPack
from campus_engine.text import read_from
from src.core.exceptions import NotFoundError
from src.shared.clock.clock import today_sast

from ..repositories.pack_repository import funding_pack


def pack() -> FundingPack:
    """The whole funding pack: NSFAS, which every plan shows, and the bursaries matched by field."""
    return funding_pack()


def confirmation(funding: FundingPack) -> dict:
    """Whether a person has checked the pack, and, if not, where its facts come from and when they were read."""
    notice = read_from("each funder's own pages", [s.retrieved for s in funding.sources])
    confirmed = funding.release and bool(funding.sources) and all(s.human_verified for s in funding.sources)
    return {"confirmed": confirmed, "notice": None if confirmed else notice}


def _today() -> date:
    """Today in South Africa, or a preview's test date (src/shared/clock)."""
    return today_sast()


def funding_list(*, fields: list[str] | None = None, status: str | None = None, kind: str | None = None,
                 stage: str | None = None) -> dict:
    """Every funder, or those the learner filtered for, open ones first, with the counts the list
    starts with and the fields to filter by."""
    funding, today = pack(), _today()
    found = engine.cards(funding, today, fields=fields, status=status, kind=kind, stage=stage)
    counts = engine.counts(found)
    return {
        "today": today.isoformat(),
        "summary": counts.line,
        "counts": {"total": counts.total, "open_now": counts.open_now, "closing_soon": counts.closing_soon},
        "fields": [{"id": tag, "label": label, "funders": n} for tag, label, n in engine.field_counts(funding)],
        "funders": [_card(c) for c in found],
        # The same funders grouped, so the app never shows one endless list (ids point into "funders").
        "sections": [_section(s) for s in engine.sections(found)],
        "missing_middle": _section(mm) if (mm := engine.missing_middle(funding, found)) else None,
        **confirmation(funding),
    }


def _section(s: engine.Section) -> dict:
    return {"id": s.id, "title": s.title, "line": s.line, "funder_ids": [c.funder.id for c in s.cards]}


def detail(funder_id: str) -> dict:
    """One funder in full: who can apply, what it covers, what it asks in return, how to apply and
    every intake's dates, with the source of each."""
    funding = pack()
    funder = next((f for f in funding.funders if f.id == funder_id), None)
    if funder is None:
        raise NotFoundError("We don't have that funder.", code="FUNDER_NOT_FOUND")
    today = _today()
    card, guide = engine.detail(funding, funder, today)
    return {
        "today": today.isoformat(),
        "funder": {
            **_card(card),
            "who_can_apply": _group(guide.who_can_apply),
            "covers": _group(engine.group(funding, funder.covers)),
            "obligations": _group(engine.group(funding, funder.obligations)),
            "apply": _guide(guide),
            "sources": [
                {"url": s.url, "publisher": s.publisher, "title": s.title,
                 "retrieved": _iso(s.retrieved), "last_verified": _iso(s.last_verified)}
                for s in funding.sources if s.id in _cited(funder)
            ],
        },
        **confirmation(funding),
    }


def has(funder_id: str) -> bool:
    """Whether the pack lists this funder."""
    return any(f.id == funder_id for f in pack().funders)


def saved_list(saved: dict[str, date], today: date) -> dict:
    """The funders a student saved (id -> the day they saved it) that the pack still lists, open first,
    each card with the day it was saved, and the line the list starts with."""
    found = [c for c in engine.cards(pack(), today) if c.funder.id in saved]
    counts = engine.counts(found)
    return {
        "today": today.isoformat(),
        "summary": counts.line,
        "counts": {"total": counts.total, "open_now": counts.open_now, "closing_soon": counts.closing_soon},
        "funders": [{**_card(c), "saved_on": saved[c.funder.id].isoformat()} for c in found],
        **confirmation(pack()),
    }


def saved_card(funder_id: str, saved_on: date, today: date) -> dict:
    """One saved funder's card, with the day it was saved."""
    funding = pack()
    return {**_card(engine.card(funding, funding.funder(funder_id), today)), "saved_on": saved_on.isoformat()}


def reminders(saved: dict[str, date], today: date) -> list[engine.Reminder]:
    """What to tell a student today about the funders they saved."""
    return engine.reminders(pack(), saved, today)


def short_name(funder_id: str) -> str | None:
    return next((f.short_name for f in pack().funders if f.id == funder_id), None)


def for_programme(fields: list[str], university: str, today: date) -> dict:
    """The funding a course-finder choice could look at: the best few, how many there are in all,
    and the fields to search the full list by."""
    found = engine.matches(pack(), fields, university, today)
    return {
        "fields": found.fields,
        "count": found.count,
        "open_now": found.open_now,
        "lines": found.lines,
        "funders": [_card(c) for c in found.cards],
    }


def _iso(d: date | None) -> str | None:
    return d.isoformat() if d else None


def _cited(funder: Funder) -> set[str]:
    groups = (funder.who_can_apply, funder.covers, funder.obligations, funder.tips, funder.warnings, funder.at_registration,
              funder.income)
    return {g.source for g in groups if g} | {sid for _, sid in funder.applications.citations()}


def _card(c: engine.Card) -> dict:
    f, w = c.funder, c.window
    return {
        "id": f.id,
        "name": f.name,
        "short_name": f.short_name,
        "kind": f.kind,
        "kind_label": engine.KIND_LABELS[f.kind],
        "sector": f.sector,
        "sector_label": engine.SECTOR_LABELS[f.sector],
        "any_field": f.fields == "any",
        "fields": [] if f.fields == "any" else [{"id": t, "label": FIELDS[t]} for t in f.fields],
        "not_fields": [{"id": t, "label": FIELDS[t]} for t in f.not_fields],
        "stages": [{"id": s, "label": engine.STAGE_LABELS[s]} for s in f.stages],
        "study_at": f.study_at,
        "applying": f.applying,
        "status": c.status,
        "label": c.label,
        "intake": w.intake if w else None,
        "heading": w.heading if w else None,
        "opens": _iso(w.opens) if w else None,
        "closes": _iso(w.closes) if w else None,
        "next_date": _iso(w.next_date) if w else None,
        "days": c.days,
        "lines": c.lines,
        "why": c.why,
        "income_says": f.income.says if f.income else None,  # the funder's own words; never asked of the learner
        "url": c.url,
        "source_url": c.source_url,
        "checked": _iso(c.checked),
    }


def _group(g: Group | None) -> dict | None:
    return {"items": g.items, "source_url": g.source_url} if g else None


def _window(w: WindowStatus) -> dict:
    return {
        "intake": w.intake,
        "heading": w.heading,
        "status": w.status,
        "label": w.label,
        "opens": _iso(w.opens),
        "closes": _iso(w.closes),
        "late_opens": _iso(w.late_opens),
        "late_closes": _iso(w.late_closes),
        "next_date": _iso(w.next_date),
        "days": w.days,
        "lines": w.lines,
        "source_url": w.source_url,
    }


def _guide(g: Guide) -> dict:
    return {
        "url": g.url,
        "how": g.how,
        "fee_cents": g.fee_cents,
        "fee_note": g.fee_note,
        "contact": g.contact,
        "documents": _group(g.documents),
        "after": [{"text": a.text, "source_url": a.source_url} for a in g.after],
        "tips": _group(g.tips),
        "warnings": _group(g.warnings),
        "windows": [_window(w) for w in g.windows],
        "lines": g.lines,
        "source_url": g.source_url,
    }
