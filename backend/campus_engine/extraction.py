"""Turn a forwarded class announcement into a candidate event for the class rep to confirm.

Rule-based on purpose: predictable, testable and cheap. Every field carries a
confidence, anything uncertain is flagged for the rep, and nothing goes live
without the rep's confirmation.

Reads English, and the Afrikaans words students use for the same things
(toets, eksamen, vasvra, opdrag, verskuif, gekanselleer, the months and the
days). Greetings and asides in any language are simply passed over. "Môre"
is left out on purpose: it means "tomorrow" and "good morning".
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta

from .text import join, long_day, num
from .workload import AcademicEvent

CHECK_BELOW = 0.7

#: How the fields are named to a rep.
FIELD_WORDS = {"kind": "type", "module": "module", "on": "date", "at": "time", "venue": "venue"}

# A kind's word can run straight into its number ("test1"): each ends where letters end, not at a word boundary.
STRONG_KINDS = [
    ("exam", r"\b(?:exam(?:ination)?s?|eksamens?)(?![a-z])"),
    ("test", r"\b(?:tests?|(?:klas|semester)?toetse?)(?![a-z])"),
    ("quiz", r"\b(?:quiz(?:zes)?|vasvrae?)(?![a-z])"),
    ("practical", r"\b(?:practicals?|pracs?|praktika|praks?)(?![a-z])"),
    ("assignment", r"\b(?:assignments?|essays?|projects?|reports?|(?:werk)?opdrag(?:te)?|werkstuk(?:ke)?)(?![a-z])"),
]
WEAK_ASSIGNMENT = re.compile(r"\b(?:due|submit|submission|inhandig|ingehandig)\b", re.I)

_MONTH = (
    r"(jan(?:uary|uarie)?|feb(?:ruary|ruarie)?|mar(?:ch)?|maart|mrt|apr(?:il)?|may|mei|jun(?:e|ie)?|jul(?:y|ie)?|"
    r"aug(?:ust(?:us)?)?|sep(?:t(?:ember)?)?|oct(?:ober)?|okt(?:ober)?|nov(?:ember)?|dec(?:ember)?|des(?:ember)?)\.?"
)
MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    "maa": 3, "mrt": 3, "mei": 5, "okt": 10, "des": 12,  # Afrikaans
}

TITLE = re.compile(
    r"\b(exam|test|quiz|practical|prac|assignment|essay|project|report|eksamen|toets|vasvra|werkopdrag|opdrag|praktika|prak)"
    r"\s*(?:no\.?\s*|nr\.?\s*|number\s*|nommer\s*|#\s*)?(\d{1,2})\b"
    rf"(?!\s*%)(?![/.]\d)(?!\s*(?:st|nd|rd|th)?\s+(?:of\s+)?{_MONTH})",
    re.I,
)
#: A title's word as the app says it.
TITLE_WORDS = {
    "prac": "practical", "prak": "practical", "praktika": "practical", "toets": "test", "eksamen": "exam",
    "vasvra": "quiz", "opdrag": "assignment", "werkopdrag": "assignment",
}
QUALIFIED = re.compile(r"\b(semester|class|mid[- ]?term|final|main|practical)\s+(test|exam)\b", re.I)

CANCELLED = re.compile(
    r"\b(?:cancel(?:l)?ed|called off|won'?t take place|will not take place|no longer taking place|"
    r"(?:ge)?kanselleer|afgelas|sal nie plaasvind nie)\b",
    re.I,
)
MOVED = re.compile(
    r"\b(?:moved|moves? to|postponed|rescheduled|shifted|changed to|has been changed|venue change[ds]?|"
    r"new (?:date|time|venue)|brought forward|now on|verskuif|uitgestel|nuwe datum)\b",
    re.I,
)

PERCENT = re.compile(r"\b(\d{1,3}(?:\.\d+)?)\s?%")
TIME_12 = re.compile(r"\b(1[0-2]|0?[1-9])(?:[:h.]([0-5]\d))?\s*(am|pm)\b", re.I)
TIME_24 = re.compile(r"\b([01]?\d|2[0-3])[:hH]([0-5]\d)\b")

ISO_DATE = re.compile(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b")
DAY_MONTH = re.compile(rf"\b(\d{{1,2}})(?:st|nd|rd|th)?\s+(?:of\s+)?{_MONTH}(?:,?\s+(\d{{4}}))?\b", re.I)
MONTH_DAY = re.compile(rf"\b{_MONTH}\s+(\d{{1,2}})(?:st|nd|rd|th)?(?:,?\s+(\d{{4}}))?\b", re.I)
NUMERIC_DATE = re.compile(r"\b(\d{1,2})[/.](\d{1,2})(?:[/.](\d{4}|\d{2}))?\b")
RELATIVE = re.compile(r"\b(today|tonight|tomorrow|vandag|vanaand)\b", re.I)
WEEKDAY_LONG = re.compile(
    r"\b(next\s+|volgende\s+)?(monday|tuesday|wednesday|thursday|friday|saturday|sunday|"
    r"maandag|dinsdag|woensdag|donderdag|vrydag|saterdag|sondag)\b",
    re.I,
)
WEEKDAY_SHORT = re.compile(r"\b(next\s+)?(Mon|Tues|Tue|Wed|Thurs|Thur|Thu|Fri|Sat|Sun)\b")
WEEKDAYS = {
    "mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6,
    "maa": 0, "din": 1, "woe": 2, "don": 3, "vry": 4, "son": 6,  # Afrikaans (Saterdag is "sat")
}

VENUE_KEYED = re.compile(
    r"\b(lecture hall|room|hall|lab|lt|auditorium|venue)\s*[:#-]?\s*([A-Za-z]{0,2}\s?\d{1,4}[A-Za-z]?)\b", re.I
)
VENUE_GENERIC = re.compile(r"\bvenue\s*[:\-]\s*([^,.;\n]{2,40})", re.I)
MODULE_CODE = re.compile(r"\b([A-Z]{3,4})\s?(\d{3,4})\b")


@dataclass
class Candidate:
    raw: str
    kind: str | None = None
    title: str | None = None
    module: str | None = None
    on: date | None = None
    at: time | None = None
    venue: str | None = None
    weighting: float | None = None
    change: str | None = None  # moved | cancelled
    confidence: dict[str, float] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def needs_check(self) -> list[str]:
        """Fields the rep should look at before confirming."""
        out = []
        required = ["kind", "module"] + ([] if self.change == "cancelled" else ["on"])
        for name in ["kind", "module", "on", "at", "venue"]:
            value = getattr(self, name)
            if value is None:
                if name in required:
                    out.append(name)
            elif self.confidence.get(name, 1.0) < CHECK_BELOW:
                out.append(name)
        return out

    def to_event(self) -> AcademicEvent:
        if self.on is None or self.kind is None:
            raise ValueError("an event needs at least a type and a date")
        return AcademicEvent(
            title=self.title or self.kind.capitalize(),
            kind=self.kind,
            starts=datetime.combine(self.on, self.at or time(0, 0)),
            module=self.module,
            weighting=self.weighting,
            venue=self.venue,
            verified=False,
        )


def _blank(text: str, match: re.Match) -> str:
    """Replace a matched span with spaces so later patterns can't reuse it."""
    start, end = match.span()
    return text[:start] + " " * (end - start) + text[end:]


