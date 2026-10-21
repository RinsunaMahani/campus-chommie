"""
Test setup: the real PostgreSQL test database (POSTGRES_TEST_DB), migrated
to the latest version once per run, with the identity tables emptied
before every test that uses the app, so tests never depend on each other.

Tests that never touch the app (the engine, the architecture rules) don't
start it, so they run without a database at all.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from src import create_app  # noqa: E402
from src.extensions import db  # noqa: E402
from src.shared.cache import cache as cache_module  # noqa: E402
from src.shared.email.email import get_fake_provider  # noqa: E402
from src.shared.queue.queue import wait_until_idle  # noqa: E402
from src.shared.rate_limit.limiter import limiter  # noqa: E402

# Emptied with CASCADE, which also empties every table that points at a
# user (notifications, ...).
IDENTITY_TABLES = ["google_identities", "sessions", "trusted_phones", "devices", "email_codes", "password_resets", "password_credentials", "consents", "users"]


@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    with app.app_context():
        from flask_migrate import upgrade

        upgrade()
    return app


@pytest.fixture(autouse=True)
def clean(request):
    if "app" not in request.fixturenames:
        yield  # no app, no database: nothing to clean
        return
    app = request.getfixturevalue("app")
    # Alerts are written by the background queue: let the last test's finish
    # before its tables are emptied (a TRUNCATE waiting on a half-done job hangs).
    wait_until_idle(timeout=30)
    with app.app_context():
        db.session.execute(text("TRUNCATE " + ", ".join(f"identity.{t}" for t in IDENTITY_TABLES) + " CASCADE"))
        db.session.commit()
    get_fake_provider().clear()
    # Per-address email limits live in memory for the whole run; each test
    # starts with fresh counters (the limit itself is tested separately).
    cache_module.cache.clear()
    # Limits off by default; tests/domains/identity/test_rate_limits.py turns them on.
    limiter.enabled = False
    yield
    with app.app_context():
        db.session.remove()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def outbox(app):
    return get_fake_provider().sent_emails
