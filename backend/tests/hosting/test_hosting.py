"""
The backend ready for any host. One scheduler for the whole deployment
(a database lock), never in a one-off command such as a migration, with the
demo's re-base also running as it starts. gunicorn as one process with
threads, logging no IP address and no query string. A container that runs
as a normal user and keeps secrets out of the image. Browsers allowed in
production only from named https addresses.
"""
from __future__ import annotations

import runpy
from datetime import UTC, datetime, timedelta
from pathlib import Path

import click
import pytest

from src import _one_off_command
from src.config import get_config
from src.extensions import db
from src.master_scheduler import lock, trigger
from src.master_scheduler.engine import APSchedulerEngine
from src.master_scheduler.registry import ALL_JOB_SPECS

BACKEND = Path(__file__).resolve().parents[2]


# --------------------------------------------------------------- scheduler


def test_only_one_process_holds_the_scheduler_lock(app):
    with app.app_context():
        first = lock.hold(db.engine)
        assert first is not None
        assert lock.hold(db.engine) is None  # a second process is turned away
        lock.release(first)
        again = lock.hold(db.engine)  # and once it's free, the next takes it
        assert again is not None
        lock.release(again)


def test_the_scheduler_starts_only_with_the_lock(app, monkeypatch):
    monkeypatch.setattr(trigger, "register_all", lambda engine, context_factory=None: None)  # no real jobs here
    with app.app_context():
        held_elsewhere = lock.hold(db.engine)
    try:
        trigger.start(app)
        assert not trigger.is_running()
    finally:
        lock.release(held_elsewhere)
    trigger.start(app)
    try:
        assert trigger.is_running()
        with app.app_context():
            assert lock.hold(db.engine) is None  # this process holds it now
    finally:
        trigger.stop()
    with app.app_context():
        freed = lock.hold(db.engine)  # stopping gave it back
        assert freed is not None
        lock.release(freed)


def test_a_job_can_also_run_as_the_scheduler_starts():
    engine = APSchedulerEngine()
    engine.add_job("at_start", lambda: None, 3600, run_at_start=True)
    engine.add_job("later", lambda: None, 3600)
    engine._scheduler.start(paused=True)
    try:
        now = datetime.now(UTC)
        assert engine._scheduler.get_job("at_start").next_run_time <= now + timedelta(seconds=5)
        assert engine._scheduler.get_job("later").next_run_time >= now + timedelta(minutes=59)
    finally:
        engine._scheduler.shutdown(wait=False)


def test_the_demo_rebase_runs_as_a_sleeping_server_wakes():
    starts = {spec.name for spec in ALL_JOB_SPECS if spec.run_at_start}
    assert starts == {"demo_rebase"}


@pytest.mark.parametrize(
    "from_cli, command, one_off",
    [
        (None, None, False),  # gunicorn or python app.py: the server
        ("true", "run", False),  # flask run: a development server
        ("true", "upgrade", True),  # flask db upgrade
        ("true", "seed", True),  # flask seed
        ("true", None, True),
    ],
)
def test_one_off_commands_never_start_the_scheduler(monkeypatch, from_cli, command, one_off):
    if from_cli is None:
        monkeypatch.delenv("FLASK_RUN_FROM_CLI", raising=False)
    else:
        monkeypatch.setenv("FLASK_RUN_FROM_CLI", from_cli)
    if command is None:
        assert _one_off_command() is one_off
    else:
        with click.Context(click.Command(command), info_name=command):
            assert _one_off_command() is one_off


# ---------------------------------------------------------------- gunicorn


def test_gunicorn_runs_one_process_and_logs_no_ip_or_query(monkeypatch):
    monkeypatch.setenv("PORT", "10000")
    conf = runpy.run_path(str(BACKEND / "gunicorn.conf.py"))
    assert conf["bind"] == "0.0.0.0:10000"
    assert (conf["workers"], conf["worker_class"]) == (1, "gthread") and conf["threads"] >= 1
    log_format = conf["access_log_format"]
    for leaky in ("%(h)s", "%(q)s", "%(r)s", "%({x-forwarded-for}i)s"):
        assert leaky not in log_format, leaky  # the client's IP, the query string, the request line with it
    assert "%(U)s" in log_format  # the path alone