def _safe_date(year: int, month: int, day: int) -> date | None:
    try:
        return date(year, month, day)
    except ValueError:
        return None


def _infer_year(month: int, day: int, sent: date) -> date | None:
    d = _safe_date(sent.year, month, day)
    if d and d < sent - timedelta(days=30):
        d = _safe_date(sent.year + 1, month, day)
    return d


def _find_kind(text: str) -> tuple[str | None, float]:
    found = []
    for kind, pattern in STRONG_KINDS:
        m = re.search(pattern, text, re.I)
        if m:
            found.append((m.start(), kind))
    if found:
        return min(found)[1], 0.9
    if WEAK_ASSIGNMENT.search(text):
        return "assignment", 0.6
    return None, 0.0


def _find_title(text: str, kind: str | None) -> str | None:
    m = TITLE.search(text)
    if m:
        word = m.group(1).lower()
        word = TITLE_WORDS.get(word, word)
        return f"{word.capitalize()} {int(m.group(2))}"
    m = QUALIFIED.search(text)
    if m:
        return f"{m.group(1).capitalize()} {m.group(2).lower()}"
    return kind.capitalize() if kind else None


def _weekday_date(match: re.Match, sent: date) -> tuple[date, float]:
    target = WEEKDAYS[match.group(2)[:3].lower()]
    delta = (target - sent.weekday()) % 7
    confidence = 0.7
    if delta == 0:
        delta, confidence = 7, 0.5
    if match.group(1):  # "next Thursday" is ambiguous: read as the one in the following week
        if target > sent.weekday():
            delta += 7
        confidence = 0.5
    return sent + timedelta(days=delta), confidence


