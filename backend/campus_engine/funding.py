"""Funding on today's date, the way a learner browses it.

Every funder in the funding pack with the status that matters most today (open now, closing soon,
not open yet, closed, dates not published), the counts a list starts with ("3 open now, 1 closing
soon"), the bursaries a programme's fields point to, for the course finder's plan, and what to
remind a student about the funders they saved.

Statuses come from each funder's own dates (applications.window_status). A merit award paid without
an application, or funding students reach through their university, says so instead. Nothing here
asks a learner anything: who can apply is shown in the funder's words, and the learner decides.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from .applications import (
    CHECK,
    CLOSED,
    CLOSING_SOON,
    LATE_AHEAD,
    LATE_OPEN,
    NOT_PUBLISHED,
    OPEN,
    OPENS_LATER,
    STATUS_LABELS,
    Group,
    Guide,
    WindowStatus,
    funder_guide,
)
from .config import load_config
from .schemas import FIELDS, Funder, FundingPack, SourcedList
from .text import in_days, join, long_day, plural

AUTOMATIC = "automatic"
VIA_UNIVERSITY = "via_university"

LABELS = {**STATUS_LABELS, AUTOMATIC: "No application needed", VIA_UNIVERSITY: "Apply through the university"}

#: What each status filter shows.
FILTERS = {
    "open": {OPEN, CLOSING_SOON, LATE_OPEN},
    "closing_soon": {CLOSING_SOON},
    "upcoming": {OPENS_LATER, LATE_AHEAD},
    "check": {CHECK},
    "automatic": {AUTOMATIC},
    "via_university": {VIA_UNIVERSITY},
    "not_published": {NOT_PUBLISHED},
    "closed": {CLOSED},
}
OPEN_NOW = FILTERS["open"]

# Open first (soonest closing first), then dates to check, then not open yet (soonest first), then
# funding with no application dates, then dates not published, then closed.
_ORDER = {
    OPEN: 0, CLOSING_SOON: 0, LATE_OPEN: 0, CHECK: 1, OPENS_LATER: 2, LATE_AHEAD: 2,
    AUTOMATIC: 3, VIA_UNIVERSITY: 3, NOT_PUBLISHED: 4, CLOSED: 5,
}

KIND_LABELS = {"bursary": "Bursary", "merit_award": "Merit award", "loan": "Loan"}
SECTOR_LABELS = {"government": "Government", "university": "University", "company": "Company", "non_profit": "Non-profit"}
STAGE_LABELS = {"first_year": "Starting university", "senior": "Already studying", "postgraduate": "Postgraduate"}


@dataclass
class Card:
    """One funder in the list: who, for what, and where its applications stand today."""

    funder: Funder
    status: str
    lines: list[str]
    window: WindowStatus | None = None  # the intake that matters most today; None when there's no application
    url: str | None = None  # where to apply, from the funder's own page
    source_url: str | None = None
    checked: date | None = None  # the day we read the funder's page
    why: str | None = None  # set when the card answers a search by field

    @property
    def label(self) -> str:
        return LABELS[self.status]

    @property
    def days(self) -> int | None:
        return self.window.days if self.window else None


@dataclass
class Counts:
    total: int
    open_now: int
    closing_soon: int
    line: str


@dataclass
class Matches:
    """The funding a course-finder choice could look at: the best few, and how many there are."""

    fields: list[str]
    cards: list[Card] = field(default_factory=list)
    count: int = 0
    open_now: int = 0
    lines: list[str] = field(default_factory=list)


def _headline(windows: list[WindowStatus]) -> WindowStatus:
    """The intake that matters most today: one open now, then one to check, then the next to open,
    then one closed, then one not published (every plan has at least two intakes)."""
    for wanted in (OPEN_NOW, {CHECK}, FILTERS["upcoming"], {CLOSED}):
        for w in windows:
            if w.status in wanted:
                return w
    return windows[0]


def card(pack: FundingPack, funder: Funder, today: date, cfg: dict | None = None) -> Card:
    """Where one funder's applications stand today, in plain words."""
    cfg = cfg or load_config()
    apps = funder.applications
    source = pack.source(apps.source) if apps.source else None
    out = Card(funder, NOT_PUBLISHED, [], url=apps.url, source_url=source.url if source else None,
               checked=source.retrieved if source else None)
    if funder.applying == AUTOMATIC:
        out.status, out.lines = AUTOMATIC, ["There's no application: it's paid to students who qualify."]
        return out
    windows = funder_guide(pack, funder, today, cfg).windows
    headline = _headline(windows)
    if funder.applying == VIA_UNIVERSITY and headline.status == NOT_PUBLISHED:
        out.status, out.lines = VIA_UNIVERSITY, ["You apply through the university, not to the funder directly."]
        return out
    out.window, out.status, out.lines = headline, headline.status, list(headline.lines)
    later = next((w for w in windows if w.intake > headline.intake), None)
    if headline.status == CLOSED and later:  # and what's known about the next round
        out.lines.append(f"{later.heading}: {later.lines[0]}")
        out.lines += [w.note for w in apps.windows if w.intake == later.intake and w.note and w.note not in later.lines[:1]]
    return out


