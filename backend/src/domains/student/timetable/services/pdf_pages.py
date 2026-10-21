"""
What a timetable PDF's pages hold, for campus_engine.timetable_import: each piece of text with where it sits,
the page's text line by line, and the drawn lines that border a grid's cells.

The PDF is read from memory and never written anywhere. Only a real, unlocked PDF of at most MAX_PAGES pages is
read (the request itself is capped by MAX_CONTENT_LENGTH); anything pypdf can't read is one plain answer, never
a stack trace.
"""
from __future__ import annotations

import io

from pypdf import PdfReader
from pypdf.generic import ContentStream

from campus_engine.timetable_import import Page, Word
from src.core.exceptions import ValidationError

from ..constants import MAX_PAGES

#: A drawn border: at most this thick, and at least this long (PDF points).
THIN = 2.0
LONG = 20.0


def _refuse(message: str) -> ValidationError:
    return ValidationError("Please check the highlighted fields.", errors=[{"file": [message]}])


def _times(a: list[float], b: list[float]) -> list[float]:
    """The product of two PDF matrices [a b c d e f]."""
    return [
        a[0] * b[0] + a[1] * b[2], a[0] * b[1] + a[1] * b[3],
        a[2] * b[0] + a[3] * b[2], a[2] * b[1] + a[3] * b[3],
        a[4] * b[0] + a[5] * b[2] + b[4], a[4] * b[1] + a[5] * b[3] + b[5],
    ]


def _point(m: list[float], x: float, y: float) -> tuple[float, float]:
    return m[0] * x + m[2] * y + m[4], m[1] * x + m[3] * y + m[5]


def _rules(page, reader) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """The y of every horizontal border and the x of every vertical one, from thin rectangles and lines."""
    across: set[float] = set()
    down: set[float] = set()

    def add(x0: float, y0: float, x1: float, y1: float) -> None:
        if abs(y1 - y0) <= THIN and abs(x1 - x0) >= LONG:
            across.add(round((y0 + y1) / 2 * 2) / 2)
        elif abs(x1 - x0) <= THIN and abs(y1 - y0) >= LONG:
            down.add(round((x0 + x1) / 2 * 2) / 2)

    contents = page.get_contents()
    if contents is None:
        return (), ()
    ctm = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
    stack: list[list[float]] = []
    here = (0.0, 0.0)
    for operands, op in ContentStream(contents, reader).operations:
        if op == b"q":
            stack.append(ctm)
        elif op == b"Q" and stack:
            ctm = stack.pop()
        elif op == b"cm" and len(operands) == 6:
            ctm = _times([float(v) for v in operands], ctm)
        elif op == b"re" and len(operands) == 4:
            x, y, w, h = (float(v) for v in operands)
            x0, y0 = _point(ctm, x, y)
            x1, y1 = _point(ctm, x + w, y + h)
            add(x0, y0, x1, y1)
        elif op == b"m" and len(operands) == 2:
            here = _point(ctm, float(operands[0]), float(operands[1]))
        elif op == b"l" and len(operands) == 2:
            nxt = _point(ctm, float(operands[0]), float(operands[1]))
            add(*here, *nxt)
            here = nxt
    return tuple(sorted(across)), tuple(sorted(down))


def read(data: bytes) -> tuple[list[Page], list[str]]:
    """The pages' words and borders (for a week grid) and every page's text lines (for an exam list)."""
    if not data.startswith(b"%PDF-"):
        raise _refuse("That isn't a PDF. Choose your timetable's PDF file.")
    try:
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted and not reader.decrypt(""):
            raise _refuse("That PDF is locked with a password. Choose one that opens without a password.")
        if len(reader.pages) > MAX_PAGES:
            raise _refuse(f"That PDF has more than {MAX_PAGES} pages. Choose your timetable only.")
        pages: list[Page] = []
        lines: list[str] = []
        for page in reader.pages:
            words: list[Word] = []
            waiting: list[tuple[str, float]] = []

            def visit(text, cm, tm, _font, size, words=words, waiting=waiting):
                # pypdf sometimes hands over text that continues a line before saying where it is (at 0, 0),
                # then says where in its next call: such text waits for that call's position.
                x, y = _point(cm, tm[4], tm[5])
                if (x, y) == (0.0, 0.0):
                    if text.strip():
                        waiting.append((text, float(size or 0)))
                    return
                scale = abs(_times(tm, cm)[0]) or 1.0
                for piece, piece_size in [*waiting, (text, float(size or 0))]:
                    if piece.strip():
                        words.append(Word(round(x, 1), round(y, 1), piece, round(piece_size * scale, 2)))
                waiting.clear()

            lines.extend((page.extract_text(visitor_text=visit) or "").splitlines())
            across, down = _rules(page, reader)
            pages.append(Page(tuple(words), across, down))
    except ValidationError:
        raise
    except Exception:  # pypdf raises many kinds of error on a broken file; the answer is the same
        raise _refuse("We couldn't read that PDF. Try saving it again, or add your classes by hand.") from None
    return pages, lines
