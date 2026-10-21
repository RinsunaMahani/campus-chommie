"""Tiny, real PDFs for the timetable import's tests: text at given places and thin rectangles as cell borders,
one page each, in Helvetica. Made up here; no real timetable is used."""
from __future__ import annotations


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def make_pdf(pages: list[dict]) -> bytes:
    """pages: [{"texts": [(x, y, size, text)], "rects": [(x, y, w, h)]}] on A4 landscape."""
    objects: list[bytes] = []

    def add(body: bytes) -> int:
        objects.append(body)
        return len(objects)

    font = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    kids = []
    pages_id = len(objects) + 1 + 2 * len(pages)  # the Pages object comes after every page and its content
    for page in pages:
        ops = [f"{x} {y} {w} {h} re f" for x, y, w, h in page.get("rects", [])]
        for x, y, size, text in page.get("texts", []):
            ops.append(f"BT /F1 {size} Tf 1 0 0 1 {x} {y} Tm ({_escape(text)}) Tj ET")
        stream = "\n".join(ops).encode("cp1252")
        content = add(b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream")
        kids.append(add(b"<< /Type /Page /Parent %d 0 R /MediaBox [0 0 842 595] /Contents %d 0 R "
                        b"/Resources << /Font << /F1 %d 0 R >> >> >>" % (pages_id, content, font)))
    assert add(b"<< /Type /Pages /Kids [%s] /Count %d >>" % (b" ".join(b"%d 0 R" % k for k in kids), len(kids))) == pages_id
    catalog = add(b"<< /Type /Catalog /Pages %d 0 R >>" % pages_id)

    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(objects, 1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % number + body + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    out += b"".join(b"%010d 00000 n \n" % o for o in offsets)
    out += b"trailer\n<< /Size %d /Root %d 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objects) + 1, catalog, xref)
    return bytes(out)


def week_grid_pdf() -> bytes:
    """Monday and Tuesday, two periods, borders drawn: ABC101 on Monday for both periods, DEF202's practical
    on Tuesday's first period."""
    texts = [
        (150, 455, 9, "MONDAY"), (270, 455, 9, "TUESDAY"),
        (50, 430, 9, "08:00 - 08:50"), (50, 400, 9, "09:00 - 09:50"),
        (120, 432, 8, "ABC101 - HALL 1"), (120, 402, 8, "ABC101 - HALL 1"),
        (240, 432, 8, "DEF202 - LAB 3 (PRAC)"),
    ]
    rects = [(40, y, 330, 0.5) for y in (385, 415, 445)] + [(x, 385, 0.5, 80) for x in (40, 115, 235, 370)]
    return make_pdf([{"texts": texts, "rects": rects}])


def exam_list_pdf() -> bytes:
    rows = [
        "31 26-OCT-2026 1 09H00 180 ABC101 INTRODUCTION TO EXAMPLES S1 42 N 1 PAPER ONE",
        "31 02-NOV-2026 2 14H00 120 DEF202 MADE-UP STUDIES II S0 5 N 1 PAPER 1",
        "31 03-NOV-2026 1 09H00 120 XYZ999 SOMEONE ELSE'S MODULE S0 9 N 1 PAPER 1",
    ]
    return make_pdf([{"texts": [(30, 500 - 20 * i, 9, row) for i, row in enumerate(rows)]}])
