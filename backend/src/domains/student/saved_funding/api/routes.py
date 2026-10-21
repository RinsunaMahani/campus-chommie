"""
/api/v1/me/funding -- the funding the signed-in student saved. Owner-only.

  GET    /me/funding           {today, summary, counts, funders: [card + saved_on], confirmed, notice}
  PUT    /me/funding/<id>      save it (saving again is fine) -> {funder}
  DELETE /me/funding/<id>      -> {}

Nothing else is sent: no body, no query. A funder the pack doesn't list, or one the student
hasn't saved, is a 404. Thin: validate -> service -> answer. Rate-limited per student.
"""
from __future__ import annotations

from flask import request

from src.api import api_bp
from src.core.decorators import auth_required, current_user
from src.core.responses import success_response
from src.shared.rate_limit.keys import per_user
from src.shared.rate_limit.limiter import limiter

from ..constants import CHANGE_LIMIT, READ_LIMIT
from ..schemas.saved_funding_schemas import NothingSchema, load
from ..services import saved_funding_service as service

BASE = "/me/funding"


def _nothing_sent() -> None:
    """No query parameters, and no body beyond an empty JSON object."""
    load(NothingSchema(), request.args.to_dict())
    if request.get_data(cache=True):
        body = request.get_json(silent=True)
        load(NothingSchema(), body if body is not None else "not JSON")


@api_bp.get(BASE)
@limiter.limit(READ_LIMIT, key_func=per_user)
@auth_required
def my_saved_funding():
    _nothing_sent()
    return success_response(service.mine(current_user()))


@api_bp.put(f"{BASE}/<funder_id>")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def save_funder(funder_id: str):
    _nothing_sent()
    return success_response(service.save(current_user(), funder_id))


@api_bp.delete(f"{BASE}/<funder_id>")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def unsave_funder(funder_id: str):
    _nothing_sent()
    return success_response(service.unsave(current_user(), funder_id))
