"""How to apply, on today's date.

For each choice in a plan, and each intake a learner could still aim at: whether applications
are open, closing soon, closed or not published yet, and the late window where a university
publishes one. For each university and national funder (NSFAS): where to apply, the fee, the
documents and what happens next. Then every date still ahead, in order.

Every date comes from a data pack. A date nobody has published is said to be not published,
never guessed, and every status explains itself in plain words with its source.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date

from .bridges import Plan
from .config import load_config
from .schemas import Applications, Funder, FundingPack, SourcedList, University, Window
from .text import day, in_days, long_day, rand

OPEN = "open"
CLOSING_SOON = "closing_soon"
CHECK = "check"
OPENS_LATER = "opens_later"
LATE_OPEN = "late_open"
LATE_AHEAD = "late_ahead"
CLOSED = "closed"
NOT_PUBLISHED = "not_published"

STATUS_LABELS = {
    OPEN: "Open",
    CLOSING_SOON: "Closing soon",
    CHECK: "Check the dates",
    OPENS_LATER: "Not open yet",
    LATE_OPEN: "Late applications open",
    LATE_AHEAD: "Closed, late applications ahead",
    CLOSED: "Closed",
    NOT_PUBLISHED: "Dates not published yet",
}

NOT_VERIFIED = "not verified yet"

UrlFor = Callable[[str], str | None]


@dataclass
class WindowStatus:
    """One intake's applications for one programme, or for one funder, on one day."""

    intake: int
    heading: str
    status: str
    opens: date | None = None
    closes: date | None = None  # this programme's closing date, when published
    closes_one_of: list[date] = field(default_factory=list)  # its possible dates when it isn't
    late_opens: date | None = None
    late_closes: date | None = None
    next_date: date | None = None  # the next date that matters
    days: int | None = None  # from today to next_date
    lines: list[str] = field(default_factory=list)
    source_url: str | None = None

    @property
    def label(self) -> str:
        return STATUS_LABELS[self.status]


@dataclass
class Group:
    items: list[str]
    source_url: str | None


@dataclass
class Line:
    text: str
    source_url: str | None


@dataclass
class Guide:
    """How to apply to one university or one funder."""

    id: str
    name: str
    kind: str  # university | funder
    url: str | None = None
    how: str | None = None
    fee_cents: int | None = None
    fee_note: str | None = None
    contact: str | None = None
    max_choices: int | None = None
    documents: Group | None = None
    after: list[Line] = field(default_factory=list)
    who_can_apply: Group | None = None
    tips: Group | None = None
    warnings: Group | None = None
    windows: list[WindowStatus] = field(default_factory=list)  # funders only: a university's depend on the programme
    lines: list[str] = field(default_factory=list)
    source_url: str | None = None


@dataclass
class Deadline:
    on: date
    days: int
    text: str
    intake: int
    who: str  # a university or funder id
    programme_id: str | None = None  # set when the date is this programme's own
    source_url: str | None = None


@dataclass
class ApplyGuide:
    """'How to apply' for a whole plan."""

    today: date
    windows: dict[tuple[str, str], list[WindowStatus]]  # (university, programme) -> one per intake
    universities: list[Guide]
    funding: list[Guide]
    deadlines: list[Deadline]
    notes: list[str]


def _url_for(pack: University | FundingPack) -> UrlFor:
    def url(source_id: str) -> str | None:
        source = pack.source(source_id)
        return source.url if source else None

    return url


def _either(dates: list[date]) -> str:
    """'Tue 15 Jun, Sat 31 Jul or Thu 30 Sep 2027'."""
    same_year = len({d.year for d in dates}) == 1
    parts = [day(d) if same_year else long_day(d) for d in dates[:-1]] + [long_day(dates[-1])]
    return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " or " + parts[-1]


def _span(first: date, last: date) -> str:
    """'Thu 14 to Fri 22 Jan 2027', 'Wed 1 Apr to Fri 31 Jul 2026' or both dates in full."""
    if (first.year, first.month) == (last.year, last.month):
        return f"{first:%a} {first.day} to {long_day(last)}"
    if first.year == last.year:
        return f"{day(first)} to {long_day(last)}"
    return f"{long_day(first)} to {long_day(last)}"


