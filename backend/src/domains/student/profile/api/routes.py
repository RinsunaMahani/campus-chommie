"""
/api/v1/me/profile -- the signed-in student's university and campus.

  GET /me/profile    {profile: {university, university_name, campus, campus_name, confirmed_18_or_older_at, consents}}
  PUT /me/profile    {university, campus} -> {profile}

Thin: validate -> service -> answer. Rate-limited per student.
"""
from __future__ import annotations

from flask import request

from src.api import api_bp
from src.core.decorators import auth_required, current_user
from src.core.responses import success_response
from src.shared.rate_limit.keys import per_user
from src.shared.rate_limit.limiter import limiter

from ..constants import CHANGE_LIMIT, READ_LIMIT
from ..schemas.profile_schemas import ProfileSchema, load
from ..services import profile_service as service

BASE = "/me/profile"


@api_bp.get(BASE)
@limiter.limit(READ_LIMIT, key_func=per_user)
@auth_required
def my_profile():
    return success_response({"profile": service.view(current_user())})


@api_bp.put(BASE)
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def update_my_profile():
    body = load(ProfileSchema(), request.get_json(silent=True))
    return success_response({"profile": service.update(current_user(), body["university"], body["campus"])})
