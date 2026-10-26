"""
The demo accounts for the judges: `flask seed` makes three fictional students
through the real services (short money and a heavy week ahead; a heavy week
now; a class rep with a classmate's message waiting), and a daily job
re-bases them so their dates stay current. Signing in skips the new-phone
code (judges can't read the demo inbox), wrong passwords never lock them,
and nobody can change, reset or close them. A real account is never turned
into a demo one.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from demo_helpers import CONSENT, EMAILS, PASSWORD, TODAY, fresh_password, on_day, seed, sign_in, student

from src.domains.classes.classes.models import ModuleClass
from src.domains.identity.accounts.models import Consent, User
from src.domains.identity.auth.rate_limit import policies
from src.domains.platform.demo.jobs import rebase_demo
from src.shared.rate_limit.limiter import limiter
from src.domains.platform.demo.models import DemoAccount
from src.domains.platform.demo.services import demo_service

API = "/api/v1"
SAST = ZoneInfo("Africa/Johannesburg")


@pytest.fixture(autouse=True)
def on_12_october(monkeypatch):
    on_day(monkeypatch, TODAY)


@pytest.fixture
def password():
    return fresh_password()


@pytest.fixture
def seeded(app, password):
    seed(app, password)
    return password


def get(client, headers, path, **query):
    r = client.get(f"{API}{path}", headers=headers, query_string=query)
    assert r.status_code == 200, r.get_json()
    return r.get_json()["data"]


# ------------------------------------------------------------------- seed


def test_the_seed_makes_three_fictional_students(app, seeded):
    with app.app_context():
        users = User.query.filter(User.email.in_(EMAILS.values())).all()
        assert len(users) == 3 and all(u.is_demo and u.is_active and u.email_verified_at for u in users)
        assert sorted(a.persona for a in DemoAccount.query) == ["naledi", "sipho", "thabo"]
        assert all(a.rebased_on == TODAY for a in DemoAccount.query)
        consents = Consent.query.filter(Consent.user_id.in_([u.id for u in users])).all()
        assert len(consents) == 9 and all("demo account" in c.user_agent for c in consents)


def test_the_seed_needs_a_strong_password_and_never_echoes_it(app, monkeypatch):
    with app.app_context(), pytest.raises(demo_service.DemoPasswordError):
        demo_service.seed("password")
    runner = app.test_cli_runner()
    monkeypatch.delenv("DEMO_PASSWORD", raising=False)
    result = runner.invoke(args=["seed"])
    assert result.exit_code != 0 and "DEMO_PASSWORD" in result.output
    password = fresh_password()
    monkeypatch.setenv("DEMO_PASSWORD", password)
    result = runner.invoke(args=["seed"])
    assert result.exit_code == 0, result.output
    assert EMAILS["naledi"] in result.output and password not in result.output


def test_seeding_twice_changes_nothing_but_the_password(app, client, seeded):
    newer = fresh_password()
    seed(app, newer)
    with app.app_context():
        assert User.query.filter(User.email.in_(EMAILS.values())).count() == 3
    assert client.post(f"{API}/auth/login", json={"email": EMAILS["sipho"], "password": seeded}).status_code == 401
    sign_in(client, "sipho", newer)


def test_the_server_starting_builds_data_only_for_a_new_account(app, seeded):
    """flask start-up seeds with rebuild=False: existing data waits for the scheduler's re-base, so the server
    answers sooner; a brand-new account still gets its data straight away."""
    calls = []
    real = demo_service.rebase
    with app.app_context():
        demo_service.rebase = lambda today: calls.append(today) or real(today)
        try:
            demo_service.seed(seeded, today=TODAY + timedelta(days=1), rebuild=False)
            assert calls == []  # already built: left to the scheduler
            assert all(a.rebased_on == TODAY for a in DemoAccount.query)
            DemoAccount.query.filter_by(persona="sipho").one().rebased_on = None  # as if just made
            demo_service.seed(seeded, today=TODAY, rebuild=False)
            assert calls == [TODAY]
        finally:
            demo_service.rebase = real


def test_a_real_account_is_never_turned_into_a_demo_one(app, client, outbox, password):
    client.post(f"{API}/auth/register", json={"email": EMAILS["naledi"], "password": PASSWORD, "consent": CONSENT})
    with app.app_context(), pytest.raises(ValueError, match="real account"):
        demo_service.seed(password)
    with app.app_context():
        assert not User.query.filter_by(email=EMAILS["naledi"]).one().is_demo


# ---------------------------------------------------------------- sign in


def test_demo_accounts_skip_the_new_phone_code_and_say_they_are_demo(client, outbox, seeded):
    headers = sign_in(client, "naledi", seeded)  # 200 straight away: no code to read from an inbox
    assert outbox == []
    me = get(client, headers, "/me")
    assert me["demo"] is True and me["email"] == EMAILS["naledi"]


def test_a_real_account_still_needs_the_code(client, outbox, seeded):
    who = student(client, outbox, "lerato@example.com")
    assert get(client, who.headers, "/me")["demo"] is False
    r = client.post(f"{API}/auth/login", json={"email": "lerato@example.com", "password": PASSWORD})
    assert r.status_code == 202 and r.get_json()["data"]["code_required"] is True


def test_wrong_passwords_never_lock_a_demo_account(client, seeded):
    for _ in range(8):
        r = client.post(f"{API}/auth/login", json={"email": EMAILS["thabo"], "password": "Wrong-pass-1!"})
        assert r.status_code == 401
    sign_in(client, "thabo", seeded)  # the judges are never locked out


def test_nobody_can_change_reset_or_close_a_demo_account(client, outbox, seeded):
    headers = sign_in(client, "sipho", seeded)
    r = client.post(f"{API}/auth/change-password", json={"current_password": seeded, "new_password": fresh_password()},
                    headers=headers)
    assert r.status_code == 403 and r.get_json()["code"] == "DEMO_ACCOUNT"
    r = client.post(f"{API}/me/close-account", json={"password": seeded}, headers=headers)
    assert r.status_code == 403 and r.get_json()["code"] == "DEMO_ACCOUNT"
    r = client.post(f"{API}/auth/forgot-password", json={"email": EMAILS["sipho"]})
    assert r.status_code == 202 and outbox == []  # the same answer as for anyone, and no email
    sign_in(client, "sipho", seeded)


def test_demo_sign_ins_have_their_own_limit(app, seeded):
    """A demo account can't be locked, so its stricter per-IP limit applies to demo emails only."""
    for email, exempt in ((EMAILS["naledi"], False), ("lerato@example.com", True), ("", True)):
        with app.test_request_context(json={"email": email}):
            assert policies.not_a_demo_login() is exempt
    assert policies.DEMO_LOGIN == "20 per hour"