def _closing(window: Window, programme_id: str | None) -> tuple[date | None, list[date], str, bool]:
    """This programme's closing date (None when not published), the dates it may close on when
    the university hasn't said which applies, the source of the date, and whether the date is the
    programme's own rather than the window's usual one."""
    for group in window.programme_closes:
        if programme_id in group.programmes:
            return group.closes, [], group.source or window.source, True
    if window.closes is not None:
        return window.closes, [], window.source, False
    return None, list(window.closes_one_of), window.source, False


def _last_day(window: Window) -> date | None:
    if window.late:
        return window.late.closes
    closings = [d for d in (window.closes, *window.closes_one_of) if d] + [g.closes for g in window.programme_closes]
    return max(closings) if closings else None


def intakes(today: date, windows: list[Window]) -> list[int]:
    """The intakes a learner could still aim at: next year's and the year after, plus this
    year's while a window for it hasn't finished (a late window in January, say)."""
    years = {today.year + 1, today.year + 2}
    for w in windows:
        last = _last_day(w)
        if w.intake == today.year and last is not None and last >= today:
            years.add(w.intake)
    return sorted(years)


def _previous(prev: Window | None, programme_id: str | None, heading: str, today: date) -> list[str]:
    """Last intake's dates, said as such, for when this intake's aren't published yet. Only once
    last intake's closing date has passed, so the line can say what happened."""
    if prev is None:
        return []
    closes, _, _, own = _closing(prev, programme_id)
    if closes is None or closes >= today:
        return []
    if own:
        return [f"{heading}, applications for this programme closed on {long_day(closes)}."]
    if prev.opens:
        return [f"{heading}, applications ran from {_span(prev.opens, closes)}."]
    return [f"{heading}, applications closed on {long_day(closes)}."]


def window_status(
    window: Window | None,
    intake: int,
    today: date,
    *,
    who: str,
    heading: str,
    url_for: UrlFor,
    programme_id: str | None = None,
    previous: Window | None = None,
    previous_heading: str = "",
    cfg: dict | None = None,
) -> WindowStatus:
    """Where one intake's applications stand today, in plain words. `who` names the university
    or funder; `previous` is the intake before, whose dates are offered as a guide (and said to be
    last time's) when this intake's aren't published."""
    cfg = cfg or load_config()
    out = WindowStatus(intake=intake, heading=heading, status=NOT_PUBLISHED)
    earlier = _previous(previous, programme_id, previous_heading, today)
    if window is None:
        out.lines = [f"{who} hasn't published these dates yet."] + earlier
        return out

    closes, maybe, source, _ = _closing(window, programme_id)
    late = window.late
    out.opens, out.closes, out.closes_one_of = window.opens, closes, maybe
    out.source_url = url_for(source)
    if late:
        out.late_opens, out.late_closes = late.opens, late.closes
    at = f" at {window.closing_time}" if window.closing_time else ""
    last = closes or (maybe[-1] if maybe else None)  # the last day this programme could close
    unsure = (
        f"Programmes close on {_either(maybe)}, and which date applies to this one isn't published yet"
        if maybe
        else ""
    )
    lines: list[str] = []

    def until(d: date) -> str:
        out.next_date, out.days = d, (d - today).days
        return in_days(out.days)

    def late_lines() -> list[str]:
        assert late is not None
        return [f"Late applications: {_span(late.opens, late.closes)} ({until(late.opens)})."] + (
            [late.note] if late.note else []
        )

    if late and today >= late.opens:
        if today <= late.closes:
            out.status = LATE_OPEN
            lines.append(
                f"The closing date has passed, but late applications are open until {long_day(late.closes)} "
                f"({until(late.closes)})."
            )
            lines += [late.note] if late.note else []
        else:
            out.status = CLOSED
            lines.append(f"Closed. Late applications closed on {long_day(late.closes)}.")
    elif window.opens is not None and today < window.opens:
        out.status = OPENS_LATER
        lines.append(f"Opens on {long_day(window.opens)} ({until(window.opens)}).")
        if closes is not None:
            lines.append(f"Closes on {long_day(closes)}{at}.")
        elif maybe:
            lines.append(f"{unsure}: apply by {long_day(maybe[0])} to be safe.")
            lines += earlier
        else:
            lines.append("The closing date isn't published yet.")
            lines += earlier
    elif last is None:
        if window.opens is not None:
            out.status = OPEN
            lines.append("Open now. The closing date isn't published yet, so apply early.")
        else:
            lines.append(f"{who} hasn't published these dates yet.")
            if late:
                lines += late_lines()
        lines += earlier
    elif today <= last:
        upcoming = [d for d in maybe if d >= today]
        passed = [d for d in maybe if d < today]
        nxt = closes if closes is not None else upcoming[0]
        when = until(nxt)
        if passed:
            out.status = CHECK
            lines.append(
                f"This programme may already have closed on {_either(passed)}. If it hasn't, it closes on "
                f"{_either(upcoming)}: check with {who}."
            )
            lines += earlier
        elif window.opens is None:
            out.status = CHECK
            closing = f"{long_day(closes)}{at}" if closes is not None else _either(maybe)
            lines.append(f"Closes on {closing} ({when}). We haven't verified when applications open, so check that they're open.")
        else:
            soon = out.days is not None and out.days <= cfg["applications"]["closing_soon_days"]
            out.status = CLOSING_SOON if soon else OPEN
            if closes is not None:
                lines.append(f"Open now. Closes on {long_day(closes)}{at} ({when}).")
            else:
                lines.append(f"Open now. {unsure}: apply by {long_day(nxt)} to be safe ({when}).")
                lines += earlier
    else:
        if closes is not None:
            lines.append(f"Closed on {long_day(closes)}.")
        else:
            lines.append(f"Closed: the last of its possible closing dates was {long_day(last)}.")
        if late and today < late.opens:
            out.status = LATE_AHEAD
            lines += late_lines()
        else:
            out.status = CLOSED

    if window.no_late_applications:
        lines.append("No late applications.")
    if window.note:
        lines.append(window.note)
    out.lines = lines
    return out