def _field(tag: str) -> str:
    """A field's label inside a sentence: 'computing and IT'."""
    label = FIELDS[tag]
    return label[0].lower() + label[1:]


def _why(funder: Funder, fields: list[str]) -> str:
    if funder.fields == "any":
        return "Open to any field."
    return f"Funds {join([_field(f) for f in fields if f in funder.fields])}."


def _sort_key(c: Card, fields: list[str] | None):
    general = 1 if fields and c.funder.fields == "any" else 0  # a field's own funders before "any field"
    return (_ORDER[c.status], general, c.days if c.days is not None else 10**6, c.funder.name)


def cards(
    pack: FundingPack,
    today: date,
    cfg: dict | None = None,
    *,
    fields: list[str] | None = None,
    status: str | None = None,
    kind: str | None = None,
    stage: str | None = None,
    university: str | None = None,
) -> list[Card]:
    """Every funder, or those a learner filtered for, open ones first and the soonest to close first.
    A field filter keeps funders of any one of `fields`."""
    cfg = cfg or load_config()
    found = [card(pack, f, today, cfg) for f in pack.funders]
    if fields:
        found = [c for c in found if c.funder.funds(fields)]
        for c in found:
            c.why = _why(c.funder, fields)
    if status:
        found = [c for c in found if c.status in FILTERS[status]]
    if kind:
        found = [c for c in found if c.funder.kind == kind]
    if stage:
        found = [c for c in found if stage in c.funder.stages]
    if university:
        found = [c for c in found if c.funder.usable_at(university)]
    return sorted(found, key=lambda c: _sort_key(c, fields))


def counts(found: list[Card]) -> Counts:
    """'25 funding options: 3 open now, 1 closing soon.'"""
    open_now = sum(c.status in OPEN_NOW for c in found)
    soon = sum(c.status == CLOSING_SOON for c in found)
    line = f"{plural(len(found), 'funding option')}: {open_now} open now" + (f", {soon} closing soon" if soon else "") + "."
    return Counts(len(found), open_now, soon, line)


#: The funding list's groups, in this order, so a long list never scrolls on and on (Rinsuna, 21 Oct 2026).
SECTION_TITLES = {
    "government": "Government",
    "company": "Companies",
    "non_profit": "Non-profits and foundations",
    "university": "Through your university",
}
NSFAS_ID = "nsfas"


@dataclass
class Section:
    """One group of the funding list: who offers it, how many, and how many are open."""

    id: str
    title: str
    cards: list[Card]
    line: str


def _section_line(found: list[Card]) -> str:
    """'9 funders: 2 open now, 1 closing soon.'"""
    c = counts(found)
    line = f"{plural(c.total, 'funder')}: {c.open_now} open now"
    return line + (f", {c.closing_soon} closing soon." if c.closing_soon else ".")


def sections(found: list[Card]) -> list[Section]:
    """The list grouped by who offers the funding, in SECTION_TITLES' order; each keeps the list's order (open ones
    first, the soonest to close first). Empty groups are left out."""
    out = []
    for sector, title in SECTION_TITLES.items():
        mine = [c for c in found if c.funder.sector == sector]
        if mine:
            out.append(Section(sector, title, mine, _section_line(mine)))
    return out


def above_nsfas(pack: FundingPack, funder: Funder) -> bool:
    """Whether the funder's own words place it above NSFAS's household-income limit: it names the missing middle
    (or any household income), or a limit higher than NSFAS's own. Never a guess: a funder that says nothing
    about income isn't counted."""
    if funder.id == NSFAS_ID or funder.income is None:
        return False
    if funder.income.missing_middle:
        return True
    try:
        nsfas = pack.funder(NSFAS_ID).income
    except KeyError:
        return False
    limit = nsfas.limit_cents if nsfas else None
    return limit is not None and funder.income.limit_cents is not None and funder.income.limit_cents > limit


def missing_middle(pack: FundingPack, found: list[Card]) -> Section | None:
    """'If your family earns too much for NSFAS': the funders whose own words say so, in the list's order."""
    mine = [c for c in found if above_nsfas(pack, c.funder)]
    if not mine:
        return None
    return Section("missing_middle", "If your family earns too much for NSFAS", mine, _section_line(mine))


