"""
Application factory. create_app() builds the app: config, extensions,
blueprints, one error handler for every AppError, and the CLI.
(Pattern reused from TruConnect; see REUSE.md.)
"""
from __future__ import annotations

import logging
import os

import click
from flask import Flask

from src.config import get_config
from src.extensions import bcrypt, db, jwt, ma, migrate

#: Deeper JSON than this is refused (400) before any route sees it.
MAX_JSON_DEPTH = 32


def create_app(env_name: str | None = None) -> Flask:
    # Before anything else logs: the scheduler's start-up lines included.
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    app = Flask(__name__)
    app.config.from_object(get_config(env_name))

    _register_extensions(app)
    _register_models()
    _register_blueprints(app)
    _register_listeners(app)
    _register_error_handlers(app)
    _register_input_guard(app)
    _register_security_headers(app)
    _register_cli(app)

    # Background jobs (identity clean-up, idempotency sweep). Not in tests, and not in a one-off command.
    if app.config.get("SCHEDULER_ENABLED") and not _one_off_command():
        from src.master_scheduler import trigger

        trigger.start(app)

    # The config actually in use (FLASK_ENV when no env_name is passed), not the argument.
    app.logger.info("Campus Chommie backend ready (env=%s)", app.config.get("ENV_NAME"))
    return app


def _one_off_command() -> bool:
    """`flask db upgrade`, `flask seed` and the like do one thing and stop, so they never run the
    scheduled jobs: a migration must never race a job, even on a host's very first start. `flask run`
    (a development server) does run them. Flask's command line sets FLASK_RUN_FROM_CLI for every command."""
    if os.environ.get("FLASK_RUN_FROM_CLI") != "true":
        return False
    ctx = click.get_current_context(silent=True)
    return ctx is None or ctx.info_name != "run"


def _register_extensions(app: Flask) -> None:
    from src.shared.rate_limit import responses as rate_limit_responses
    from src.shared.rate_limit.limiter import limiter

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    from src.domains.identity.auth.services import jwt_callbacks

    jwt_callbacks.register(jwt)
    ma.init_app(app)
    bcrypt.init_app(app)
    limiter.init_app(app)
    rate_limit_responses.register(app)

    # Only where configured (development's web preview); never in production.
    if app.config.get("CORS_ORIGINS"):
        from flask_cors import CORS

        CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}}, supports_credentials=False)


def _register_models() -> None:
    """Import every feature's models so they're in SQLAlchemy's metadata
    (migrations and tests need them). Explicit on purpose: a clever scan
    would hide which tables exist. Add one line per feature as its tables
    are built, e.g.:
        from src.domains.identity.accounts import models  # noqa: F401
    """
    # Infrastructure (platform schema)
    from src.shared.idempotency import models  # noqa: F401
    # identity schema: accounts, auth, devices
    from src.domains.identity.accounts import models as _accounts  # noqa: F401
    from src.domains.identity.auth import models as _auth  # noqa: F401
    from src.domains.identity.devices import models as _devices  # noqa: F401
    # platform schema: every user's alerts and their switches
    from src.domains.platform.notifications import models as _notifications  # noqa: F401
    # audit schema: the append-only audit trail
    from src.domains.security.audit import models as _audit  # noqa: F401
    # platform schema: which account plays which demo persona
    from src.domains.platform.demo import models as _demo  # noqa: F401
    # student schema: a student's own profile, money and marks (owner-only)
    from src.domains.student.academics import models as _academics  # noqa: F401
    from src.domains.student.money import models as _money  # noqa: F401
    from src.domains.student.profile import models as _profile  # noqa: F401
    from src.domains.student.saved_funding import models as _saved_funding  # noqa: F401
    from src.domains.student.timetable import models as _timetable  # noqa: F401
    # classes schema: classes, members, reps, announcements and verified events
    from src.domains.classes.classes import models as _classes  # noqa: F401
    from src.domains.classes.events import models as _events  # noqa: F401


def _register_listeners(app: Flask) -> None:
    """Subscribers to shared events: the audit trail stores every audit event."""
    from src.domains.security.audit.services import audit_service
    from src.shared.rate_limit import responses as rate_limit_responses
    from src.domains.identity.auth.rate_limit.policies import RATE_LIMIT_AUDIT_EVENTS

    audit_service.register(app)
    # Alerts published anywhere are kept by the notifications feature.
    from src.domains.platform.notifications.services import notification_service

    notification_service.register(app)
    rate_limit_responses.register_audit_events(RATE_LIMIT_AUDIT_EVENTS)
    _register_exporters()
    _register_daily_checks()


