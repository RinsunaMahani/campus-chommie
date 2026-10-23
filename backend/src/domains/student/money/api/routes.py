"""
/api/v1/money -- the signed-in student's own money. Owner-only.

  GET    /money/settings                       {settings | null}
  PUT    /money/settings                       {balance_cents, balance_on, essentials_per_day_cents, life_fund_reserve_cents}
  GET    /money/income-sources                 {income_sources}
  POST   /money/income-sources                 {label, amount_cents, day_of_month | expected_on, reliability}
  PUT    /money/income-sources/<id>            the same fields; its unreceived payments are made again
  DELETE /money/income-sources/<id>            with its payments
  GET    /money/payments                       {payments}: a month back to the runway's horizon
  PATCH  /money/payments/<id>                  {expected_on?, amount_cents?, received?}
  GET    /money/spending?days=30               {spending}: newest first
  PUT    /money/spending/<YYYY-MM-DD>          {amount_cents}: one number per day
  DELETE /money/spending/<YYYY-MM-DD>
  GET    /money/summary?late=true              balance, pace, runway, safe to spend, life fund, next payment
  GET    /money/cheap-things                   the data pack's cheap things to do near the student's campus
  POST   /money/afford                         {amount_cents}: what buying it today does (nothing stored)
  GET    /money/plan                           {payday, goals, university_dates, lines}
  POST   /money/goals                          {label, amount_cents, due_on, saved_cents?, from_university?}
  PATCH  /money/goals/<id>                     any of the same fields
  DELETE /money/goals/<id>

Amounts are integer cents. Thin: validate -> service -> answer. Rate-limited
per student; another student's row is the same 404 as one that doesn't exist.
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
from ..schemas.money_schemas import (
    AffordSchema,
    CheckinSchema,
    FixedCostChangeSchema,
    FixedCostSchema,
    GoalChangeSchema,
    GoalSchema,
    NoQuerySchema,
    PaymentUpdateSchema,
    SettingsSchema,
    SourceSchema,
    SpendingQuerySchema,
    SpendingSchema,
    SummaryQuerySchema,
    load,
)
from ..services import money_service as service

BASE = "/money"


@api_bp.get(f"{BASE}/settings")
@limiter.limit(READ_LIMIT, key_func=per_user)
@auth_required
def my_money_settings():
    load(NoQuerySchema(), request.args.to_dict())
    return success_response(service.get_settings(current_user()))


@api_bp.put(f"{BASE}/settings")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def save_my_money_settings():
    body = load(SettingsSchema(), request.get_json(silent=True))
    return success_response(service.put_settings(current_user(), body))


@api_bp.get(f"{BASE}/income-sources")
@limiter.limit(READ_LIMIT, key_func=per_user)
@auth_required
def my_income_sources():
    load(NoQuerySchema(), request.args.to_dict())
    return success_response(service.list_sources(current_user()))


@api_bp.post(f"{BASE}/income-sources")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def add_income_source():
    body = load(SourceSchema(), request.get_json(silent=True))
    return success_response(service.add_source(current_user(), body), status_code=201)


@api_bp.put(f"{BASE}/income-sources/<uuid:source_id>")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def replace_income_source(source_id: uuid.UUID):
    body = load(SourceSchema(), request.get_json(silent=True))
    return success_response(service.replace_source(current_user(), source_id, body))


@api_bp.delete(f"{BASE}/income-sources/<uuid:source_id>")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def delete_income_source(source_id: uuid.UUID):
    return success_response(service.delete_source(current_user(), source_id))


@api_bp.get(f"{BASE}/payments")
@limiter.limit(READ_LIMIT, key_func=per_user)
@auth_required
def my_payments():
    load(NoQuerySchema(), request.args.to_dict())
    return success_response(service.list_payments(current_user()))


@api_bp.patch(f"{BASE}/payments/<uuid:payment_id>")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def update_payment(payment_id: uuid.UUID):
    body = load(PaymentUpdateSchema(), request.get_json(silent=True))
    return success_response(service.update_payment(current_user(), payment_id, body))


@api_bp.get(f"{BASE}/spending")
@limiter.limit(READ_LIMIT, key_func=per_user)
@auth_required
def my_spending():
    query = load(SpendingQuerySchema(), request.args.to_dict())
    return success_response(service.list_spending(current_user(), query["days"]))


@api_bp.put(f"{BASE}/spending/<spent_on>")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def log_spending(spent_on: str):
    body = load(SpendingSchema(), request.get_json(silent=True))
    return success_response(service.put_spending(current_user(), spent_on, body["amount_cents"]))


@api_bp.delete(f"{BASE}/spending/<spent_on>")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def delete_spending(spent_on: str):
    return success_response(service.delete_spending(current_user(), spent_on))


@api_bp.get(f"{BASE}/summary")
@limiter.limit(READ_LIMIT, key_func=per_user)
@auth_required
def my_money_summary():
    query = load(SummaryQuerySchema(), request.args.to_dict())
    return success_response(service.summary(current_user(), query["late"]))


@api_bp.get(f"{BASE}/cheap-things")
@limiter.limit(READ_LIMIT, key_func=per_user)
@auth_required
def cheap_things_near_me():
    load(NoQuerySchema(), request.args.to_dict())
    return success_response(service.cheap_things(current_user()))


@api_bp.post(f"{BASE}/afford")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def can_i_afford():
    load(NoQuerySchema(), request.args.to_dict())
    body = load(AffordSchema(), request.get_json(silent=True))
    return success_response(service.can_i_afford(current_user(), body["amount_cents"]))


@api_bp.get(f"{BASE}/plan")
@limiter.limit(READ_LIMIT, key_func=per_user)
@auth_required
def my_money_plan():
    load(NoQuerySchema(), request.args.to_dict())
    return success_response(service.plan(current_user()))


@api_bp.post(f"{BASE}/goals")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def add_money_goal():
    load(NoQuerySchema(), request.args.to_dict())
    body = load(GoalSchema(), request.get_json(silent=True))
    return success_response(service.add_goal(current_user(), body), status_code=201)


@api_bp.patch(f"{BASE}/goals/<uuid:goal_id>")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def change_money_goal(goal_id: uuid.UUID):
    load(NoQuerySchema(), request.args.to_dict())
    body = load(GoalChangeSchema(), request.get_json(silent=True))
    return success_response(service.change_goal(current_user(), goal_id, body))


@api_bp.delete(f"{BASE}/goals/<uuid:goal_id>")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def delete_money_goal(goal_id: uuid.UUID):
    load(NoQuerySchema(), request.args.to_dict())
    return success_response(service.delete_goal(current_user(), goal_id))


# ------------------------------------------------------------- fixed costs


@api_bp.get(f"{BASE}/fixed-costs")
@limiter.limit(READ_LIMIT, key_func=per_user)
@auth_required
def my_fixed_costs():
    load(NoQuerySchema(), request.args.to_dict())
    return success_response(service.list_fixed_costs(current_user()))


@api_bp.post(f"{BASE}/fixed-costs")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def add_fixed_cost():
    load(NoQuerySchema(), request.args.to_dict())
    body = load(FixedCostSchema(), request.get_json(silent=True))
    return success_response(service.add_fixed_cost(current_user(), body), status_code=201)


@api_bp.put(f"{BASE}/fixed-costs/<uuid:cost_id>")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def replace_fixed_cost(cost_id: uuid.UUID):
    load(NoQuerySchema(), request.args.to_dict())
    body = load(FixedCostSchema(), request.get_json(silent=True))
    return success_response(service.replace_fixed_cost(current_user(), cost_id, body))


@api_bp.patch(f"{BASE}/fixed-costs/<uuid:cost_id>")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def change_fixed_cost(cost_id: uuid.UUID):
    load(NoQuerySchema(), request.args.to_dict())
    body = load(FixedCostChangeSchema(), request.get_json(silent=True))
    return success_response(service.replace_fixed_cost(current_user(), cost_id, body))


@api_bp.delete(f"{BASE}/fixed-costs/<uuid:cost_id>")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def delete_fixed_cost(cost_id: uuid.UUID):
    load(NoQuerySchema(), request.args.to_dict())
    return success_response(service.delete_fixed_cost(current_user(), cost_id))


# ----------------------------------------------------------- weekly checkin


@api_bp.get(f"{BASE}/checkin")
@limiter.limit(READ_LIMIT, key_func=per_user)
@auth_required
def my_checkin_status():
    load(NoQuerySchema(), request.args.to_dict())
    return success_response(service.get_checkin_status(current_user()))


@api_bp.post(f"{BASE}/checkin")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def submit_checkin():
    load(NoQuerySchema(), request.args.to_dict())
    body = load(CheckinSchema(), request.get_json(silent=True))
    return success_response(service.submit_checkin(current_user(), body))


# ----------------------------------------------------------- money health


@api_bp.get(f"{BASE}/health")
@limiter.limit(READ_LIMIT, key_func=per_user)
@auth_required
def my_money_health():
    load(NoQuerySchema(), request.args.to_dict())
    return success_response(service.get_money_health(current_user()))