@pytest.fixture
def limits_on(app):
    was = limiter.enabled
    limiter.enabled = True
    with app.app_context():
        limiter.reset()
    yield
    with app.app_context():
        limiter.reset()
    limiter.enabled = was


def test_judges_can_sign_in_as_often_as_they_need(client, seeded, limits_on):
    """From one address, right passwords never run out (only DEMO_SIGN_INS' flood guard); wrong ones still do."""
    for _ in range(25):  # more than LOGIN's 5 a minute and DEMO_LOGIN's 20 an hour
        r = client.post(f"{API}/auth/login", json={"email": EMAILS["naledi"], "password": seeded})
        assert r.status_code == 200, r.get_json()
    wrong = [client.post(f"{API}/auth/login", json={"email": EMAILS["naledi"], "password": "Wrong-2026!"}).status_code
             for _ in range(21)]
    assert wrong[:20] == [401] * 20 and wrong[20] == 429
    r = client.post(f"{API}/auth/login", json={"email": "lerato@example.com", "password": "Wrong-2026!"})
    assert r.status_code == 401  # anyone else's limits are their own


# ------------------------------------------------------------------- data


def test_the_personas_are_built_as_written(client, seeded):
    naledi = sign_in(client, "naledi", seeded)
    money = get(client, naledi, "/money/summary")
    assert money["balance"]["cents"] == 61000
    assert money["runway"]["runs_out_on"] == "2026-10-24" and money["life_fund"]["state"] == "paused"
    week = get(client, naledi, "/week")["weeks"]
    assert [w["load"] for w in week[:2]] == ["Manageable", "Heavy"]
    assert [m["code"] for m in get(client, naledi, "/academics/modules")["modules"]] == ["ANA201", "PHY121"]
    classes = get(client, naledi, "/classes/mine")["classes"]
    assert sorted(c["module_code"] for c in classes) == ["ANA201", "BCH111", "PHY121"]
    assert {c["role"] for c in classes} == {"student"}

    sipho = sign_in(client, "sipho", seeded)
    summary = get(client, sipho, "/money/summary")
    assert summary["life_fund"]["state"] == "amber" and summary["this_week"]["colour"] == "red"
    assert {c["role"] for c in get(client, sipho, "/classes/mine")["classes"]} == {"rep"}

    thabo = sign_in(client, "thabo", seeded)
    classes = get(client, thabo, "/classes/mine")["classes"]
    assert {c["role"] for c in classes} == {"rep"} and len(classes) == 3
    bch = next(c for c in classes if c["module_code"] == "BCH111")
    waiting = get(client, thabo, f"/classes/{bch['id']}/candidates")["candidates"]
    assert len(waiting) == 1 and waiting[0]["from_rep"] is False and waiting[0]["confirmable"] is True
    assert waiting[0]["read_as"]["on"] == "2026-10-16"  # "Friday", from the day it was sent


