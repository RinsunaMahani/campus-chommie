"""
/api/v1/universities -- what the data packs say, for anyone (no account).

  GET /universities         {universities: [{id, name, city, academic_year, programmes, confirmed, notice}]}
  GET /universities/<id>    {university: the pack, with confirmed and notice}

Read-only and public. Thin: validate -> service -> answer. Rate-limited per IP.
"""
from __future__ import annotations

from flask import request

from src.api import api_bp
from src.core.responses import success_response
from src.shared.rate_limit.limiter import limiter

from ..constants import READ_LIMIT
from ..schemas.university_schemas import NoQuerySchema, load
from ..services import university_service as service

BASE = "/universities"


@api_bp.get(BASE)
@limiter.limit(READ_LIMIT)
def list_universities():
    load(NoQuerySchema(), request.args.to_dict())
    return success_response({"universities": service.summaries()})


@api_bp.get(f"{BASE}/<university_id>")
@limiter.limit(READ_LIMIT)
def get_university(university_id: str):
    load(NoQuerySchema(), request.args.to_dict())
    return success_response({"university": service.detail(university_id)})
