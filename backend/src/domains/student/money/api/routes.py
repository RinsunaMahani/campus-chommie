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
