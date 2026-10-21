"""
/api/v1/me -- the signed-in user's own account.

No user id in the URL: the account comes from the token, so there is no
id to swap for someone else's (no IDOR by construction).
"""
from __future__ import annotations

from src.api import api_bp
from src.core.decorators import auth_required, current_user
from src.core.responses import success_response
from src.shared.rate_limit.keys import per_user
from src.shared.rate_limit.limiter import limiter

from ..services import account_service

#: Every route has a limit; this one is per user and never met by a real person.
ME_LIMIT = "120 per minute"


@api_bp.get("/me")
@limiter.limit(ME_LIMIT, key_func=per_user)
@auth_required
def me():
    return success_response(account_service.public_view(current_user()))