def extract(text: str, sent: date, modules: list[str] | tuple[str, ...] = ()) -> Candidate:
    """Read one announcement. `sent` is the date the message was sent."""
    c = Candidate(raw=text)
    work = text

    c.kind, kind_conf = _find_kind(work)
    if c.kind:
        c.confidence["kind"] = kind_conf
    c.title = _find_title(work, c.kind)

    if CANCELLED.search(work):
        c.change = "cancelled"
    elif MOVED.search(work):
        c.change = "moved"

    for m in PERCENT.finditer(work):
        value = float(m.group(1))
        if 0 < value <= 100 and c.weighting is None:
            c.weighting = value
    for m in list(PERCENT.finditer(work)):
        work = _blank(work, m)

    m = TIME_12.search(work)
    if m:
        hour = int(m.group(1)) % 12 + (12 if m.group(3).lower() == "pm" else 0)
        c.at, c.confidence["at"] = time(hour, int(m.group(2) or 0)), 0.9
        work = _blank(work, m)
    else:
        m = TIME_24.search(work)
        if m:
            c.at, c.confidence["at"] = time(int(m.group(1)), int(m.group(2))), 0.9
            work = _blank(work, m)

    found: date | None = None
    m = ISO_DATE.search(work)
    if m:
        found = _safe_date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        conf = 0.95
    if found is None:
        m = DAY_MONTH.search(work)
        if m:
            month, dd = MONTHS[m.group(2)[:3].lower()], int(m.group(1))
            found = _safe_date(int(m.group(3)), month, dd) if m.group(3) else _infer_year(month, dd, sent)
            conf = 0.95 if m.group(3) else 0.9
    if found is None:
        m = MONTH_DAY.search(work)
        if m:
            month, dd = MONTHS[m.group(1)[:3].lower()], int(m.group(2))
            found = _safe_date(int(m.group(3)), month, dd) if m.group(3) else _infer_year(month, dd, sent)
            conf = 0.95 if m.group(3) else 0.9
    if found is None:
        m = NUMERIC_DATE.search(work)
        if m:
            dd, month = int(m.group(1)), int(m.group(2))
            year = m.group(3)
            if year:
                found = _safe_date(int(year) + (2000 if len(year) == 2 else 0), month, dd)
            else:
                found = _infer_year(month, dd, sent)
            conf = 0.85
    if found is None:
        m = RELATIVE.search(work)
        if m:
            found = sent + timedelta(days=1 if m.group(1).lower() == "tomorrow" else 0)
            conf = 0.9
    if found is None:
        m = WEEKDAY_LONG.search(work) or WEEKDAY_SHORT.search(work)
        if m:
            found, conf = _weekday_date(m, sent)
    if found is not None:
        c.on, c.confidence["on"] = found, conf
        if found < sent:
            c.confidence["on"] = 0.5
            c.notes.append("This date is before the message was sent.")

    m = VENUE_KEYED.search(work)
    if m:
        keyword = m.group(1).lower()
        label = {"lt": "LT", "venue": "Venue"}.get(keyword, keyword.title())
        c.venue, c.confidence["venue"] = f"{label} {m.group(2).strip().upper()}", 0.85
        work = _blank(work, m)
    else:
        m = VENUE_GENERIC.search(work)
        if m:
            c.venue, c.confidence["venue"] = m.group(1).strip(), 0.7
            work = _blank(work, m)

    for code in modules:
        letters = re.match(r"[A-Za-z]+", code)
        digits = code[letters.end():] if letters else ""
        if letters and re.search(rf"\b{letters.group(0)}\s?{re.escape(digits)}\b", work, re.I):
            c.module, c.confidence["module"] = code.upper(), 0.95
            break
    if c.module is None:
        m = MODULE_CODE.search(work)
        if m:
            c.module, c.confidence["module"] = f"{m.group(1)}{m.group(2)}", 0.6
            if modules:
                c.notes.append("That module code isn't in this class's module list.")
    return c


