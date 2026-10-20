"""
The /api/v1 blueprint. Platform-level routes (health) live here; each
domain registers its own routes on this blueprint from its api/ package.
"""
from __future__ import annotations

from flask import Blueprint
from sqlalchemy import text

from src.core.responses import error_response, success_response
from src.extensions import db
from src.shared.rate_limit.limiter import limiter

api_bp = Blueprint("api", __name__)

#: Per IP. Uptime monitors and the app's start-up check stay far below it.
HEALTH_LIMIT = "120 per minute"


@api_bp.get("/health")
@limiter.limit(HEALTH_LIMIT)
def health():
    """Public. Reports whether the API and the database answer; used by
    the app on start-up and by monitoring."""
    try:
        db.session.execute(text("SELECT 1"))
        return success_response({"status": "ok", "database": "ok"}, message="Campus Chommie API is healthy")
    except Exception:  # noqa: BLE001
        return error_response(message="Database unavailable", status_code=503, code="DB_UNAVAILABLE")


@api_bp.get("/ping")
@limiter.limit(HEALTH_LIMIT)
def ping():
    """Public. Answers without touching the database: for an uptime pinger
    that keeps a free host awake, and the container's own check. Pinging
    /health instead would keep a free database awake all month and use up
    its compute hours."""
    return success_response({"status": "ok"}, message="Campus Chommie API is up")


# Each feature's routes attach to api_bp by being imported here.
from src.domains.catalogue.colleges.api import routes as _colleges_routes  # noqa: E402,F401
from src.domains.catalogue.funding.api import routes as _funding_routes  # noqa: E402,F401
from src.domains.catalogue.maps.api import routes as _maps_routes  # noqa: E402,F401
from src.domains.catalogue.universities.api import routes as _universities_routes  # noqa: E402,F401
from src.domains.classes.classes.api import routes as _classes_routes  # noqa: E402,F401
from src.domains.classes.events.api import routes as _events_routes  # noqa: E402,F401
from src.domains.identity.accounts.api import routes as _accounts_routes  # noqa: E402,F401
from src.domains.identity.auth.api import routes as _auth_routes  # noqa: E402,F401
from src.domains.pathways.course_finder.api import routes as _course_finder_routes  # noqa: E402,F401
from src.domains.platform.notifications.api import routes as _notifications_routes  # noqa: E402,F401
from src.domains.student.academics.api import routes as _academics_routes  # noqa: E402,F401
from src.domains.student.alerts.api import routes as _alerts_routes  # noqa: E402,F401
from src.domains.student.money.api import routes as _money_routes  # noqa: E402,F401
from src.domains.student.profile.api import routes as _profile_routes  # noqa: E402,F401
from src.domains.student.saved_funding.api import routes as _saved_funding_routes  # noqa: E402,F401
from src.domains.student.timetable.api import routes as _timetable_routes  # noqa: E402,F401