def _register_exporters() -> None:
    """What each feature holds about a person, for GET /me/export (POPIA). Add one line per feature
    that stores personal data; identity's own part is added by its export."""
    from src.domains.classes.classes.services import class_service
    from src.domains.classes.events.services import events_service
    from src.domains.platform.notifications.services import notification_service
    from src.domains.student.academics.services import academics_service
    from src.domains.student.money.services import money_service
    from src.domains.student.profile.services import profile_service
    from src.domains.student.saved_funding.services import saved_funding_service
    from src.domains.student.timetable.services import timetable_service
    from src.shared.privacy import privacy

    privacy.register_exporter("profile", profile_service.export_for)
    privacy.register_exporter("money", money_service.export_for)
    privacy.register_exporter("marks", academics_service.export_for)
    privacy.register_exporter("classes", class_service.export_for)
    privacy.register_exporter("class_messages", events_service.export_for)
    privacy.register_exporter("alerts", notification_service.export_for)
    privacy.register_exporter("alert_switches", notification_service.export_switches)
    privacy.register_exporter("saved_funding", saved_funding_service.export_for)
    privacy.register_exporter("timetable", timetable_service.export_for)


def _register_daily_checks() -> None:
    """Checks that may publish alerts on a student's first poll of the day (shared.notifications)."""
    from src.domains.student.saved_funding.services import saved_funding_service
    from src.shared.notifications import notifications as shared_notifications

    shared_notifications.register_daily(saved_funding_service.daily_reminders)


def _register_blueprints(app: Flask) -> None:
    from src.api import api_bp

    app.register_blueprint(api_bp, url_prefix="/api/v1")
    # The page the reset email's button opens (outside /api/v1: it must match the emailed URL).
    from src.domains.identity.auth.api.reset_page import reset_page_bp

    app.register_blueprint(reset_page_bp)


def _register_error_handlers(app: Flask) -> None:
    from src.core.exceptions import AppError
    from src.core.responses import error_response

    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        return error_response(
            message=error.message,
            errors=error.errors,
            status_code=error.status_code,
            code=error.code,
            data=error.data,
        )

    @app.errorhandler(413)
    def handle_too_large(_error):
        return error_response(message="That request is too large.", status_code=413, code="PAYLOAD_TOO_LARGE")

    @app.errorhandler(404)
    def handle_not_found(_error):
        return error_response(message="Resource not found", status_code=404, code="NOT_FOUND")

    @app.errorhandler(405)
    def handle_method_not_allowed(_error):
        return error_response(message="Method not allowed", status_code=405, code="METHOD_NOT_ALLOWED")

    @app.errorhandler(500)
    def handle_internal_error(error):
        app.logger.exception("Unhandled server error: %s", error)
        return error_response(message="Internal server error", status_code=500, code="INTERNAL_ERROR")


def _register_input_guard(app: Flask) -> None:
    """Refuse any request carrying the NUL character anywhere (JSON, form,
    query). PostgreSQL can't store it and no human types it; it only
    arrives in attacks and broken clients. Fields also clean their own text
    (shared/validation/text.py); this is the net under them."""
    from flask import request

    from src.core.responses import error_response

    class _TooDeep(Exception):
        pass

    def _has_nul(value) -> bool:
        """Walks the JSON with its own stack, not recursion: a body nested
        thousands deep can't overflow Python's stack (found by Risuna's
        hostile-input tests). No request of ours nests past a few levels."""
        stack = [(value, 0)]
        while stack:
            item, depth = stack.pop()
            if depth > MAX_JSON_DEPTH:
                raise _TooDeep()
            if isinstance(item, str):
                if "\x00" in item:
                    return True
            elif isinstance(item, dict):
                stack.extend((k, depth + 1) for k in item.keys())
                stack.extend((v, depth + 1) for v in item.values())
            elif isinstance(item, list):
                stack.extend((v, depth + 1) for v in item)
        return False

    @app.before_request
    def _refuse_nul():
        try:
            found = any(_has_nul(v) for v in request.args.values()) or any(_has_nul(v) for v in request.form.values())
            if not found and request.is_json:
                found = _has_nul(request.get_json(silent=True))
        except (_TooDeep, RecursionError):  # RecursionError: the JSON parser itself gave up
            return error_response(message="The request isn't in a shape we accept.", status_code=400, code="INVALID_BODY")
        if found:
            return error_response(message="The request contains characters we don't accept.", status_code=400, code="INVALID_CHARACTERS")


def _register_security_headers(app: Flask) -> None:
    """Headers on every response. The API returns JSON with tokens and
    personal data: nothing may be cached, sniffed as another type, or framed. In production (always behind
    https) browsers are also told to use https only, for a year (HSTS)."""

    @app.after_request
    def _headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
        # JSON loads nothing: a browser shown an API reply runs no script and frames nothing. A page that is HTML
        # (the password reset page) sets its own, narrower policy first.
        response.headers.setdefault("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'; base-uri 'none'")
        # No camera, microphone or location for anything we serve; no other window can reach ours (ZAP, 21 Oct 2026).
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=()"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        response.headers.pop("Server", None)
        if app.config.get("HSTS"):
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


def _register_cli(app: Flask) -> None:
    from src.cli import register_cli

    register_cli(app)
