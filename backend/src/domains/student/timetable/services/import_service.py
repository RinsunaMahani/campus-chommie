"""
Reading a timetable PDF the student chose, so they don't type every class or exam. Nothing is saved here: the
answer is everything the PDF lists, the student picks their own modules and checks each row in the app, and
only what they then send to /me/timetable/batch or /me/exams/batch is kept. The PDF itself is read from memory
and dropped (services/pdf_pages.py); it is never stored or logged.

  read(data, layout)   layout "classes" (a week grid) or "exams" (an exam list)
"""
from __future__ import annotations

from campus_engine import timetable_import as engine
from campus_engine.text import long_day
from campus_engine.timetable import DAYS, hhmm

from . import pdf_pages


def _class(c: engine.FoundClass) -> dict:
    return {"module": c.module, "kind": c.kind, "weekday": c.weekday, "day": DAYS[c.weekday],
            "starts": hhmm(c.starts), "ends": hhmm(c.ends), "venue": c.venue}


def _exam(e: engine.FoundExam) -> dict:
    return {"module": e.module, "title": e.title, "paper": e.paper, "on": e.on.isoformat(), "day": long_day(e.on),
            "starts": hhmm(e.starts), "minutes": e.minutes}


def read(data: bytes, layout: str) -> dict:
    pages, lines = pdf_pages.read(data)
    if layout == "classes":
        found = engine.read_class_grid(pages)
        return {"layout": layout, "modules": found.modules, "classes": [_class(c) for c in found.classes],
                "exams": [], "lines": found.lines}
    found = engine.read_exam_list(lines)
    return {"layout": layout, "modules": found.modules, "classes": [], "exams": [_exam(e) for e in found.exams],
            "lines": found.lines}
