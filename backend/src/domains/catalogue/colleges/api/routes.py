"""
/api/v1/colleges -- public TVET colleges and DHET's registers of private institutions, for anyone (no account).

  GET /colleges           ?q= &kind= &province= &status= &page=   (all optional)
                          {summary, counts, total, page, pages, colleges, confirmed, notice}
  GET /colleges/check     ?name=   "is this college registered?"
                          {verdict, label, lines, colleges, unregistered, warning_signs, sources, confirmed, notice}
  GET /colleges/<id>      {college: card + sites, qualifications, occupational, notes, sources, ...}

Read-only and public: nothing is stored or logged, and no search is kept. Thin: validate -> service ->
answer. Rate-limited per IP.
"""
from __future__ import annotations

from flask import request

from src.api import api_bp
from src.core.responses import success_response
from src.shared.rate_limit.limiter import limiter

from ..constants import READ_LIMIT
from ..schemas.college_schemas import CheckSchema, CollegeListSchema, NoQuerySchema, load, query
from ..services import college_service as service

BASE = "/colleges"


@api_bp.get(BASE)
@limiter.limit(READ_LIMIT)
def list_colleges():
    f = load(CollegeListSchema(), query(request.args))
    return success_response(service.college_list(
        q=f.get("q"), kind=f.get("kind"), province=f.get("province"), status=f.get("status"), page=f.get("page", 1),
    ))


@api_bp.get(f"{BASE}/check")
@limiter.limit(READ_LIMIT)
def check_college():
    f = load(CheckSchema(), query(request.args))
    return success_response(service.check(f["name"]))


@api_bp.get(f"{BASE}/<college_id>")
@limiter.limit(READ_LIMIT)
def get_college(college_id: str):
    load(NoQuerySchema(), query(request.args))
    return success_response(service.detail(college_id))
