"""
Application startup hook. Starts the Master Scheduler exactly once.

Three things this guards against:
  1. Calling start() twice in the same process (accidental double-init).
  2. Flask's debug-mode reloader, which runs the app in TWO processes --
     without the guard below, both would start their own scheduler,
     silently double-executing every job.
  3. Several web processes (gunicorn workers, containers): only the one
     holding the database lock (lock.py) runs the jobs.
"""

from __future__ import annotations

import logging
import os

from flask import Flask
from sqlalchemy.engine import Connection

from src.extensions import db
from src.master_scheduler import lock
from src.master_scheduler.engine import APSchedulerEngine
from src.master_scheduler.interfaces import SchedulerEngine
from src.master_scheduler.registry import register_all

logger = logging.getLogger(__name__)

_engine: SchedulerEngine | None = None
_lock: Connection | None = None


def start(app: Flask) -> None:
    """
    Call once, from create_app(), AFTER db.init_app(app) and after all
    domain modules are otherwise importable -- right before `return app`.
    """
    global _engine, _lock

    if not _should_start_in_this_process(app):
        logger.info("master scheduler: skipping start in reloader watcher process")
        return

    if _engine is not None:
        logger.warning("master scheduler: start() called but already running -- ignoring")
        return

    with app.app_context():
        held = lock.hold(db.engine)
    if held is None:
        logger.info("master scheduler: another process runs the jobs; not starting one here")
        return
    _lock = held

    # security.schedulers.monitor self-registers as a runner listener on
    # import -- imported here, not at this module's top level, so
    # Security only gets wired in at the moment the scheduler actually
    # starts, matching the same reasoning as before this file moved.
    # A security monitor can subscribe to job outcomes here later
    # (runner.add_listener). None is wired in yet.

    _engine = APSchedulerEngine()
    register_all(_engine, context_factory=lambda: app.app_context())
    _engine.start()
    logger.info("master scheduler: started")


def stop() -> None:
    global _engine, _lock
    if _engine is not None:
        _engine.stop()
        _engine = None
    if _lock is not None:
        lock.release(_lock)
        _lock = None


def is_running() -> bool:
    return _engine is not None and _engine.is_running


def _should_start_in_this_process(app: Flask) -> bool:
    return (not app.debug) or os.environ.get("WERKZEUG_RUN_MAIN") == "true"
