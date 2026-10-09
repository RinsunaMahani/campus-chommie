"""
/api/v1/pathways -- the course finder. Anyone can use it; no account.

  POST /pathways/assess   {university, marks: [{subject, percent}]}         -> {university, matches}
  POST /pathways/plan     {university, goal, marks: [{subject, percent}]}   -> {plan}

Marks are used for the answer and forgotten: nothing is stored or logged.
Thin: validate -> service -> answer. Rate-limited per IP.
"""
from __future__ import annotations

from flask import request

from src.api import api_bp
from src.core.responses import success_response
from src.shared.rate_limit.limiter import limiter

from ..constants import ASSESS_LIMIT, PLAN_LIMIT
from ..schemas.course_finder_schemas import AssessSchema, PlanSchema, load
from ..services import course_finder_service as service

BASE = "/pathways"


@api_bp.post(f"{BASE}/assess")
@limiter.limit(ASSESS_LIMIT)
def assess_marks():
    body = load(AssessSchema(), request.get_json(silent=True))
    return success_response(service.assess(body["university"], body["marks"]))


@api_bp.post(f"{BASE}/plan")
@limiter.limit(PLAN_LIMIT)
def plan_choices():
    body = load(PlanSchema(), request.get_json(silent=True))
    return success_response(service.plan(body["university"], body["goal"], body["marks"]))
