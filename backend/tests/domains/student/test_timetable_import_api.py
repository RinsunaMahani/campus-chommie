"""
Timetable import and exams: a student sends their timetable's PDF and gets back everything it lists (nothing is
saved), then saves the classes or exams they checked in one go. Exams are owner-only like classes, in the export,
and gone with the account. Hostile files and forms are refused. The PDFs are made up here (pdf_helpers).
"""
from __future__ import annotations

import io

import pytest
from pdf_helpers import exam_list_pdf, make_pdf, week_grid_pdf
from student_helpers import student

from src.extensions import db
from src.shared.rate_limit.limiter import limiter

API = "/api/v1"
TT = f"{API}/me/timetable"
EXAMS = f"{API}/me/exams"
IMPORT = f"{TT}/import"
EXAM = {"module": "abc 101", "on": "2026-10-26", "starts": "09:00", "minutes": 180, "title": "Introduction to examples",
        "paper": "Paper one"}
LECTURE = {"module": "ABC101", "kind": "lecture", "weekday": 0, "starts": "08:00", "ends": "09:50", "venue": "HALL 1"}


@pytest.fixture
def lerato(client, outbox):
    return student(client, outbox, "lerato@example.com")


@pytest.fixture
def sipho(client, outbox):
    return student(client, outbox, "sipho@example.com")


@pytest.fixture
def limits_on(app):
    was = limiter.enabled
    limiter.enabled = True
    with app.app_context():
        limiter.reset()
    yield
    with app.app_context():
        limiter.reset()
    limiter.enabled = was


def ok(response, status=200):
    assert response.status_code == status, response.get_json()
    return response.get_json()["data"]


def upload(client, who, data: bytes, layout: str = "classes", name: str = "timetable.pdf", **extra):
    form = {"layout": layout, "file": (io.BytesIO(data), name), **extra}
    return client.post(IMPORT, data=form, headers=who.headers, content_type="multipart/form-data")


def table_rows(app, table: str) -> int:
    with app.app_context():
        return db.session.execute(db.text(f"SELECT count(*) FROM {table}")).scalar()


def test_a_week_grid_pdf_is_read_back_and_nothing_is_saved(app, client, lerato):
    data = ok(upload(client, lerato, week_grid_pdf()))
    assert data["layout"] == "classes" and data["modules"] == ["ABC101", "DEF202"] and data["exams"] == []
    assert data["classes"] == [
        {"module": "ABC101", "kind": "lecture", "weekday": 0, "day": "Monday", "starts": "08:00", "ends": "09:50",
         "venue": "HALL 1"},
        {"module": "DEF202", "kind": "practical", "weekday": 1, "day": "Tuesday", "starts": "08:00", "ends": "08:50",
         "venue": "LAB 3"},
    ]
    assert data["lines"][0] == "Found 2 classes for 2 modules, on Monday and Tuesday."
    assert ok(client.get(TT, headers=lerato.headers))["entries"] == []
    assert table_rows(app, "student.timetable_entries") == 0


def test_an_exam_list_pdf_is_read_back_without_student_numbers(client, lerato):
    data = ok(upload(client, lerato, exam_list_pdf(), layout="exams"))
    assert data["modules"] == ["ABC101", "DEF202", "XYZ999"] and data["classes"] == []
    assert data["exams"][0] == {"module": "ABC101", "title": "INTRODUCTION TO EXAMPLES", "paper": "PAPER ONE",
                                "on": "2026-10-26", "day": "Mon 26 Oct 2026", "starts": "09:00", "minutes": 180}
    assert "42" not in str(data["exams"])  # the number of students writing it isn't passed on


def test_the_wrong_layout_says_what_it_couldnt_find(client, lerato):
    data = ok(upload(client, lerato, exam_list_pdf(), layout="classes"))
    assert data["classes"] == [] and data["lines"][0].startswith("We couldn't find a week grid in this PDF")


@pytest.mark.parametrize("data, message", [
    (b"just text, not a pdf", "That isn't a PDF."),
    (b"%PDF-1.4\n" + b"\x00garbage" * 200, "We couldn't read that PDF."),
    (make_pdf([{"texts": [(50, 500, 9, f"page {i}")]} for i in range(31)]), "more than 30 pages"),
])
def test_files_that_arent_a_readable_timetable_are_refused_plainly(client, lerato, data, message):
    r = upload(client, lerato, data)
    assert r.status_code == 422
    assert message in str(r.get_json()["errors"])