def programme_windows(uni: University, programme_id: str, today: date, cfg: dict | None = None) -> list[WindowStatus]:
    """One status per intake for one programme."""
    windows = uni.applications.windows if uni.applications else []
    by_intake = {w.intake: w for w in windows}
    return [
        window_status(
            by_intake.get(year), year, today,
            who=uni.name, heading=f"To start in {year}", url_for=_url_for(uni), programme_id=programme_id,
            previous=by_intake.get(year - 1), previous_heading=f"To start in {year - 1}", cfg=cfg,
        )
        for year in intakes(today, windows)
    ]


def _group(items: SourcedList | None, url_for: UrlFor) -> Group | None:
    return Group(list(items.items), url_for(items.source)) if items else None


def _guide(key: str, name: str, kind: str, apps: Applications | None, url_for: UrlFor) -> Guide:
    guide = Guide(id=key, name=name, kind=kind)
    lines: list[str] = []
    if apps is not None:
        guide.url, guide.how, guide.contact = apps.url, apps.how, apps.contact
        guide.fee_cents, guide.fee_note = apps.fee_cents, apps.fee_note
        guide.source_url = url_for(apps.source) if apps.source else None
        guide.documents = _group(apps.documents, url_for)
        guide.after = [Line(a.text, url_for(a.source)) for a in apps.after]
    lines.append(f"Where to apply: {guide.url}" if guide.url else f"Where to apply: {NOT_VERIFIED}.")
    if guide.how:
        lines.append(guide.how)
    if guide.fee_cents is None:
        lines.append(f"Application fee: {NOT_VERIFIED}.")
    elif guide.fee_cents == 0:
        lines.append("Applying is free.")
    else:
        lines.append(f"Application fee: {rand(guide.fee_cents)}.")
    if guide.fee_note:
        lines.append(guide.fee_note)
    if guide.documents is None:
        lines.append(f"Documents: {NOT_VERIFIED}.")
    guide.lines = lines
    return guide


def university_guide(uni: University) -> Guide:
    """Where and how to apply to one university, what it costs and what to send."""
    guide = _guide(uni.university, uni.name, "university", uni.applications, _url_for(uni))
    guide.max_choices = uni.max_choices
    if uni.max_choices is None:
        guide.lines.append(f"How many programmes you can list on one application: {NOT_VERIFIED}.")
    else:
        guide.lines.append(f"You can list {uni.max_choices} programmes on one application.")
    if guide.contact:
        guide.lines.append(f"Questions: {guide.contact}")
    return guide


