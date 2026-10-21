"""
/api/v1/academics -- My marks: the signed-in student's own modules and
assessments. Owner-only; standing and projection come in every answer.

  GET    /academics/modules                                {modules}
  POST   /academics/modules                                {code, name?, target?} -> {module}
  PUT    /academics/modules/<id>                           {code, name, target} -> {module}
  DELETE /academics/modules/<id>                           with its assessments
  POST   /academics/modules/<id>/assessments               {name, weight, mark?} -> {module}
  PUT    /academics/modules/<id>/assessments/<aid>         {name, weight, mark} -> {module}
  DELETE /academics/modules/<id>/assessments/<aid>         -> {module}

Thin: validate -> service -> answer. Rate-limited per student; another
student's module is the same 404 as one that doesn't exist.
"""
from __future__ import annotations

import uuid

from flask import request

from src.api import api_bp
from src.core.decorators import auth_required, current_user
from src.core.responses import success_response
from src.shared.rate_limit.keys import per_user
from src.shared.rate_limit.limiter import limiter

from ..constants import CHANGE_LIMIT, READ_LIMIT
from ..schemas.academics_schemas import AssessmentSchema, ModuleSchema, NoQuerySchema, load
from ..services import academics_service as service

BASE = "/academics/modules"


@api_bp.get(BASE)
@limiter.limit(READ_LIMIT, key_func=per_user)
@auth_required
def my_modules():
    load(NoQuerySchema(), request.args.to_dict())
    return success_response(service.list_modules(current_user()))


@api_bp.post(BASE)
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def add_module():
    body = load(ModuleSchema(), request.get_json(silent=True))
    return success_response(service.add_module(current_user(), body), status_code=201)


@api_bp.put(f"{BASE}/<uuid:module_id>")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def replace_module(module_id: uuid.UUID):
    body = load(ModuleSchema(), request.get_json(silent=True))
    return success_response(service.replace_module(current_user(), module_id, body))


@api_bp.delete(f"{BASE}/<uuid:module_id>")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def delete_module(module_id: uuid.UUID):
    return success_response(service.delete_module(current_user(), module_id))


@api_bp.post(f"{BASE}/<uuid:module_id>/assessments")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def add_assessment(module_id: uuid.UUID):
    body = load(AssessmentSchema(), request.get_json(silent=True))
    return success_response(service.add_assessment(current_user(), module_id, body), status_code=201)


@api_bp.put(f"{BASE}/<uuid:module_id>/assessments/<uuid:assessment_id>")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def replace_assessment(module_id: uuid.UUID, assessment_id: uuid.UUID):
    body = load(AssessmentSchema(), request.get_json(silent=True))
    return success_response(service.replace_assessment(current_user(), module_id, assessment_id, body))


@api_bp.delete(f"{BASE}/<uuid:module_id>/assessments/<uuid:assessment_id>")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def delete_assessment(module_id: uuid.UUID, assessment_id: uuid.UUID):
    return success_response(service.delete_assessment(current_user(), module_id, assessment_id))
