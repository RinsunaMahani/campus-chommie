"""Reading a university's timetable from what a PDF's pages hold, so a student doesn't type every class.

Two layouts, each read from plain data (no PDF library here; the web side extracts words and lines):

  read_class_grid(pages)   a week grid: weekdays across the top, periods ("07:45 - 08:25") down the side,
                           and in each cell the classes in it ("MCHM000 - CP4L001", "(PRAC)", "TUT").
                           A class listed in several periods in a row becomes one class from the first
                           start to the last end.
  read_exam_list(lines)    an exam schedule with one paper per line: date, session, start ("09H00"),
                           minutes, module code, its name, and the paper ("PAPER ONE").

Both only read back what the document says. Nothing is decided about the student: they pick their own
modules and check every class before anything is saved, because reading a layout can go wrong.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, time

from .config import load_config
from .text import join, long_day, plural, span

#: A module code as universities print them: MCHM000, ANA201, COS 132, MPHB022.
CODE = re.compile(r"\b([A-Z]{3,5}) ?(\d{3,4}[A-Z]?)\b")
#: Dashes and spaces around a venue ("MCHM000 – CP4L001"); some PDFs turn the dash into U+FFFD.
_EDGES = re.compile(r"^[\s\-\u2013\u2014\ufffd]+|[\s\-\u2013\u2014\ufffd]+$")
_TIME = re.compile(r"\b(\d{1,2})[:hH.](\d{2})\b")
_WEEKDAYS = {"MONDAY": 0, "TUESDAY": 1, "WEDNESDAY": 2, "THURSDAY": 3, "FRIDAY": 4, "SATURDAY": 5, "SUNDAY": 6}
_MONTHS = {m: i for i, m in enumerate(("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"), 1)}
#: Estimating a piece's width from its font size, per character as in Helvetica/Arial (bold): capitals about
#: 0.7 of it, digits 0.56, small letters 0.5, a space 0.28, punctuation 0.33. Pieces closer than GAP_EM of the font
#: size are touching (a space is about 0.28).
GAP_EM = 0.08


def _em(ch: str) -> float:
    if ch.isupper():
        return 0.7
    if ch.isdigit():
        return 0.556
    if ch.islower():
        return 0.5
    return 0.28 if ch.isspace() else 0.33
_PRACTICAL = re.compile(r"\(?\bPRAC(TICAL)?S?\b\)?", re.I)
_TUTORIAL = re.compile(r"\(?\bTUT(ORIAL)?S?\b\)?", re.I)


@dataclass(frozen=True)
class Word:
    """A piece of text where the page puts it. PDF coordinates: x grows to the right, y grows upwards."""

    x: float
    y: float
    text: str
    #: The font size it's drawn at, to tell touching pieces ("CP" "2" "L001") from separate words; 0 if unknown.
    size: float = 0.0


@dataclass(frozen=True)
class Page:
    words: tuple[Word, ...]
    #: The y of each drawn horizontal line and the x of each vertical one: the grid's cell borders, if drawn.
    across: tuple[float, ...] = ()
    down: tuple[float, ...] = ()


@dataclass(frozen=True)
class FoundClass:
    module: str
    kind: str  # lecture, tutorial or practical
    weekday: int  # 0 = Monday
    starts: time
    ends: time
    venue: str | None


@dataclass(frozen=True)
class FoundExam:
    module: str
    title: str | None
    paper: str | None
    on: date
    starts: time
    minutes: int | None


@dataclass
class Reading:
    classes: list[FoundClass] = field(default_factory=list)
    exams: list[FoundExam] = field(default_factory=list)
    modules: list[str] = field(default_factory=list)
    lines: list[str] = field(default_factory=list)


def module_code(text: str) -> str:
    """'cos 132' and 'COS132' are the same module: upper case, no space."""
    return re.sub(r"\s+", "", text.upper())


def _minutes(t: time) -> int:
    return t.hour * 60 + t.minute


def _clock(h: str, m: str) -> time | None:
    hour, minute = int(h), int(m)
    return time(hour, minute) if hour < 24 and minute < 60 else None


# --- the week grid ----------------------------------------------------------------------------------------


def _group(words: list[Word], tol: float) -> list[list[Word]]:
    """Words at the same height (within tol), top line first."""
    rows: list[list[Word]] = []
    for w in sorted(words, key=lambda w: -w.y):
        if rows and abs(rows[-1][0].y - w.y) <= tol:
            rows[-1].append(w)
        else:
            rows.append([w])
    return rows


def _joined(words: list[Word]) -> str:
    """One line's pieces left to right. Pieces that touch are one word: a PDF often draws "CP2L001" as "CP",
    "2", "L001". A piece's width isn't known, so it's estimated from its font size (_em per character)."""
    out = ""
    end = None
    for w in sorted(words, key=lambda w: w.x):
        touching = end is not None and w.size > 0 and w.x - end < GAP_EM * w.size and not w.text[:1].isspace()
        out += w.text if touching or not out or out.endswith(" ") else " " + w.text
        end = w.x + sum(_em(c) for c in w.text) * w.size if w.size > 0 else None
    return " ".join(out.split())


