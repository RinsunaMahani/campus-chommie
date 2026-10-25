"""
/api/v1 -- the signed-in student's alerts and their campus support.

  GET /alerts     {today, alerts, notes}: each alert's kind, title, message and actions (where each leads,
                  and the campus's own support service when the pack has one)
  GET /support    {university, campus, kinds}: counselling, crisis lines, financial aid, food support,
                  tutoring, chaplaincy and health for the student's campus, or "Not verified yet"
  GET /me/next-steps  {today, steps}: "Do this next" for Home, at most three, each with why, one action and
                  where it leads (money, week, timetable, funding, support)
  GET /me/week-review?week=auto|this|last  your week in review: {week_start, week_end, finished, ready, headline,
                  done, coming, marks, spending, support}; the week is the one the money check-in uses

Thin: validate -> service -> answer. Rate-limited per student; nothing is stored.
"""
from __future__ import annotations

from flask import request

from src.api import api_bp
from src.core.decorators import auth_required, current_user
from src.core.responses import success_response
from src.shared.rate_limit.keys import per_user
from src.shared.rate_limit.limiter import limiter

from ..constants import READ_LIMIT
from ..schemas.alert_schemas import NoQuerySchema, WeekReviewQuerySchema, load, load_query
from ..services import alert_service as service
from ..services import next_steps_service, review_service


@api_bp.get("/alerts")
@limiter.limit(READ_LIMIT, key_func=per_user)
@auth_required
def my_alerts():
    load(NoQuerySchema(), request.args.to_dict())
    return success_response(service.alerts(current_user()))


@api_bp.get("/support")
@limiter.limit(READ_LIMIT, key_func=per_user)
@auth_required
def my_campus_support():
    load(NoQuerySchema(), request.args.to_dict())
    return success_response(service.support(current_user()))


@api_bp.get("/me/next-steps")
@limiter.limit(READ_LIMIT, key_func=per_user)
@auth_required
def my_next_steps():
    load(NoQuerySchema(), request.args.to_dict())
    return success_response(next_steps_service.mine(current_user()))


@api_bp.get("/me/week-review")
@limiter.limit(READ_LIMIT, key_func=per_user)
@auth_required
def my_week_review():
    q = load_query(WeekReviewQuerySchema(), request.args)
    return success_response(review_service.review(current_user(), q["week"]))
