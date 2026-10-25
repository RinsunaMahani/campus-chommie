"""
OWASP A09: the hourly attack watch speaks up when the last hour's failures look like an attack, stays quiet
otherwise, and its line carries counts only, never an email or an address.

audit_events is append-only and keeps every other test's rows, so each test moves the job's clock back to an hour of
its own, years ago (rows dated later would show up in other tests' "since now" reads), and writes that hour's rows.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

from src.domains.security.audit.constants import WATCH_ALL_KINDS, WATCH_ONE_KIND
from src.domains.security.audit.jobs import attack_watch
from src.domains.security.audit.repositories import audit_repository


def _an_hour_of_our_own(monkeypatch) -> datetime:
    now = datetime.now(timezone.utc) - timedelta(days=random.randint(400, 30000))
    monkeypatch.setattr(attack_watch, "utcnow", lambda: now)
    return now


def _warnings(monkeypatch) -> list[str]:
    said: list[str] = []
    monkeypatch.setattr(attack_watch.logger, "warning", lambda msg, *args: said.append(msg % args))
    return said


def _failures(now: datetime, name: str, n: int, ips: int = 1) -> None:
    for i in range(n):
        audit_repository.insert({
            "timestamp": now - timedelta(minutes=30), "domain": "auth", "event_name": name, "status": "failure",
            "actor_type": "user", "email": f"victim{i}@example.test", "ip_address": f"203.0.113.{i % ips}",
            "metadata": {},
        })


def test_a_password_guessing_burst_raises_one_alert_with_counts_only(app, monkeypatch):
    said = _warnings(monkeypatch)
    with app.app_context():
        now = _an_hour_of_our_own(monkeypatch)
        _failures(now, "auth.login_failed", WATCH_ONE_KIND, ips=7)
        result = attack_watch.run()
    assert result.success and result.count == 1
    [line] = said
    assert line.startswith("security_alert ")
    assert f"failures={WATCH_ONE_KIND}" in line and "sources=7" in line and f"auth.login_failed={WATCH_ONE_KIND}" in line
    assert "@" not in line and "203.0.113" not in line


def test_many_small_kinds_together_also_raise_it(app, monkeypatch):
    said = _warnings(monkeypatch)
    with app.app_context():
        now = _an_hour_of_our_own(monkeypatch)
        per_kind = WATCH_ONE_KIND - 1
        kinds = -(-WATCH_ALL_KINDS // per_kind)
        for k in range(kinds):
            _failures(now, f"auth.kind_{k}_failed", per_kind)
        assert attack_watch.run().count == 1
    assert len(said) == 1


def test_an_ordinary_hour_stays_quiet(app, monkeypatch):
    said = _warnings(monkeypatch)
    with app.app_context():
        now = _an_hour_of_our_own(monkeypatch)
        _failures(now, "auth.login_failed", 5)
        _failures(now - timedelta(hours=2), "auth.login_failed", WATCH_ONE_KIND)  # an older burst is not this hour's
        result = attack_watch.run()
    assert result.success and result.count == 0 and "5 failed events" in result.detail
    assert said == []


def test_the_watch_is_registered_with_the_scheduler():
    from src.master_scheduler.registry import ALL_JOB_SPECS

    assert "security_attack_watch" in {s.name for s in ALL_JOB_SPECS}
