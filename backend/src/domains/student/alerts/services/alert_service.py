"""
The student's alerts and their campus support. Alerts come from the engine
over the student's own records: the coming weeks (verified class events
only), how long their money lasts with the next payment on time, and where
they stand in each module. Every action names where it leads; one that
leads to campus support carries the campus's own service from the data pack
when it has one. Nothing is stored, and everything read is the signed-in
student's own.

Crisis lines require human review or dated official university provenance,
under Rinsuna's verification decision of 25 October 2026.
"""
from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

from campus_engine.alerts import Alert, alerts_for, module_alert
from campus_engine.config import load_config
from campus_engine.schemas import Source, SupportService, University
from src.domains.catalogue.universities.services import university_service as catalogue
from src.domains.classes.events.services import week_service
from src.domains.student.academics.services import academics_service as academics
from src.domains.student.money.services import money_service as money
from src.domains.student.profile.services import profile_service as profile

from ..constants import CRISIS_HELD, EXTRA_KINDS, NO_CAMPUS, NO_CLASSES, NO_MONEY, NOT_VERIFIED, SUPPORT_KINDS, TIMEZONE


def _today() -> date:
    """Today in South Africa: every student's day."""
    return datetime.now(ZoneInfo(TIMEZONE)).date()


def _checked(source: Source | None) -> bool:
    """Crisis contacts retain the human-review or official-university evidence requirement."""
    return source is not None and (source.human_verified or source.verification_basis == "official_university")


def _campus(user) -> tuple[University | None, str | None]:
    university, campus = profile.place_of(user)
    return (catalogue.packs().get(university) if university else None), campus


def _shown(uni: University, campus: str | None) -> list[tuple[SupportService, Source | None]]:
    """The campus's support services (one with no campuses is for all), crisis lines only once checked."""
    sources = {s.id: s for s in uni.sources}
    out = []
    for s in uni.support_services:
        if s.campuses and campus not in s.campuses:
            continue
        source = sources.get(s.source)
        if s.kind == "crisis" and not _checked(source):
            continue
        out.append((s, source))
    return out


def _service(s: SupportService, source: Source | None) -> dict:
    return {
        "name": s.name,
        "contact": s.contact,
        "hours": s.hours,
        "note": s.note,
        "source_url": source.url if source else None,
        "read_on": source.retrieved.isoformat() if source and source.retrieved else None,
        "last_verified": source.last_verified.isoformat() if source and source.last_verified else None,
    }


# ----------------------------------------------------------------- support


def support(user) -> dict:
    """Every kind of support the brief lists, for the student's campus: its services, or "Not verified yet"."""
    uni, campus = _campus(user)
    if uni is None:
        return {"university": None, "campus": None, "campus_name": None, "kinds": [], "lines": [NO_CAMPUS]}
    shown = _shown(uni, campus)
    present = {s.kind for s, _ in shown}
    crisis_in_pack = any(
        s.kind == "crisis" and (not s.campuses or campus in s.campuses) for s in uni.support_services
    )
    kinds = []
    for kind in SUPPORT_KINDS + tuple(k for k in EXTRA_KINDS if k in present):
        services = [_service(s, source) for s, source in shown if s.kind == kind]
        line = None
        if not services:
            line = CRISIS_HELD if kind == "crisis" and crisis_in_pack else NOT_VERIFIED
        kinds.append({"kind": kind, "services": services, "line": line})
    campuses = {c.id: c.name for c in uni.campuses}
    return {
        "university": {"id": uni.university, "name": uni.name, **catalogue.confirmation(uni)},
        "campus": campus,
        "campus_name": campuses.get(campus) if campus else None,
        "kinds": kinds,
        "lines": [],
    }


# ------------------------------------------------------------------ alerts


def alerts(user) -> dict:
    """Today's alerts, most pressing first: the engine's week-and-money alerts, then any module whose
    target is out of reach."""
    today = _today()
    lookahead = load_config()["alerts"]["lookahead_weeks"]
    weeks = week_service.loads(user, today, lookahead)
    runway = money.runway_for(user, today)
    found = alerts_for(weeks, runway, lookahead)
    found += [module_alert(code, target, why) for code, target, why in academics.out_of_reach(user)]

    uni, campus = _campus(user)
    first: dict[str, dict] = {}
    for s, source in _shown(uni, campus) if uni else []:
        first.setdefault(s.kind, _service(s, source))
    notes = []
    if not weeks:
        notes.append(NO_CLASSES)
    if runway is None:
        notes.append(NO_MONEY)
    return {"today": today.isoformat(), "alerts": [_alert(a, first) for a in found], "notes": notes}


def _alert(a: Alert, first: dict[str, dict]) -> dict:
    return {
        "kind": a.kind,
        "title": a.title,
        "message": a.message,
        "actions": [
            {
                "text": x.text,
                "target": x.target,
                "support_kind": x.support_kind,
                # The campus's own service, when the pack has one; otherwise the app opens Support.
                "service": first.get(x.support_kind) if x.support_kind else None,
            }
            for x in a.actions
        ],
    }