def funder_guide(pack: FundingPack, funder: Funder, today: date, cfg: dict | None = None) -> Guide:
    """How to apply to one funder, with its windows on today's date."""
    url_for = _url_for(pack)
    guide = _guide(funder.id, funder.name, "funder", funder.applications, url_for)
    guide.who_can_apply = _group(funder.who_can_apply, url_for)
    guide.tips = _group(funder.tips, url_for)
    guide.warnings = _group(funder.warnings, url_for)
    windows = funder.applications.windows
    by_intake = {w.intake: w for w in windows}
    guide.windows = [
        window_status(
            by_intake.get(year), year, today,
            who=funder.short_name, heading=f"Funding for {year}", url_for=url_for,
            previous=by_intake.get(year - 1), previous_heading=f"For {year - 1} funding", cfg=cfg,
        )
        for year in intakes(today, windows)
    ]
    if guide.contact:
        guide.lines.append(f"Questions: {guide.contact}")
    return guide


def _window_deadlines(
    who: str, name: str, window: Window, today: date, url_for: UrlFor, *,
    what: str, programme: tuple[str, str] | None = None,
) -> list[Deadline]:
    """Every date in one window that is still ahead."""
    out: list[Deadline] = []

    def add(on: date, text: str, source: str, programme_id: str | None = None) -> None:
        if on >= today:
            out.append(Deadline(on, (on - today).days, text, window.intake, who, programme_id, url_for(source)))

    if window.opens:
        add(window.opens, f"{name}: {what} open.", window.source)
    pid, pname = programme or (None, None)
    closes, maybe, source, own = _closing(window, pid)
    at = f" at {window.closing_time}" if window.closing_time else ""
    if closes is not None:
        add(closes, f"{name}, {pname}: {what} close{at}." if own else f"{name}: {what} close{at}.", source, pid if own else None)
    else:
        upcoming = [d for d in maybe if d >= today]
        if upcoming and pname:
            add(upcoming[0], f"{name}, {pname}: {what} may close on this date, so apply by then to be safe.", source, pid)
    if window.late:
        late = window.late
        add(late.opens, f"{name}: late {what} open.", late.source)
        add(late.closes, f"{name}: late {what} close.", late.source)
    return out


def apply_guide(
    catalogue: dict[str, University],
    funding: FundingPack | None,
    plan: Plan,
    today: date,
    cfg: dict | None = None,
) -> ApplyGuide:
    """'How to apply' for every choice in a plan, the universities and funders involved, and every
    date still ahead, soonest first."""
    slots = [s for s in (plan.goal, plan.bridge, plan.safe, *plan.other_routes) if s is not None]
    choices = list(dict.fromkeys((s.match.university, s.match.programme_id, s.match.programme_name) for s in slots))

    windows = {(u, pid): programme_windows(catalogue[u], pid, today, cfg) for u, pid, _ in choices}
    universities = [university_guide(catalogue[u]) for u in dict.fromkeys(u for u, _, _ in choices)]
    funders = [funder_guide(funding, f, today, cfg) for f in funding.funders] if funding else []

    deadlines: list[Deadline] = []
    for u, pid, pname in choices:
        uni = catalogue[u]
        uni_windows = uni.applications.windows if uni.applications else []
        years = intakes(today, uni_windows)
        for w in uni_windows:
            if w.intake in years:
                deadlines += _window_deadlines(
                    u, uni.name, w, today, _url_for(uni), what=f"applications to start in {w.intake}", programme=(pid, pname)
                )
    if funding:
        for f in funding.funders:
            years = intakes(today, f.applications.windows)
            for w in f.applications.windows:
                if w.intake in years:
                    deadlines += _window_deadlines(
                        f.id, f.short_name, w, today, _url_for(funding), what=f"applications for {w.intake} funding"
                    )
    unique = {(d.on, d.text): d for d in deadlines}
    deadlines = sorted(unique.values(), key=lambda d: (d.on, d.text))

    notes = [
        "Apply on each university's own website, and pay a fee only as its page explains. "
        "Campus Chommie can't apply for you."
    ]
    if funders:
        notes.append(
            "Funding is a separate application: if you might qualify for "
            + " or ".join(f.short_name for f in funding.funders)
            + ", apply there as well."
        )
    return ApplyGuide(today, windows, universities, funders, deadlines, notes)
