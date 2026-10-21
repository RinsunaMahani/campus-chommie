"""
/api/v1/me/timetable -- the classes the signed-in student entered for their week. Owner-only.

  GET    /me/timetable          {entries: [{id, module, title, kind, weekday, day, starts, ends, venue, clashes}], lines}
  POST   /me/timetable          {module, kind, weekday, starts, ends, title?, venue?} -> {entry, entries, lines}
  PATCH  /me/timetable/<id>     any of the same fields -> {entry, entries, lines}
  DELETE /me/timetable/<id>     -> {entries, lines}
  POST   /me/timetable/batch    {entries: [...], replace?} -> {entries, lines}     (after an import, all or none)
  POST   /me/timetable/import   multipart: file (a PDF), layout ("classes" | "exams")
                                -> {layout, modules, classes, exams, lines}      (nothing is saved)

  GET    /me/exams              {exams: [{id, module, title, paper, on, day, starts, minutes, venue, clashes}], lines}
  POST   /me/exams              {module, on, starts, minutes?, title?, paper?, venue?} -> {exam, exams, lines}
  POST   /me/exams/batch        {exams: [...], replace?} -> {exams, lines}
  DELETE /me/exams/<id>         -> {exams, lines}

A class or exam that isn't the student's is a 404, the same as one that doesn't exist. Strict bodies and
forms, no query parameters. Thin: validate -> service -> answer. Rate-limited per student; reading a PDF has
its own, tighter limit. The PDF is never stored (services/import_service.py).
"""
from __future__ import annotations

from flask import request

from src.api import api_bp
from src.core.decorators import auth_required, current_user
from src.core.responses import success_response
from src.shared.rate_limit.keys import per_user
from src.shared.rate_limit.limiter import limiter

from src.core.exceptions import ValidationError

from ..constants import CHANGE_LIMIT, IMPORT_LIMIT, READ_LIMIT
from ..schemas.timetable_schemas import (
    EntryBatchSchema, EntryChangeSchema, EntrySchema, ExamBatchSchema, ExamSchema, ImportFormSchema, NothingSchema,
    load,
)
from ..services import exam_service, import_service
from ..services import timetable_service as service

BASE = "/me/timetable"
EXAMS = "/me/exams"


def _no_query() -> None:
    load(NothingSchema(), request.args.to_dict())


@api_bp.get(BASE)
@limiter.limit(READ_LIMIT, key_func=per_user)
@auth_required
def my_timetable():
    _no_query()
    return success_response(service.mine(current_user()))


@api_bp.post(BASE)
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def add_class():
    _no_query()
    fields = load(EntrySchema(), request.get_json(silent=True))
    return success_response(service.add(current_user(), fields), status_code=201)


@api_bp.patch(f"{BASE}/<entry_id>")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def change_class(entry_id: str):
    _no_query()
    fields = load(EntryChangeSchema(), request.get_json(silent=True))
    return success_response(service.change(current_user(), entry_id, fields))


@api_bp.delete(f"{BASE}/<entry_id>")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def remove_class(entry_id: str):
    _no_query()
    return success_response(service.remove(current_user(), entry_id))


@api_bp.post(f"{BASE}/batch")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def add_classes():
    _no_query()
    body = load(EntryBatchSchema(), request.get_json(silent=True))
    return success_response(service.add_many(current_user(), body["entries"], body["replace"]), status_code=201)


@api_bp.post(f"{BASE}/import")
@limiter.limit(IMPORT_LIMIT, key_func=per_user)
@auth_required
def import_pdf():
    _no_query()
    form = load(ImportFormSchema(), request.form.to_dict())
    if set(request.files) != {"file"} or len(request.files.getlist("file")) != 1:
        raise ValidationError("Please check the highlighted fields.", errors=[{"file": ["Choose one PDF file."]}])
    return success_response(import_service.read(request.files["file"].read(), form["layout"]))


@api_bp.get(EXAMS)
@limiter.limit(READ_LIMIT, key_func=per_user)
@auth_required
def my_exams():
    _no_query()
    return success_response(exam_service.mine(current_user()))


@api_bp.post(EXAMS)
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def add_exam():
    _no_query()
    fields = load(ExamSchema(), request.get_json(silent=True))
    return success_response(exam_service.add(current_user(), fields), status_code=201)


@api_bp.post(f"{EXAMS}/batch")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def add_exams():
    _no_query()
    body = load(ExamBatchSchema(), request.get_json(silent=True))
    return success_response(exam_service.add_many(current_user(), body["exams"], body["replace"]), status_code=201)


@api_bp.delete(f"{EXAMS}/<exam_id>")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def remove_exam(exam_id: str):
    _no_query()
    return success_response(exam_service.remove(current_user(), exam_id))
