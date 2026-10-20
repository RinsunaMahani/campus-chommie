"""
/api/v1/pathways -- the course finder. Anyone can use it; no account.

  POST /pathways/points   {marks: [{subject, percent}]}                     -> {universities}: points at each
  POST /pathways/assess   {university, marks: [{subject, percent}]}         -> {university, matches}
  POST /pathways/plan     {university, goal, marks: [{subject, percent}]}   -> {plan}, with how to apply
  GET  /pathways/apply/<university>                                         -> {university, apply}: no marks needed

Marks are used for the answer and forgotten: nothing is stored or logged.
Thin: validate -> service -> answer. Rate-limited per IP.
"""
from __future__ import annotations

from flask import request

from src.api import api_bp
from src.core.responses import success_response
from src.shared.rate_limit.limiter import limiter

from ..constants import APPLY_LIMIT, ASSESS_LIMIT, PLAN_LIMIT, POINTS_LIMIT
from ..schemas.course_finder_schemas import AssessSchema, NoQuerySchema, PlanSchema, PointsSchema, load
from ..services import course_finder_service as service

BASE = "/pathways"


@api_bp.post(f"{BASE}/points")
@limiter.limit(POINTS_LIMIT)
def points_everywhere():
    body = load(PointsSchema(), request.get_json(silent=True))
    return success_response(service.points(body["marks"]))


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


@api_bp.get(f"{BASE}/apply/<university_id>")
@limiter.limit(APPLY_LIMIT)
def how_to_apply(university_id: str):
    load(NoQuerySchema(), request.args.to_dict())
    return success_response(service.apply_info(university_id))