def find_existing(candidate: Candidate, events: list[AcademicEvent]) -> AcademicEvent | None:
    """The one live event a change message most likely refers to, or None if unclear."""
    live = [e for e in events if not e.cancelled]

    def same_module(e: AcademicEvent) -> bool:
        return candidate.module is None or e.module is None or candidate.module == e.module

    if candidate.title:
        hits = [e for e in live if e.title.lower() == candidate.title.lower() and same_module(e)]
        if len(hits) == 1:
            return hits[0]
    if candidate.kind:
        hits = [e for e in live if e.kind == candidate.kind and same_module(e)]
        if len(hits) == 1:
            return hits[0]
    return None


def apply_change(candidate: Candidate, event: AcademicEvent) -> list[str]:
    """Apply a moved or cancelled message to an existing event. Returns what changed."""
    changes: list[str] = []
    if candidate.change == "cancelled":
        event.cancelled = True
        return [f"{event.title} cancelled"]
    if candidate.on and candidate.on != event.starts.date():
        changes.append(f"date {event.starts.date():%d %b} to {candidate.on:%d %b}")
        event.starts = datetime.combine(candidate.on, event.starts.time())
    if candidate.at and candidate.at != event.starts.time():
        changes.append(f"time {event.starts:%H:%M} to {candidate.at:%H:%M}")
        event.starts = datetime.combine(event.starts.date(), candidate.at)
    if candidate.venue and candidate.venue != event.venue:
        changes.append(f"venue {event.venue or 'not set'} to {candidate.venue}")
        event.venue = candidate.venue
    return changes


def _clock(t: time | None) -> str:
    return f"{t:%H:%M}" if t else "no time set"


def reading(c: Candidate, target_title: str | None = None, target_on: date | None = None) -> list[str]:
    """What we read from an announcement, and what the rep should check, in plain words. For a
    change message, `target_title` and `target_on` name the event it most likely changes."""
    if c.change == "cancelled":
        lines = [
            f"We read this as: {target_title} on {long_day(target_on)} is cancelled."
            if target_title and target_on
            else "We read this as a cancellation, but couldn't tell which event: choose it before confirming."
        ]
    elif c.change == "moved":
        if target_title and target_on:
            new = (f" to {long_day(c.on)}" if c.on else "") + (f" at {c.at:%H:%M}" if c.at else "")
            new += f", {c.venue}" if c.venue else ""
            lines = [f"We read this as: {target_title} on {long_day(target_on)} moves{new or ', but not where to'}."]
        else:
            lines = ["We read this as a change to an event, but couldn't tell which one: choose it before confirming."]
    else:
        what = c.title or (c.kind.capitalize() if c.kind else None)
        if what is None and c.on is None:
            lines = ["We couldn't find a test, assignment or date in this message: fill in the event before confirming."]
        else:
            text = f"We read this as: {what or 'An event'}" + (f" for {c.module}" if c.module else "")
            text += (f" on {long_day(c.on)}" if c.on else "") + (f" at {c.at:%H:%M}" if c.at else "")
            text += (f", {c.venue}" if c.venue else "") + (f", worth {num(c.weighting)}% of the mark" if c.weighting else "")
            lines = [text + "."]
    checks = c.needs_check()
    if checks:
        lines.append(f"Check the {join([FIELD_WORDS[f] for f in checks])} before confirming.")
    return lines + c.notes


def change_line(field: str, old, new) -> str:
    """One recorded change to a verified event, in plain words: `old` and `new` are a date (on),
    a time or None (at), text or None (venue), or True and False (cancelled)."""
    if field == "on":
        return f"Moved from {long_day(old)} to {long_day(new)}."
    if field == "at":
        return f"Time changed from {_clock(old)} to {_clock(new)}."
    if field == "venue":
        return f"Venue changed from {old or 'not set'} to {new or 'not set'}."
    if field == "cancelled":
        return "Cancelled." if new else "Back on: no longer cancelled."
    raise ValueError(f"unknown field {field!r}")
