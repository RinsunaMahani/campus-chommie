"""
Reading a timetable from a PDF's pages: a week grid (weekdays across, periods down, classes in the cells) and an
exam list (one paper per line). Every page and line here is made up in the shapes universities print; no real
timetable is used.
"""
from __future__ import annotations

from datetime import date, time

from campus_engine.timetable import Exam, exam_summary
from campus_engine.timetable_import import Page, Word, module_code, read_class_grid, read_exam_list

#: Columns' left edges and periods' label heights (PDF y grows upwards).
MON, TUE = 120.0, 240.0
P1, P2, P3 = 430.0, 400.0, 370.0


def grid(cells: list[Word], *, lines: bool = True) -> Page:
    words = [
        Word(60, 455, "PERIOD"), Word(150, 455, "MONDAY"), Word(270, 455, "TUESDAY"),
        Word(50, P1, "08:00"), Word(75, P1, "–"), Word(82, P1, "08:50"),
        Word(50, P2, "09:00"), Word(75, P2, "–"), Word(82, P2, "09:50"),
        Word(50, P3, "10:00 - 10:50"),
        *cells,
    ]
    if not lines:
        return Page(tuple(words))
    return Page(tuple(words), across=(355.0, 385.0, 415.0, 445.0, 465.0), down=(40.0, 115.0, 235.0, 360.0))


def test_a_class_in_back_to_back_periods_is_one_class_and_its_kind_and_venue_are_read():
    page = grid([
        Word(MON, P1 + 5, "ABCD000 – HALL 1"), Word(MON, P2 + 5, "ABCD000 – HALL 1"),
        Word(TUE, P1 + 5, "EFG101 - NSB LAB 008 (PRAC)"), Word(TUE, P2 + 5, "EFG101 - NSB LAB 008 (PRAC)"),
        Word(TUE, P3 + 5, "EFG101 - ROOM 2 TUT"),
    ])
    reading = read_class_grid([page])
    got = [(c.weekday, c.starts, c.ends, c.module, c.kind, c.venue) for c in reading.classes]
    assert got == [
        (0, time(8, 0), time(9, 50), "ABCD000", "lecture", "HALL 1"),
        (1, time(8, 0), time(9, 50), "EFG101", "practical", "NSB LAB 008"),
        (1, time(10, 0), time(10, 50), "EFG101", "tutorial", "ROOM 2"),
    ]
    assert reading.modules == ["ABCD000", "EFG101"]
    assert reading.lines[0] == "Found 3 classes for 2 modules, on Monday and Tuesday."


def test_a_code_later_in_a_line_is_a_venue_and_a_line_without_a_code_continues_the_class():
    page = grid([
        Word(MON, P1 + 8, "MCOB000 – BMS301"),
        Word(MON, P1 + 2, "MAPA000 – PH E-"), Word(MON, P1 - 4, "CLASS"),
        Word(TUE, P1 + 5, "LUNCH"),
    ])
    got = {(c.module, c.venue) for c in read_class_grid([page]).classes}
    assert got == {("MCOB000", "BMS301"), ("MAPA000", "PH E-CLASS")}


def test_touching_pieces_are_one_word_and_a_spaced_piece_is_not():
    # "CP" "2" "L001" drawn edge to edge at 8 pt, as a highlighted venue often is.
    page = grid([
        Word(MON, P1 + 5, "MPHS000 –", 8.0), Word(MON + 40, P1 + 5, "CP", 8.0),
        Word(MON + 40 + 2 * 0.55 * 8, P1 + 5, "2", 8.0), Word(MON + 40 + 3 * 0.55 * 8, P1 + 5, "L001", 8.0),
        Word(TUE, P1 + 5, "MPHB000 – PH", 8.0), Word(TUE + 65, P1 + 5, "LAB", 8.0),
    ])
    venues = {c.module: c.venue for c in read_class_grid([page]).classes}
    assert venues == {"MPHS000": "CP2L001", "MPHB000": "PH LAB"}


def test_a_venue_spelt_two_ways_is_still_one_class():
    page = grid([Word(MON, P1 + 5, "XYZ200 - CP2L001"), Word(MON, P2 + 5, "XYZ200 - CP2LOO1")])
    [only] = read_class_grid([page]).classes
    assert (only.starts, only.ends, only.venue) == (time(8, 0), time(9, 50), "CP2L001")


