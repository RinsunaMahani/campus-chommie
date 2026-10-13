"""
/api/v1/universities/<id>/map -- campus maps, for anyone (no account).

  GET /universities/<id>/map?campus=   {university, campuses: [{id, name, mapped, south_west, north_east,
                                        centre, outline, places, support, lines, source_url}],
                                        attribution, attribution_url, licence, licence_url, confirmed, notice}

Read-only and public: nothing is stored or asked. Thin: validate -> service -> answer. Rate-limited per IP.
"""
from __future__ import annotations

from flask import request

from src.api import api_bp
from src.core.responses import success_response
from src.shared.rate_limit.limiter import limiter

from ..constants import READ_LIMIT
from ..schemas.map_schemas import MapQuerySchema, load, query
from ..services import map_service as service


@api_bp.get("/universities/<university_id>/map")
@limiter.limit(READ_LIMIT)
def get_campus_map(university_id: str):
    filters = load(MapQuerySchema(), query(request.args))
    return success_response(service.university_map(university_id, filters.get("campus")))
