"""
/api/v1/classes -- classes, invite codes and reps.

  POST   /classes                       {university, campus?, module_code, module_name?, year} -> 201 {class}; you're its rep
  POST   /classes/join                  {code}: an invite code joins; a rep code makes you a rep -> {class, joined}
  GET    /classes/mine                  {classes}: with your role and member counts (never who)
  POST   /classes/<id>/reps             rep only -> 201 {code, expires_at}: a one-time code for the next rep
  DELETE /classes/<id>/membership       leave the class

Thin: validate -> service -> answer. Rate-limited per student (joining
slowly, so codes can't be guessed); a class you're not in is the same 404
as one that doesn't exist.
"""
from __future__ import annotations

import uuid

from flask import request

from src.api import api_bp
from src.core.decorators import auth_required, current_user
from src.core.responses import success_response
from src.shared.rate_limit.keys import per_user
from src.shared.rate_limit.limiter import limiter

from ..constants import CHANGE_LIMIT, CREATE_LIMIT, JOIN_LIMIT, READ_LIMIT
from ..schemas.class_schemas import ClassSchema, JoinSchema, NoBodySchema, NoQuerySchema, load
from ..services import class_service as service

BASE = "/classes"


@api_bp.post(BASE)
@limiter.limit(CREATE_LIMIT, key_func=per_user)
@auth_required
def create_class():
    body = load(ClassSchema(), request.get_json(silent=True))
    return success_response(service.create(current_user(), body), status_code=201)


@api_bp.post(f"{BASE}/join")
@limiter.limit(JOIN_LIMIT, key_func=per_user)
@auth_required
def join_class():
    body = load(JoinSchema(), request.get_json(silent=True))
    return success_response(service.join(current_user(), body["code"]))


@api_bp.get(f"{BASE}/mine")
@limiter.limit(READ_LIMIT, key_func=per_user)
@auth_required
def my_classes():
    load(NoQuerySchema(), request.args.to_dict())
    return success_response(service.mine(current_user()))


@api_bp.post(f"{BASE}/<uuid:class_id>/reps")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def make_rep_code(class_id: uuid.UUID):
    load(NoBodySchema(), request.get_json(silent=True))
    return success_response(service.rep_code(current_user(), class_id), status_code=201)


@api_bp.delete(f"{BASE}/<uuid:class_id>/membership")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def leave_class(class_id: uuid.UUID):
    return success_response(service.leave(current_user(), class_id))