def test_odd_forms_are_refused(client, lerato):
    pdf = week_grid_pdf()
    assert upload(client, lerato, pdf, layout="calendar").status_code == 422
    assert upload(client, lerato, pdf, student_number="123").status_code == 422
    no_file = client.post(IMPORT, data={"layout": "classes"}, headers=lerato.headers, content_type="multipart/form-data")
    assert no_file.status_code == 422
    two = client.post(IMPORT, data={"layout": "classes", "file": [(io.BytesIO(pdf), "a.pdf"), (io.BytesIO(pdf), "b.pdf")]},
                      headers=lerato.headers, content_type="multipart/form-data")
    assert two.status_code == 422
    other_field = client.post(IMPORT, data={"layout": "classes", "upload": (io.BytesIO(pdf), "a.pdf")},
                              headers=lerato.headers, content_type="multipart/form-data")
    assert other_field.status_code == 422
    assert client.post(IMPORT, json={"layout": "classes"}, headers=lerato.headers).status_code == 422
    query = client.post(f"{IMPORT}?debug=1", data={"layout": "classes", "file": (io.BytesIO(pdf), "a.pdf")},
                        headers=lerato.headers, content_type="multipart/form-data")
    assert query.status_code == 422


def test_a_file_over_the_request_limit_is_refused(client, lerato):
    r = upload(client, lerato, b"%PDF-1.4\n" + b" " * (1024 * 1024 + 1))
    assert r.status_code == 413


def test_signed_out_is_refused(client):
    assert client.post(IMPORT, data={"layout": "classes"}, content_type="multipart/form-data").status_code == 401
    assert client.get(EXAMS).status_code == 401
    assert client.post(f"{TT}/batch", json={"entries": [LECTURE]}).status_code == 401
    assert client.post(f"{EXAMS}/batch", json={"exams": [EXAM]}).status_code == 401


def test_reading_pdfs_has_its_own_tighter_limit(client, lerato, limits_on):
    codes = [upload(client, lerato, b"not a pdf").status_code for _ in range(7)]
    assert codes[:6] == [422] * 6 and codes[6] == 429


def test_checked_classes_are_saved_together_and_replace_clears_the_week_first(client, lerato):
    ok(client.post(TT, json=LECTURE | {"module": "OLD100"}, headers=lerato.headers), 201)
    added = ok(client.post(f"{TT}/batch", json={"entries": [LECTURE]}, headers=lerato.headers), 201)
    assert [e["module"] for e in added["entries"]] == ["ABC101", "OLD100"]
    replaced = ok(client.post(f"{TT}/batch", json={"entries": [LECTURE | {"weekday": 2}], "replace": True},
                              headers=lerato.headers), 201)
    assert [(e["module"], e["day"]) for e in replaced["entries"]] == [("ABC101", "Wednesday")]


def test_a_batch_with_one_bad_class_saves_none(client, lerato):
    r = client.post(f"{TT}/batch", json={"entries": [LECTURE, LECTURE | {"starts": "08:03"}], "replace": True},
                    headers=lerato.headers)
    assert r.status_code == 422
    assert ok(client.get(TT, headers=lerato.headers))["entries"] == []


def test_a_batch_stays_within_sixty_classes(client, lerato):
    ok(client.post(f"{TT}/batch", json={"entries": [LECTURE] * 60}, headers=lerato.headers), 201)
    assert client.post(f"{TT}/batch", json={"entries": [LECTURE]}, headers=lerato.headers).status_code == 422
    assert client.post(f"{TT}/batch", json={"entries": [LECTURE] * 61, "replace": True},
                       headers=lerato.headers).status_code == 422
    assert len(ok(client.get(TT, headers=lerato.headers))["entries"]) == 60


@pytest.mark.parametrize("body", [
    {"entries": []}, {"entries": LECTURE}, {"entries": [LECTURE], "replace": "yes"},
    {"entries": [LECTURE | {"user_id": "x"}]}, {"entries": [LECTURE], "user_id": "x"},
])
def test_odd_class_batches_are_refused(client, lerato, body):
    assert client.post(f"{TT}/batch", json=body, headers=lerato.headers).status_code == 422