def detail(pack: FundingPack, funder: Funder, today: date, cfg: dict | None = None) -> tuple[Card, Guide]:
    """One funder in full: its card, and how to apply with every intake's dates. A merit award paid
    without an application has no dates, fee or documents to show."""
    cfg = cfg or load_config()
    guide = funder_guide(pack, funder, today, cfg)
    if funder.applying == AUTOMATIC:
        guide.windows = []
        guide.lines = [guide.how] if guide.how else []
    return card(pack, funder, today, cfg), guide


def group(pack: FundingPack, items: SourcedList | None) -> Group | None:
    """A funder's list (what it covers, its obligations) with its source's address."""
    if items is None:
        return None
    source = pack.source(items.source)
    return Group(list(items.items), source.url if source else None)


def field_counts(pack: FundingPack) -> list[tuple[str, str, int]]:
    """(tag, label, how many funders name it) for every field some funder names, by label. Funders
    open to any field aren't counted here."""
    named = [f for funder in pack.funders if funder.fields != "any" for f in funder.fields]
    return sorted(((tag, FIELDS[tag], named.count(tag)) for tag in set(named)), key=lambda t: t[1])


@dataclass
class Reminder:
    """Something to tell a student today about funding they saved."""

    funder_id: str
    template: str  # "open" or "closing"
    intake: int
    key: str  # the same key never alerts the same student twice
    funder: str  # the funder's short name
    when: str | None = None  # for "closing": "in 7 days, on Sat 31 Oct 2026 at 23:59"


def _closing_when(days: int, on: date, at: str | None) -> str:
    """'in 7 days, on Sat 31 Oct 2026 at 23:59', 'tomorrow, Sat 31 Oct 2026', 'today, ...'."""
    joiner = ", on " if days > 1 else ", "
    return f"{in_days(days)}{joiner}{long_day(on)}" + (f" at {at}" if at else "")


def reminders(pack: FundingPack, saved: dict[str, date], today: date, cfg: dict | None = None) -> list[Reminder]:
    """What to tell a student today about the funders they saved (funder id -> the day they saved it):
    that applications close within one of the reminder days (config: 7, then 1), or that they opened
    after the student saved the funder. Each reminder's key makes it alert once."""
    cfg = cfg or load_config()
    thresholds = sorted(cfg["funding"]["remind_days"])
    by_id = {f.id: f for f in pack.funders}
    out: list[Reminder] = []
    for funder_id, saved_on in saved.items():
        funder = by_id.get(funder_id)
        if funder is None or funder.applying != "direct":  # gone from the pack, or nothing to apply for
            continue
        c = card(pack, funder, today, cfg)
        w = c.window
        if w is None or c.status not in OPEN_NOW:
            continue
        within = next((t for t in thresholds if w.days is not None and w.days <= t), None)
        if within is not None and w.next_date is not None:
            window = next((x for x in funder.applications.windows if x.intake == w.intake), None)
            at = window.closing_time if window and w.next_date == window.closes else None
            out.append(Reminder(funder_id, "closing", w.intake, f"{funder_id}:{w.intake}:closing:{within}",
                                funder.short_name, _closing_when(w.days, w.next_date, at)))
        elif w.opens is not None and saved_on < w.opens <= today:
            out.append(Reminder(funder_id, "open", w.intake, f"{funder_id}:{w.intake}:open", funder.short_name))
    return out


def matches(
    pack: FundingPack, fields: list[str], university: str, today: date, cfg: dict | None = None
) -> Matches:
    """The funding a learner starting a programme with these field tags at this university could look
    at: funders of those fields (or any field) for first-years, usable there, the best few first.
    Funders shown with every plan (NSFAS) are left out: the plan already shows them."""
    cfg = cfg or load_config()
    found = [
        c for c in cards(pack, today, cfg, fields=fields, stage="first_year", university=university)
        if not c.funder.every_plan
    ]
    out = Matches(list(fields), found[: cfg["funding"]["per_choice"]], len(found), sum(c.status in OPEN_NOW for c in found))
    subject = join([_field(f) for f in fields if f in FIELDS]) or "this programme"
    besides = join([f.short_name for f in pack.funders if f.every_plan])
    besides = f", besides {besides}" if besides else ""
    if not found:
        out.lines = [f"We haven't found other funding for {subject} yet{besides}. Ask the university's funding office."]
    else:
        open_part = f"{out.open_now} open now" if out.open_now else "none open right now"
        out.lines = [f"{plural(len(found), 'funding option')} for {subject}{besides}: {open_part}."]
    return out