# --------------------------------------------------------------- container


def test_the_container_runs_as_a_normal_user_with_a_health_check():
    dockerfile = (BACKEND / "Dockerfile").read_text(encoding="utf-8")
    lines = [line.strip() for line in dockerfile.splitlines()]
    user_lines = [line for line in lines if line.startswith("USER ")]
    assert user_lines and user_lines[-1] != "USER root"
    # Docker's check uses /ping, which never touches the database, so a free database can sleep.
    assert any(line.startswith("HEALTHCHECK") for line in lines) and "/api/v1/ping" in dockerfile
    assert "gunicorn -c gunicorn.conf.py app:app" in dockerfile and "flask db upgrade" in dockerfile
    assert "FLASK_ENV=production" in dockerfile  # production settings: they refuse weak secrets and fake email


def test_secrets_and_tests_stay_out_of_the_image():
    ignored = (BACKEND / ".dockerignore").read_text(encoding="utf-8").split()
    for path in (".env", ".env.*", ".venv", "tests", "__pycache__"):
        assert path in ignored, path
    assert "COPY .env" not in (BACKEND / "Dockerfile").read_text(encoding="utf-8")


# -------------------------------------------------------------------- CORS

PRODUCTION = {
    "SECRET_KEY": "s" * 40, "JWT_SECRET_KEY": "j" * 40, "MAIL_PROVIDER": "smtp", "MAIL_SERVER": "smtp.example.com",
    "MAIL_USERNAME": "u", "MAIL_PASSWORD": "p", "MAIL_DEFAULT_SENDER": "Campus Chommie <a@example.com>",
    "APP_BASE_URL": "https://api.example.com",
}


@pytest.mark.parametrize(
    "origins, ok",
    [
        ("", True),
        ("https://campuschommie.example.com", True),
        ("https://a.example.com, https://b.example.com", True),
        ("http://campuschommie.example.com", False),
        ("*", False),
        ("https://*.example.com", False),
    ],
)
def test_production_allows_browsers_only_from_named_https_addresses(monkeypatch, origins, ok):
    for key, value in PRODUCTION.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setenv("CORS_ORIGINS", origins)
    if ok:
        assert get_config("production") is not None
    else:
        with pytest.raises(RuntimeError, match="CORS_ORIGINS"):
            get_config("production")


# --------------------------------------------------------------- free hosts


def test_ping_answers_without_the_database(client, monkeypatch):
    def no_database(*_args, **_kwargs):
        raise AssertionError("ping touched the database")

    monkeypatch.setattr(db.session, "execute", no_database)
    r = client.get("/api/v1/ping")
    assert r.status_code == 200 and r.get_json()["data"] == {"status": "ok"}


def test_the_container_seeds_the_demo_only_when_asked():
    dockerfile = (BACKEND / "Dockerfile").read_text(encoding="utf-8")
    assert '[ \\"$SEED_DEMO_ON_START\\" != true ] || flask seed' in dockerfile
    # Migrations still come first, and the API still starts after a failed seed.
    assert dockerfile.index("flask db upgrade") < dockerfile.index("flask seed") < dockerfile.index("exec gunicorn")



# --------------------------------------------------------------- database


def test_every_connection_caps_how_long_a_statement_may_run(app):
    """A stuck query can't hold a connection (and a server thread) for ever."""
    from sqlalchemy import text
    from sqlalchemy.exc import OperationalError

    with app.app_context():
        with db.engine.connect() as conn:
            assert conn.execute(text("SHOW statement_timeout")).scalar() == "30s"
            conn.execute(text("SET statement_timeout = 200"))  # this connection only, so the test is quick
            with pytest.raises(OperationalError, match="statement timeout"):
                conn.execute(text("SELECT pg_sleep(2)"))
            conn.rollback()
            conn.execute(text("SET statement_timeout = 30000"))