def test_exams_read_back_soonest_first_with_the_next_one_and_clashes(client, lerato):
    ok(client.post(EXAMS, json=EXAM | {"on": "2026-11-02"}, headers=lerato.headers), 201)
    first = ok(client.post(EXAMS, json=EXAM, headers=lerato.headers), 201)
    assert first["exam"] | {"id": "x"} == {
        "id": "x", "module": "ABC 101", "title": "Introduction to examples", "paper": "Paper one", "on": "2026-10-26",
        "day": "Mon 26 Oct 2026", "starts": "09:00", "minutes": 180, "venue": None, "clashes": False,
    }
    data = ok(client.post(EXAMS, json=EXAM | {"module": "DEF202", "starts": "10:00"}, headers=lerato.headers), 201)
    assert [(e["module"], e["on"], e["clashes"]) for e in data["exams"]] == [
        ("ABC 101", "2026-10-26", True), ("DEF202", "2026-10-26", True), ("ABC 101", "2026-11-02", False)]
    assert data["lines"][0] == "3 exams, Mon 26 Oct to Mon 2 Nov 2026."
    assert "are both on Mon 26 Oct 2026 at the same time" in data["lines"][-1]


def test_checked_exams_are_saved_together_and_replace_clears_them_first(client, lerato):
    ok(client.post(EXAMS, json=EXAM | {"module": "OLD100"}, headers=lerato.headers), 201)
    data = ok(client.post(f"{EXAMS}/batch", json={"exams": [EXAM, EXAM | {"on": "2026-11-02", "minutes": None}],
                                                  "replace": True}, headers=lerato.headers), 201)
    assert [(e["module"], e["minutes"]) for e in data["exams"]] == [("ABC 101", 180), ("ABC 101", None)]


def test_another_students_exam_is_a_404_and_stays(client, lerato, sipho):
    exam = ok(client.post(EXAMS, json=EXAM, headers=lerato.headers), 201)["exam"]
    r = client.delete(f"{EXAMS}/{exam['id']}", headers=sipho.headers)
    assert r.status_code == 404 and r.get_json()["code"] == "EXAM_NOT_FOUND"
    assert ok(client.get(EXAMS, headers=sipho.headers))["exams"] == []
    assert len(ok(client.get(EXAMS, headers=lerato.headers))["exams"]) == 1
    assert ok(client.delete(f"{EXAMS}/{exam['id']}", headers=lerato.headers))["exams"] == []
    assert client.delete(f"{EXAMS}/not-a-uuid", headers=lerato.headers).status_code == 404


@pytest.mark.parametrize("change", [
    {"module": ""}, {"module": "ABC;101"}, {"on": "26-10-2026"}, {"on": "2026-02-30"}, {"starts": "9:00"},
    {"starts": "09:03"}, {"starts": "04:00"}, {"minutes": 0}, {"minutes": 481}, {"minutes": "180"},
    {"title": "x" * 81}, {"paper": "Paper\none"}, {"venue": "   "}, {"students": 42}, {"user_id": "someone-else"},
])
def test_odd_exams_are_refused(client, lerato, change):
    assert client.post(EXAMS, json=EXAM | change, headers=lerato.headers).status_code == 422


def test_at_most_forty_exams(client, lerato):
    ok(client.post(f"{EXAMS}/batch", json={"exams": [EXAM] * 40}, headers=lerato.headers), 201)
    assert client.post(EXAMS, json=EXAM, headers=lerato.headers).status_code == 422
    assert client.post(f"{EXAMS}/batch", json={"exams": [EXAM]}, headers=lerato.headers).status_code == 422


def test_the_export_has_the_exams(client, lerato):
    ok(client.post(EXAMS, json=EXAM, headers=lerato.headers), 201)
    data = ok(client.get(f"{API}/me/export", headers=lerato.headers))
    assert data["timetable"]["exams"] == [{
        "module": "ABC 101", "title": "Introduction to examples", "paper": "Paper one", "on": "2026-10-26",
        "day": "Mon 26 Oct 2026", "starts": "09:00", "minutes": 180, "venue": None,
    }]
