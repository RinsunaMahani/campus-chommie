"""
/api/v1/funding -- bursaries, merit awards and loans, for anyone (no account).

  GET /funding          ?field=a,b &status= &kind= &stage=  (all optional)
                        {today, summary, counts: {total, open_now, closing_soon}, fields, funders, confirmed, notice}
  GET /funding/<id>     {today, funder: card + who_can_apply, covers, obligations, apply, sources, confirmed, notice}

Read-only and public: nothing is stored, logged or asked about the learner. Thin:
validate -> service -> answer. Rate-limited per IP.
"""
from __future__ import annotations

from flask import request

from src.api import api_bp
from src.core.responses import success_response
from src.shared.rate_limit.limiter import limiter

from ..constants import READ_LIMIT
from ..schemas.funding_schemas import FundingListSchema, NoQuerySchema, load, query
from ..services import funding_service as service

BASE = "/funding"


@api_bp.get(BASE)
@limiter.limit(READ_LIMIT)
def list_funding():
    filters = load(FundingListSchema(), query(request.args))
    fields = filters["field"].split(",") if "field" in filters else None
    return success_response(
        service.funding_list(fields=fields, status=filters.get("status"), kind=filters.get("kind"), stage=filters.get("stage"))
    )


@api_bp.get(f"{BASE}/<funder_id>")
@limiter.limit(READ_LIMIT)
def get_funder(funder_id: str):
    load(NoQuerySchema(), query(request.args))
    return success_response(service.detail(funder_id))
