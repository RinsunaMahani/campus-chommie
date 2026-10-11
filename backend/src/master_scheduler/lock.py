"""
One scheduler for the whole deployment. Every web process runs create_app
(each gunicorn worker, each container), and each would start its own
scheduler, running every job several times. So a process starts it only
while it holds a PostgreSQL advisory lock, on a connection it keeps for as
long as it lives: one holder at a time. When that process ends, its
connection closes, the lock goes with it, and the next process to start
takes over.

Needs a direct (session) connection: a pooler in transaction mode, such as
some managed databases' port 6543, can't hold a session lock (DEPLOY.md).
"""
from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.engine import Connection, Engine

#: Any fixed number: only this app takes this advisory lock.
LOCK_KEY = 2026_10_23


def hold(engine: Engine) -> Connection | None:
    """The lock, on a connection the caller keeps (and later hands to release()); None if another
    process holds it."""
    conn = engine.connect()
    try:
        held = conn.execute(text("SELECT pg_try_advisory_lock(:key)"), {"key": LOCK_KEY}).scalar()
        conn.commit()  # end the transaction: the lock belongs to the session, not to it
    except Exception:
        conn.close()
        raise
    if held:
        return conn
    conn.close()
    return None


def release(conn: Connection) -> None:
    try:
        conn.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": LOCK_KEY})
        conn.commit()
    finally:
        conn.close()
