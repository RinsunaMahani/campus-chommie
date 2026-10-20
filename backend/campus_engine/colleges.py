"""Colleges as DHET lists them, the way a learner looks for one.

Public TVET colleges, and private colleges and higher education institutions with their place in DHET's
registers: registered, provisionally registered, or cancelled, plus DHET's own list of illegal ("bogus")
colleges. A learner can search them (by name, registration number, or a qualification such as
"electrician"), open one, or ask "is this college registered?" and get the answer in plain words.

No admission rules: colleges don't publish points scales, so nothing here says who qualifies. Every
answer names the register it comes from, and "not found" never means "bogus" (colleges offering only
occupational programmes register with the QCTO, not DHET).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .config import load_config
from .schemas import College, CollegesPack, OccupationalQualification, UnregisteredCollege
from .text import plural

PUBLIC, REGISTERED, PROVISIONAL, CANCELLED = "public", "registered", "provisionally_registered", "cancelled"
BOGUS, NOT_FOUND, SEVERAL = "bogus", "not_found", "several"

KIND_LABELS = {
    "tvet": "Public TVET college",
    "private_higher_education": "Private higher education institution",
    "private_college": "Private college",
}
STATUS_LABELS = {
    PUBLIC: "Public",
    REGISTERED: "Registered",
    PROVISIONAL: "Provisionally registered",
    CANCELLED: "Registration cancelled",
    BOGUS: "Illegal (bogus) college",
    NOT_FOUND: "Not found in DHET's lists",
    SEVERAL: "Several colleges match",
}
#: The order a check's matches come in: what a learner most needs to see first.
_STATUS_ORDER = {BOGUS: 0, CANCELLED: 1, PROVISIONAL: 2, REGISTERED: 3, PUBLIC: 3}

# Words that don't tell one college from another ("Damelin (Pty) Ltd" is "damelin").
_FILLER = {"pty", "ltd", "limited", "npc", "the", "of", "and", "t", "a", "rf", "inc", "incorporated"}

#: DHET's advice on cancelled private colleges (Register of Private Colleges, 15 July 2026, introduction).
CANCELLED_COLLEGE_ADVICE = (
    "DHET advises students not to enrol or part with money: students of a cancelled college will not sit "
    "for examinations nor be certificated."
)
NOT_IN_REGISTER_NOTE = (
    "Not being in these lists doesn't make a college bogus: colleges that offer only occupational "
    "programmes (such as N4 to N6 or SETA programmes) don't register with DHET; they must be accredited "
    "by the QCTO. Ask the college for its DHET registration number or its QCTO accreditation, and check it."
)


def _words(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in _FILLER]


def _reg_key(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def name_matches(name: str, query: str) -> bool:
    """Every word of the query starts a word of the name ("dam corr" matches "Damelin Correspondence")."""
    want, have = _words(query), _words(name)
    return bool(want) and all(any(h.startswith(w) for h in have) for w in want)


@dataclass
class Card:
    """One college in a list, with its status in words."""

    college: College
    lines: list[str]

    @property
    def label(self) -> str:
        return STATUS_LABELS[self.college.status]

    @property
    def kind_label(self) -> str:
        return KIND_LABELS[self.college.kind]


def _status_line(c: College, pack: CollegesPack) -> str:
    number = f" (registration number {c.registration_number})" if c.registration_number else ""
    if c.status == PUBLIC:
        return f"{c.name} is a public TVET college, under the Department of Higher Education and Training."
    if c.status == REGISTERED:
        return f"{c.name} is registered with the Department of Higher Education and Training{number}."
    if c.status == PROVISIONAL:
        return (f"{c.name} is provisionally registered{number}: it hasn't met every requirement for registration "
                "yet, and the Registrar expects it to within a set time.")
    line = f"DHET's register lists {c.name}'s registration{number} as cancelled."
    return f"{line} {CANCELLED_COLLEGE_ADVICE}" if c.kind == "private_college" else line


def _register_line(c: College, pack: CollegesPack) -> str | None:
    if not c.registration_number and c.kind != "tvet":
        return "The register shows no registration number for it."
    if c.kind != "tvet" and c.qualifications:
        return (f"It is registered for {plural(len(c.qualifications), 'qualification')}: it may offer only those, "
                "at the sites listed.")
    return None


def card(pack: CollegesPack, c: College) -> Card:
    return Card(c, [line for line in (_status_line(c, pack), _register_line(c, pack)) if line])


def _qualification_hit(c: College, offered: dict[str, list[OccupationalQualification]], query: str) -> bool:
    quals = c.qualifications + [q.name for q in offered.get(c.id, [])]
    return any(name_matches(q, query) for q in quals)


def occupational_by_college(pack: CollegesPack) -> dict[str, list[OccupationalQualification]]:
    by: dict[str, list[OccupationalQualification]] = {}
    for q in pack.occupational:
        for cid in q.colleges:
            by.setdefault(cid, []).append(q)
    return by


@dataclass
class Results:
    cards: list[Card]
    total: int
    lines: list[str]
    counts: dict[str, int] = field(default_factory=dict)


def search(pack: CollegesPack, *, query: str | None = None, kind: str | None = None, province: str | None = None,
           status: str | None = None) -> Results:
    """Colleges matching a search: by name first, then registration number, then a qualification they offer.
    Public colleges and registered institutions come before cancelled ones; names in A to Z order inside."""
    offered = occupational_by_college(pack)
    found: list[tuple[int, College]] = []
    for c in pack.colleges:
        if kind and c.kind != kind or province and province not in c.provinces or status and c.status != status:
            continue
        if not query:
            rank = 0
        elif name_matches(c.name, query):
            rank = 0
        elif c.registration_number and _reg_key(query) and _reg_key(query) == _reg_key(c.registration_number):
            rank = 0
        elif _qualification_hit(c, offered, query):
            rank = 1
        else:
            continue
        found.append((rank, c))
    order = {PUBLIC: 0, REGISTERED: 0, PROVISIONAL: 1, CANCELLED: 2}
    found.sort(key=lambda rc: (rc[0], order[rc[1].status], rc[1].name.lower()))
    cards = [card(pack, c) for _, c in found]
    counts = {s: sum(1 for x in cards if x.college.status == s) for s in (PUBLIC, REGISTERED, PROVISIONAL, CANCELLED)}
    return Results(cards, len(cards), [_summary(len(cards), counts, query)], counts)


def _summary(total: int, counts: dict[str, int], query: str | None) -> str:
    if not total:
        return f"No college in DHET's lists matches “{query}”." if query else "No colleges to show."
    parts = []
    if counts[PUBLIC]:
        parts.append(f"{counts[PUBLIC]} public")
    if counts[REGISTERED]:
        parts.append(f"{counts[REGISTERED]} registered")
    if counts[PROVISIONAL]:
        parts.append(f"{counts[PROVISIONAL]} provisionally registered")
    if counts[CANCELLED]:
        parts.append(f"{counts[CANCELLED]} cancelled")
    return f"{plural(total, 'college')}: " + ", ".join(parts) + "."


@dataclass
class Check:
    """The answer to "is this college registered?": a verdict, in words, with every institution it matched."""

    verdict: str
    lines: list[str]
    colleges: list[College]
    unregistered: list[UnregisteredCollege]

    @property
    def label(self) -> str:
        return STATUS_LABELS[self.verdict]


def check(pack: CollegesPack, query: str, cfg: dict | None = None) -> Check:
    """Look a name or registration number up in every DHET list we hold. One status when every match shares
    it; "several" when they differ, so a broad name ("Tshwane") never borrows one college's warning for the
    others. Each match is listed, most serious first (bogus, cancelled, provisional, then registered)."""
    cfg = cfg or load_config()
    limit = cfg["colleges"]["max_matches"]
    key = _reg_key(query)
    colleges = [c for c in pack.colleges
                if name_matches(c.name, query) or (c.registration_number and key == _reg_key(c.registration_number))]
    bogus = [u for u in pack.unregistered if name_matches(u.name, query)]
    colleges.sort(key=lambda c: (_STATUS_ORDER[c.status], c.name.lower()))
    colleges, bogus = colleges[:limit], bogus[:limit]

    if not colleges and not bogus:
        return Check(NOT_FOUND, [
            f"We couldn't find “{query}” in DHET's registers of private institutions or its list of public TVET colleges.",
            NOT_IN_REGISTER_NOTE,
        ], [], [])
    statuses = [BOGUS] * bool(bogus) + [c.status for c in colleges]
    verdict = statuses[0] if len(set(statuses)) == 1 else SEVERAL
    lines = []
    for u in bogus:
        lines.append(f"DHET lists “{u.name}” as an illegal (bogus) college: it is not registered, so its "
                     "qualifications are not recognised.")
    for c in colleges:
        lines.append(_status_line(c, pack))
    if len(colleges) + len(bogus) > 1:
        lines.append(f"{plural(len(colleges) + len(bogus), 'name')} matched: check which one you mean.")
    return Check(verdict, lines, colleges, bogus)