def test_without_drawn_lines_rows_and_columns_fall_halfway_between_their_labels():
    page = grid([Word(MON, P1 + 5, "ABCD000 - HALL 1"), Word(TUE, P3 - 5, "EFG101 - ROOM 2")], lines=False)
    got = [(c.weekday, c.starts, c.module) for c in read_class_grid([page]).classes]
    assert got == [(0, time(8, 0), "ABCD000"), (1, time(10, 0), "EFG101")]


def test_a_page_without_a_week_grid_says_so_and_finds_nothing():
    reading = read_class_grid([Page((Word(50, 500, "Exam schedule"), Word(50, 480, "MONDAY")))])
    assert reading.classes == [] and reading.modules == []
    assert reading.lines[0].startswith("We couldn't find a week grid in this PDF")


EXAM_LINES = [
    "Campus Exam Exam Start Dur Subject Subject Offering Students Exam Paper Examination",
    "    31 26-OCT-2026    1 09H00 180  ABC101  INTRODUCTION TO EXAMPLES      S1              42 N          1 PAPER ONE (THEORY)",
    "    31 26-OCT-2026    1 09H00 180  ABC101  INTRODUCTION TO EXAMPLES      S1              42 N          1 PAPER ONE (THEORY)",
    "    31 02-NOV-2026    2 14H00      DEF202  MADE-UP STUDIES II            S0               5N         1 PAPER 1",
    "    31 05-NOV-2026    2 14H00  60  GHI303  PRETEND PATHOLOGY             S0               2 N         1",
    "    31 06-NOV-2026    1 09H00 999  JKL404  TOO LONG TO BE TRUE           S0               2 N         1 PAPER 2",
    "    31 31-FOO-2026    1 09H00 120  MNO505  NOT A MONTH                   S0               2 N         1 PAPER 1",
    "    31 31-NOV-2026    1 09H00 120  PQR606  NOT A DAY                     S0               2 N         1 PAPER 1",
]


def test_an_exam_list_gives_each_paper_once_without_the_student_numbers():
    reading = read_exam_list(EXAM_LINES)
    got = [(e.module, e.title, e.paper, e.on, e.starts, e.minutes) for e in reading.exams]
    assert got == [
        ("ABC101", "INTRODUCTION TO EXAMPLES", "PAPER ONE (THEORY)", date(2026, 10, 26), time(9, 0), 180),
        ("DEF202", "MADE-UP STUDIES II", "PAPER 1", date(2026, 11, 2), time(14, 0), None),
        ("GHI303", "PRETEND PATHOLOGY", None, date(2026, 11, 5), time(14, 0), 60),
        ("JKL404", "TOO LONG TO BE TRUE", "PAPER 2", date(2026, 11, 6), time(9, 0), None),
    ]
    assert "42" not in repr(reading.exams)
    assert reading.lines[0] == "Found 4 exam papers for 4 modules, Mon 26 Oct to Fri 6 Nov 2026."


def test_text_without_an_exam_list_says_so():
    reading = read_exam_list(["Timetable 2026", "MONDAY TUESDAY"])
    assert reading.exams == [] and reading.lines[0].startswith("We couldn't find an exam list in this PDF")


def test_module_codes_compare_without_case_or_spaces():
    assert module_code("cos 132") == module_code("COS132") == "COS132"


def test_the_exams_in_words_name_the_next_one_and_any_two_at_once():
    exams = [
        Exam("a", "ABC101", date(2026, 10, 26), time(9, 0), 180),
        Exam("b", "DEF202", date(2026, 10, 26), time(11, 0), 120),
        Exam("c", "GHI303", date(2026, 11, 5), time(14, 0), None),
    ]
    assert exam_summary(exams, date(2026, 10, 20)) == [
        "3 exams, Mon 26 Oct to Thu 5 Nov 2026.",
        "Next: ABC101 on Mon 26 Oct 2026 at 09:00, in 6 days.",
        "ABC101 and DEF202 are both on Mon 26 Oct 2026 at the same time: check your exam list or ask your faculty.",
    ]
    assert exam_summary(exams, date(2026, 12, 1))[1] == "All your exams are behind you."
    assert exam_summary([], date(2026, 10, 20)) == [
        "No exams yet. Add them from your university's exam list, or one at a time."]