def test_a_rebase_moves_every_date_and_undoes_what_visitors_changed(app, client, seeded, monkeypatch):
    naledi = sign_in(client, "naledi", seeded)
    client.put(f"{API}/money/settings", json={"balance_cents": 1, "balance_on": "2026-10-12", "essentials_per_day_cents": 1},
               headers=naledi)
    assert client.put(f"{API}/me/funding/nsfas", headers=naledi).status_code == 200
    thabo = sign_in(client, "thabo", seeded)
    extra = client.post(f"{API}/classes", json={"university": "smu", "campus": "ga_rankuwa", "module_code": "CHE101",
                                                "year": 2026}, headers=thabo).get_json()["data"]["class"]

    later = TODAY + timedelta(days=3)
    on_day(monkeypatch, later)
    with app.app_context():
        assert demo_service.due(later) is True
        assert demo_service.rebase(later) == 3
        assert demo_service.due(later) is False
        assert ModuleClass.query.filter_by(id=uuid.UUID(extra["id"])).first() is None  # what a visitor made is gone

    money = get(client, naledi, "/money/summary")
    assert money["balance"]["cents"] == 61000 and money["balance"]["entered_on"] == "2026-10-15"
    assert money["next_payment"]["expected_on"] == "2026-11-02"  # 30 Oct, three days on
    assert money["runway"]["runs_out_on"] == "2026-10-27"
    events = [e for w in get(client, naledi, "/week")["weeks"] for e in w["events"]]
    assert events[0]["title"] == "Quiz 3" and events[0]["on"] == "2026-10-17"
    assert get(client, naledi, "/me/funding")["funders"] == []  # what a visitor saved is gone


def test_a_real_students_class_survives_a_rebase(app, client, outbox, seeded):
    lerato = student(client, outbox, "lerato@example.com")
    made = client.post(f"{API}/classes", json={"university": "smu", "campus": "ga_rankuwa", "module_code": "ANA201",
                                               "year": 2026}, headers=lerato.headers).get_json()["data"]["class"]
    naledi = sign_in(client, "naledi", seeded)
    assert client.post(f"{API}/classes/join", json={"code": made["invite_code"]}, headers=naledi).status_code == 200
    with app.app_context():
        demo_service.rebase(TODAY)
    mine = get(client, lerato.headers, "/classes/mine")["classes"]
    assert [(c["id"], c["members"]) for c in mine] == [(made["id"], 1)]  # Naledi left; Lerato's class stays


# --------------------------------------------------------------------- job


@pytest.mark.parametrize(
    "now, rebased",
    [
        (datetime(2026, 10, 13, 1, 30, tzinfo=SAST), False),  # before 02:00 SAST
        (datetime(2026, 10, 13, 2, 5, tzinfo=SAST), True),
    ],
)
def test_the_job_rebases_once_a_day_from_two(app, seeded, monkeypatch, now, rebased):
    on_day(monkeypatch, now.date())
    monkeypatch.setattr(rebase_demo, "_now", lambda: now)
    with app.app_context():
        result = rebase_demo.run()
        assert result.success and result.count == (3 if rebased else 0)
        assert {a.rebased_on for a in DemoAccount.query} == {now.date() if rebased else TODAY}
        again = rebase_demo.run()
        assert again.success and again.count == 0  # once a day


def test_the_job_does_nothing_without_demo_accounts(app, monkeypatch):
    monkeypatch.setattr(rebase_demo, "_now", lambda: datetime(2026, 10, 13, 3, 0, tzinfo=SAST))
    with app.app_context():
        result = rebase_demo.run()
        assert result.success and result.count == 0


def test_the_personas_file_is_fictional_and_safe():
    data = demo_service.personas()
    assert isinstance(data["today"], date)
    for p in data["personas"]:
        assert p["email"].endswith("@example.com")  # reserved: never a real inbox
        assert "password" not in str(p).lower()
