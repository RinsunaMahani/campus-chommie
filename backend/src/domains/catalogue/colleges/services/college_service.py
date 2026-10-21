"""
What the colleges pack tells learners: the list (searchable and filtered), one college in full, and
"is this college registered?". Services call the engine; routes never do.

Public and stateless: nothing is stored or logged, and no search is kept. A pack nobody has checked yet
is still served, with `confirmed: false` and a notice the app shows next to it.
"""
from __future__ import annotations

import math

from campus_engine import colleges as engine
from campus_engine.config import load_config
from campus_engine.schemas import College, CollegesPack, Source
from src.core.exceptions import NotFoundError
from src.core.exceptions import ValidationError as ApiValidationError

from ..constants import UNCONFIRMED_NOTICE
from ..repositories.pack_repository import colleges_pack


def pack() -> CollegesPack:
    return colleges_pack()


def confirmation(colleges: CollegesPack) -> dict:
    """Whether a person has checked the pack, and the notice to show if not."""
    return {"confirmed": colleges.release, "notice": None if colleges.release else UNCONFIRMED_NOTICE}


def _min_chars(field: str, value: str | None) -> None:
    """A search shorter than the config's minimum would match nearly everything: refused, kindly."""
    least = load_config()["colleges"]["min_query_chars"]
    if value is not None and len(value.strip()) < least:
        raise ApiValidationError("Please check the highlighted fields.",
                                 errors=[{field: [f"Type at least {least} letters or numbers."]}])


def college_list(*, q: str | None = None, kind: str | None = None, province: str | None = None,
                 status: str | None = None, page: int = 1) -> dict:
    """The colleges matching a search or filters, a page at a time, with the line the list starts with."""
    _min_chars("q", q)
    colleges = pack()
    found = engine.search(colleges, query=q.strip() if q else None, kind=kind, province=province, status=status)
    size = load_config()["colleges"]["page_size"]
    pages = max(1, math.ceil(found.total / size))
    shown = found.cards[(page - 1) * size: page * size]
    return {
        "summary": found.lines[0],
        "counts": {"total": found.total, **found.counts},
        "total": found.total,
        "page": page,
        "pages": pages,
        "colleges": [_card(c) for c in shown],
        **confirmation(colleges),
    }


def check(name: str) -> dict:
    """Is this college registered? A verdict in words, every institution the name matched, DHET's signs of a
    bogus college, and the registers it was checked against."""
    _min_chars("name", name)
    colleges = pack()
    found = engine.check(colleges, name.strip())
    return {
        "verdict": found.verdict,
        "label": found.label,
        "lines": found.lines,
        "colleges": [_card(engine.card(colleges, c)) for c in found.colleges],
        "unregistered": [{"id": u.id, "name": u.name, "where": u.where,
                          "label": engine.STATUS_LABELS[engine.BOGUS]} for u in found.unregistered],
        "warning_signs": _signs(colleges),
        "sources": [_source(s) for s in colleges.sources],
        **confirmation(colleges),
    }


def detail(college_id: str) -> dict:
    """One college in full: its status in words, registration number, sites, registered qualifications (or a
    TVET college's occupational ones), the register's notes, and where each fact comes from."""
    colleges = pack()
    c = colleges.college(college_id)
    if c is None:
        raise NotFoundError("We don't have that college.", code="COLLEGE_NOT_FOUND")
    occupational = engine.occupational_by_college(colleges).get(c.id, [])
    return {
        "college": {
            **_card(engine.card(colleges, c)),
            "phone": c.phone,
            "head_office": list(c.head_office) if c.head_office else None,
            "sites": c.sites,
            "qualifications": c.qualifications,
            "notes": c.notes,
            "occupational": [
                {"saqa_id": q.saqa_id, "name": q.name, "nsfas_allowances": q.nsfas_allowances,
                 "centre_of_specialisation": c.id in q.centre_of_specialisation}
                for q in occupational
            ],
            "sources": [_source(s) for s in _cited(colleges, c, bool(occupational))],
        },
        "warning_signs": _signs(colleges) if c.status == engine.CANCELLED else None,
        **confirmation(colleges),
    }


def _cited(colleges: CollegesPack, c: College, occupational: bool) -> list[Source]:
    ids = [c.source] + ([q.source for q in colleges.occupational][:1] if occupational else [])
    return [s for s in colleges.sources if s.id in ids]


def _signs(colleges: CollegesPack) -> dict | None:
    signs = colleges.warning_signs
    if signs is None:
        return None
    source = colleges.source(signs.source)
    return {"items": signs.items, "source_url": source.url if source else None}


def _source(s: Source) -> dict:
    return {"url": s.url, "publisher": s.publisher, "title": s.title,
            "retrieved": s.retrieved.isoformat() if s.retrieved else None}


def _card(card: engine.Card) -> dict:
    c = card.college
    return {
        "id": c.id,
        "name": c.name,
        "kind": c.kind,
        "kind_label": card.kind_label,
        "status": c.status,
        "label": card.label,
        "registration_number": c.registration_number,
        "provinces": c.provinces,
        # Only a website that opened as the college's own: a dead or parked address is never a link.
        "website": c.website if not (c.website_check and not c.website_check.works) else None,
        "website_problem": None if not (c.website_check and not c.website_check.works) else {
            "listed": c.website, "note": c.website_check.note, "checked": c.website_check.checked.isoformat(),
        },
        "lines": card.lines,
    }
