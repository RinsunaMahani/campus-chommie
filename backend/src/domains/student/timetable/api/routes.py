"""
/api/v1/me/timetable -- the classes the signed-in student entered for their week. Owner-only.

  GET    /me/timetable          {entries: [{id, module, title, kind, weekday, day, starts, ends, venue, clashes}], lines}
  POST   /me/timetable          {module, kind, weekday, starts, ends, title?, venue?} -> {entry, entries, lines}
  PATCH  /me/timetable/<id>     any of the same fields -> {entry, entries, lines}
  DELETE /me/timetable/<id>     -> {entries, lines}

A class that isn't the student's is a 404, the same as one that doesn't exist. Strict bodies, no query
parameters. Thin: validate -> service -> answer. Rate-limited per student.
"""
from __future__ import annotations

from flask import request

from src.api import api_bp
from src.core.decorators import auth_required, current_user
from src.core.responses import success_response
from src.shared.rate_limit.keys import per_user
from src.shared.rate_limit.limiter import limiter

from ..constants import CHANGE_LIMIT, READ_LIMIT
from ..schemas.timetable_schemas import EntryChangeSchema, EntrySchema, NothingSchema, load
from ..services import timetable_service as service

BASE = "/me/timetable"


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