def _lines_of(words: list[Word], tol: float) -> list[str]:
    """Each line's words read left to right, top line first."""
    return [_joined(r) for r in _group(words, tol)]


def _entries(lines: list[str]) -> list[str]:
    """A line that starts with a module code starts a class; any other line continues the class above it
    ("PH E-" / "CLASS"). Codes later in a line are venues ("MCOB000 - BMS301")."""
    out: list[str] = []
    for line in lines:
        if CODE.match(line):
            out.append(line)
        elif out and line.upper() != "LUNCH":
            out[-1] = out[-1] + line if out[-1].endswith("-") else f"{out[-1]} {line}"
    return out


def _entry(text: str) -> tuple[str, str, str | None]:
    """'MPHB000 - NSB 007- (PRAC)' -> ('MPHB000', 'practical', 'NSB 007')."""
    m = CODE.search(text)
    code = module_code(m.group(0))
    rest = text[m.end():]
    kind = "practical" if _PRACTICAL.search(rest) else "tutorial" if _TUTORIAL.search(rest) else "lecture"
    rest = _TUTORIAL.sub(" ", _PRACTICAL.sub(" ", rest))
    rest = re.sub(r"\(\s*\)", " ", rest)
    venue = " ".join(_EDGES.sub("", " ".join(rest.split())).split())
    return code, kind, (venue[:80] or None)


def _bands(marks: list[float], rules: list[float]) -> list[tuple[float, float]]:
    """Each row label's band (top label first): from the drawn line below it to the drawn line above it,
    or halfway to the next label where no line is drawn."""
    out = []
    for i, y in enumerate(marks):
        above = [r for r in rules if r > y]
        below = [r for r in rules if r < y]
        top = min(above) if above else ((marks[i - 1] + y) / 2 if i else float("inf"))
        bottom = max(below) if below else ((marks[i + 1] + y) / 2 if i + 1 < len(marks) else float("-inf"))
        out.append((bottom, top))
    return out


def _grid(page: Page, cfg: dict) -> list[tuple[int, time, time, str, str, str | None]]:
    tol = cfg["line_tolerance"]
    heads = [(w, _WEEKDAYS[w.text.strip().upper()]) for w in page.words if w.text.strip().upper() in _WEEKDAYS]
    if len(heads) < 2:
        return []
    head_y = sorted(w.y for w, _ in heads)[len(heads) // 2]
    heads = sorted(((w, d) for w, d in heads if abs(w.y - head_y) <= tol), key=lambda h: h[0].x)
    first_x = heads[0][0].x

    # Columns: between the vertical lines around each weekday heading, or halfway between headings.
    cols: list[tuple[float, float, int]] = []
    for i, (w, d) in enumerate(heads):
        left = [r for r in page.down if r <= w.x]
        right = [r for r in page.down if r > w.x]
        lo = max(left) if left else ((heads[i - 1][0].x + w.x) / 2 if i else float("-inf"))
        hi = min(right) if right else ((heads[i + 1][0].x + w.x) / 2 if i + 1 < len(heads) else float("inf"))
        cols.append((lo, hi, d))
    if cols[0][0] == float("-inf"):
        # No line drawn left of the first day: the grid starts halfway between the times and that heading.
        times_x = [w.x for w in page.words if w.x < first_x and w.y < head_y - tol and _TIME.search(w.text)]
        cols[0] = ((max(times_x) + first_x) / 2 if times_x else first_x, cols[0][1], cols[0][2])
    grid_left = cols[0][0]

    # Periods: the times written left of the grid, one pair per row.
    side = [w for w in page.words if w.x < grid_left and w.y < head_y - tol]
    periods: list[tuple[float, time, time]] = []
    for line_words in _group(side, tol):
        times = [_clock(*m.groups()) for m in _TIME.finditer(" ".join(w.text for w in sorted(line_words, key=lambda w: w.x)))]
        times = [t for t in times if t]
        if len(times) >= 2 and times[1] > times[0]:
            periods.append((sum(w.y for w in line_words) / len(line_words), times[0], times[1]))
    if not periods:
        return []
    periods.sort(key=lambda p: -p[0])
    rules = [r for r in page.across if r < head_y]
    ys = [p[0] for p in periods]
    bands = _bands(ys, rules)

    found = []
    for (_, starts, ends), (lo, hi) in zip(periods, bands):
        for c_lo, c_hi, weekday in cols:
            cell = [w for w in page.words if c_lo <= w.x < c_hi and lo < w.y < hi and w.y < head_y - tol]
            for text in _entries(_lines_of(cell, tol)):
                code, kind, venue = _entry(text)
                found.append((weekday, starts, ends, code, kind, venue))
    return found


def _merge(found: list[tuple[int, time, time, str, str, str | None]], gap: int) -> list[FoundClass]:
    """The same module and kind in back-to-back periods on one day is one class, in the first period's venue
    (a venue spelt two ways, "CP2L001" and "CP2LOO1", is still one class)."""
    same = lambda f: (f[0], f[3], f[4])  # noqa: E731
    out: list[FoundClass] = []
    last_key = None
    for f in sorted(set(found), key=lambda f: (same(f), f[1])):
        weekday, starts, ends, code, kind, venue = f
        prev = out[-1] if out else None
        if prev and same(f) == last_key and _minutes(starts) - _minutes(prev.ends) <= gap:
            out[-1] = FoundClass(code, kind, weekday, prev.starts, max(ends, prev.ends), prev.venue)
        else:
            out.append(FoundClass(code, kind, weekday, starts, ends, venue))
        last_key = same(f)
    return sorted(out, key=lambda c: (c.weekday, c.starts, c.module))


def read_class_grid(pages: list[Page], cfg: dict | None = None) -> Reading:
    """Every class in a week grid, merged across back-to-back periods, with the module codes it names."""
    cfg = (cfg or load_config())["timetable_import"]
    found = [f for page in pages for f in _grid(page, cfg)]
    classes = _merge(found, cfg["merge_gap_minutes"])[: cfg["max_rows"]]
    modules = sorted({c.module for c in classes})
    if not classes:
        return Reading(lines=["We couldn't find a week grid in this PDF: weekdays across the top and class "
                              "times down the side. You can still add your classes by hand."])
    days = sorted({c.weekday for c in classes})
    names = [d.title() for d, n in sorted(_WEEKDAYS.items(), key=lambda kv: kv[1]) if n in days]
    return Reading(classes=classes, modules=modules, lines=[
        f"Found {plural(len(classes), 'class')} for {plural(len(modules), 'module')}, on {join(names)}.",
        "Pick your modules, then check each class before you save: reading a timetable from a PDF can go wrong.",
    ])


# --- the exam schedule ------------------------------------------------------------------------------------

_EXAM = re.compile(
    r"(?P<d>\d{1,2})[-/ ](?P<mon>[A-Za-z]{3})[-/ ](?P<y>\d{4})\s+(?:\d\s+)?"
    r"(?P<h>\d{1,2})[Hh:.](?P<m>\d{2})\s+(?:(?P<min>\d{2,3})\s+)?"
    r"(?P<code>[A-Z]{3,5} ?\d{3,4}[A-Z]?)\s+(?P<rest>.*)$"
)
#: After the module's name: offering type, number of students, exam type and paper number, then the paper.
_TAIL = re.compile(r"^(?P<title>.*?)\s+[A-Z][A-Z0-9]\s+\d+\s*[A-Z]\s+\d+(?:\s+(?P<paper>.+))?$")


def read_exam_list(lines: list[str], cfg: dict | None = None) -> Reading:
    """Every paper in an exam schedule with one paper per line. Student numbers on the list are not kept."""
    cfg = (cfg or load_config())["timetable_import"]
    seen: dict[tuple, FoundExam] = {}
    for raw in lines:
        m = _EXAM.search(raw)
        if not m or m.group("mon").upper() not in _MONTHS:
            continue
        try:
            on = date(int(m.group("y")), _MONTHS[m.group("mon").upper()], int(m.group("d")))
        except ValueError:
            continue
        starts = _clock(m.group("h"), m.group("m"))
        if starts is None:
            continue
        minutes = int(m.group("min")) if m.group("min") else None
        if minutes is not None and not (0 < minutes <= cfg["max_exam_minutes"]):
            minutes = None
        rest = " ".join(m.group("rest").split())
        tail = _TAIL.match(rest)
        title = (tail.group("title") if tail else rest).strip() or None
        paper = (tail.group("paper") or "").strip() or None if tail else None
        exam = FoundExam(module_code(m.group("code")), title and title[:80], paper and paper[:80], on, starts, minutes)
        seen.setdefault((exam.module, exam.on, exam.starts, exam.paper), exam)
    exams = sorted(seen.values(), key=lambda e: (e.on, e.starts, e.module))[: cfg["max_rows"]]
    if not exams:
        return Reading(lines=["We couldn't find an exam list in this PDF: a date, a start time and a module "
                              "code on each line. You can still add your exams by hand."])
    modules = sorted({e.module for e in exams})
    when = span(exams[0].on, exams[-1].on) if exams[0].on != exams[-1].on else long_day(exams[0].on)
    return Reading(exams=exams, modules=modules, lines=[
        f"Found {plural(len(exams), 'exam paper')} for {plural(len(modules), 'module')}, {when}.",
        "Type or pick your module codes to see your own exams, then check them before you save.",
    ])
