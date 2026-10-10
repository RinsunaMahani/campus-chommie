"""
Classes, invite codes and reps: a student makes a class and is its first
rep; classmates join with the invite code; a rep brings in the next rep with
a one-time code, up to 3. Nobody is ever listed: views carry counts only.
Then the hostile side: guessed and expired codes, a fourth rep, unknown
fields, someone else's class, floods, and the yearly clean-up.
"""
from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from class_helpers import CLASSES, UP_CLASS, join, make_class, student

from src.domains.classes.classes.constants import CODE_ALPHABET
from src.domains.classes.classes.jobs import forget_old_classes
from src.domains.classes.classes.models import ClassMember, ModuleClass, RepInvite
from src.domains.classes.classes.services import class_service
from src.extensions import db
from src.shared.rate_limit.limiter import limiter

TODAY = date(2026, 10, 12)


@pytest.fixture(autouse=True)
def on_12_october(monkeypatch):
    monkeypatch.setattr(class_service, "_today", lambda: TODAY)


@pytest.fixture
def rep(client, outbox):
    return student(client, outbox, "thabo@example.com")


@pytest.fixture
def classmate(client, outbox):
    return student(client, outbox, "naledi@example.com")


@pytest.fixture
def outsider(client, outbox):
    return student(client, outbox, "sipho@example.com")


def mine(client, who) -> list[dict]:
    r = client.get(f"{CLASSES}/mine", headers=who.headers)
    assert r.status_code == 200
    return r.get_json()["data"]["classes"]


def rep_code(client, who, class_id) -> str:
    r = client.post(f"{CLASSES}/{class_id}/reps", headers=who.headers)
    assert r.status_code == 201, r.get_json()
    return r.get_json()["data"]["code"]


@pytest.mark.parametrize(
    "method, path",
    [("post", ""), ("post", "/join"), ("get", "/mine"), ("post", f"/{uuid.uuid4()}/reps"), ("delete", f"/{uuid.uuid4()}/membership")],
)
def test_every_classes_route_needs_a_token(client, method, path):
    assert getattr(client, method)(f"{CLASSES}{path}", json={}).status_code == 401


def test_a_rep_makes_a_class_and_classmates_join(client, rep, classmate):
    made = make_class(client, rep, module_code="ana 201")
    assert (made["role"], made["members"], made["reps"]) == ("rep", 1, 1)
    assert (made["module_code"], made["university_name"], made["campus_name"]) == ("ANA 201", "University of Pretoria", "Hatfield")
    code = made["invite_code"]
    assert len(code) == 8 and set(code) <= set(CODE_ALPHABET)

    # Read out in a lecture: lower case, with a dash and a space, still works.
    spoken = f"{code[:4].lower()}- {code[4:].lower()}"
    joined = join(client, classmate, spoken)
    assert joined["joined"] is True and joined["class"]["role"] == "student"
    assert join(client, classmate, code)["joined"] is False  # twice is still once

    seen = mine(client, classmate)
    assert [(c["id"], c["role"], c["members"], c["reps"]) for c in seen] == [(made["id"], "student", 2, 1)]
    assert mine(client, rep)[0]["members"] == 2


def test_nobody_in_a_class_is_ever_listed(client, rep, classmate):
    made = make_class(client, rep)
    join(client, classmate, made["invite_code"])
    for who in (rep, classmate):
        text = str(mine(client, who))
        assert "@example.com" not in text and rep.id not in text and classmate.id not in text


@pytest.mark.parametrize("code", ["ZZZZZZZZ", "ABCD", "----", "ZZZZZZZZZZ"])
def test_a_code_that_matches_nothing_is_404(client, classmate, code):
    r = client.post(f"{CLASSES}/join", json={"code": code}, headers=classmate.headers)
    assert r.status_code == 404 and r.get_json()["code"] == "CODE_NOT_FOUND"


@pytest.mark.parametrize(
    "change, field",
    [
        ({"university": "nowhere"}, "university"),
        ({"campus": None}, "campus"),  # UP has campuses: choose one
        ({"campus": "ga_rankuwa"}, "campus"),  # not a UP campus
        ({"year": 2025}, "year"),
        ({"year": 2028}, "year"),
    ],
)
def test_class_details_are_checked_against_the_packs(client, rep, change, field):
    r = client.post(CLASSES, json=UP_CLASS | change, headers=rep.headers)
    assert r.status_code == 422 and field in r.get_json()["errors"][0]


def test_next_years_class_is_fine(client, rep):
    assert make_class(client, rep, year=2027)["year"] == 2027


def test_rep_codes_bring_in_up_to_3_reps(client, rep, classmate, outsider, outbox):
    made = make_class(client, rep)
    join(client, classmate, made["invite_code"])

    code = rep_code(client, rep, made["id"])
    assert len(code) == 10 and set(code) <= set(CODE_ALPHABET)
    became = join(client, outsider, code)  # not in the class yet: joins as a rep
    assert became["class"]["role"] == "rep"
    r = client.post(f"{CLASSES}/join", json={"code": code}, headers=classmate.headers)
    assert r.status_code == 404  # it worked once

    second = rep_code(client, outsider, made["id"])  # a rep, not only the first, can name the next
    assert join(client, classmate, second)["class"]["role"] == "rep"  # a student in the class steps up
    assert mine(client, rep)[0]["reps"] == 3

    r = client.post(f"{CLASSES}/{made['id']}/reps", headers=rep.headers)
    assert r.status_code == 409 and r.get_json()["code"] == "REPS_FULL"


def test_only_a_rep_makes_rep_codes(client, rep, classmate, outsider):
    made = make_class(client, rep)
    join(client, classmate, made["invite_code"])
    r = client.post(f"{CLASSES}/{made['id']}/reps", headers=classmate.headers)
    assert r.status_code == 403 and r.get_json()["code"] == "REP_ONLY"
    r = client.post(f"{CLASSES}/{made['id']}/reps", headers=outsider.headers)
    assert r.status_code == 404 and r.get_json()["code"] == "CLASS_NOT_FOUND"


def test_codes_waiting_can_never_make_a_fourth_rep(client, rep):
    made = make_class(client, rep)
    rep_code(client, rep, made["id"])
    rep_code(client, rep, made["id"])
    r = client.post(f"{CLASSES}/{made['id']}/reps", headers=rep.headers)
    assert r.status_code == 409 and r.get_json()["code"] == "REP_CODES_WAITING"


def test_a_full_class_turns_a_waiting_code_away(client, rep, classmate, outsider, outbox):
    made = make_class(client, rep)
    first, second = rep_code(client, rep, made["id"]), rep_code(client, rep, made["id"])
    join(client, classmate, first)
    join(client, outsider, second)
    late = student(client, outbox, "lerato@example.com")
    with client.application.app_context():  # a code from before the class filled up
        db.session.add(RepInvite(class_id=uuid.UUID(made["id"]), code_hash=class_service._hash("ABCDEFGHJK"),
                                 expires_at=datetime.now(UTC) + timedelta(hours=1)))
        db.session.commit()
    r = client.post(f"{CLASSES}/join", json={"code": "ABCDEFGHJK"}, headers=late.headers)
    assert r.status_code == 409 and r.get_json()["code"] == "REPS_FULL"


def test_an_expired_rep_code_is_404(client, rep, classmate, monkeypatch):
    made = make_class(client, rep)
    code = rep_code(client, rep, made["id"])
    later = datetime.now(UTC) + timedelta(hours=49)
    monkeypatch.setattr(class_service, "_now", lambda: later)
    r = client.post(f"{CLASSES}/join", json={"code": code}, headers=classmate.headers)
    assert r.status_code == 404 and r.get_json()["code"] == "CODE_NOT_FOUND"


def test_a_rep_cant_use_a_rep_code_on_their_own_class(client, rep, classmate):
    made = make_class(client, rep)
    code = rep_code(client, rep, made["id"])
    r = client.post(f"{CLASSES}/join", json={"code": code}, headers=rep.headers)
    assert r.status_code == 409 and r.get_json()["code"] == "ALREADY_REP"
    assert join(client, classmate, code)["class"]["role"] == "rep"  # the code wasn't used up


def test_only_the_codes_hash_is_kept(client, app, rep):
    made = make_class(client, rep)
    code = rep_code(client, rep, made["id"])
    with app.app_context():
        stored = RepInvite.query.filter_by(class_id=uuid.UUID(made["id"])).one()
        assert stored.code_hash != code and code not in stored.code_hash and len(stored.code_hash) == 64


def test_leaving_a_class(client, rep, classmate):
    made = make_class(client, rep)
    join(client, classmate, made["invite_code"])
    assert client.delete(f"{CLASSES}/{made['id']}/membership", headers=classmate.headers).status_code == 200
    assert mine(client, classmate) == []
    assert mine(client, rep)[0]["members"] == 1
    r = client.delete(f"{CLASSES}/{made['id']}/membership", headers=classmate.headers)
    assert r.status_code == 404 and r.get_json()["code"] == "CLASS_NOT_FOUND"


def test_a_student_can_be_in_so_many_classes(client, rep, classmate, monkeypatch):
    monkeypatch.setattr(class_service, "MAX_CLASSES", 1)
    first = make_class(client, rep)
    r = client.post(CLASSES, json=UP_CLASS | {"module_code": "PHY121"}, headers=rep.headers)
    assert r.status_code == 422 and "classes" in r.get_json()["errors"][0]
    make_class(client, classmate, module_code="BCH111")
    r = client.post(f"{CLASSES}/join", json={"code": first["invite_code"]}, headers=classmate.headers)
    assert r.status_code == 422


# ------------------------------------------------------------- hostile


@pytest.mark.parametrize(
    "change",
    [
        {"module_code": ""},
        {"module_code": "ANA201'; --"},
        {"module_code": "A" * 17},
        {"module_name": "   "},
        {"module_name": "x" * 81},
        {"year": "2026"},
        {"year": 2026.0},
        {"year": True},
        {"university": ""},
        {"university": "u" * 41},
        {"role": "admin"},
        {"invite_code": "AAAAAAAA"},
        {"created_by": str(uuid.uuid4())},
    ],
)
def test_odd_classes_are_refused(client, rep, change):
    assert client.post(CLASSES, json=UP_CLASS | change, headers=rep.headers).status_code == 422


@pytest.mark.parametrize("body", [{}, {"code": ""}, {"code": "A" * 41}, {"code": 12345678}, {"code": "ABCDEFGH", "role": "rep"}])
def test_odd_joins_are_refused(client, classmate, body):
    assert client.post(f"{CLASSES}/join", json=body, headers=classmate.headers).status_code == 422


def test_odd_rep_code_requests_and_queries_are_refused(client, rep):
    made = make_class(client, rep)
    r = client.post(f"{CLASSES}/{made['id']}/reps", json={"user_id": str(uuid.uuid4())}, headers=rep.headers)
    assert r.status_code == 422
    assert client.get(f"{CLASSES}/mine?all=true", headers=rep.headers).status_code == 422
    assert client.post(f"{CLASSES}/not-a-uuid/reps", headers=rep.headers).status_code == 404


def test_guessing_codes_is_slow(client, app, classmate, outsider):
    limiter.enabled = True
    with app.app_context():
        limiter.reset()
    try:
        codes = [client.post(f"{CLASSES}/join", json={"code": "ZZZZZZZZ"}, headers=classmate.headers).status_code for _ in range(21)]
        assert codes[:20] == [404] * 20 and codes[20] == 429
        assert client.post(f"{CLASSES}/join", json={"code": "ZZZZZZZZ"}, headers=outsider.headers).status_code == 404
    finally:
        with app.app_context():
            limiter.reset()
        limiter.enabled = False


def test_old_classes_and_expired_codes_are_forgotten(app):
    this_year = datetime.now(ZoneInfo("Africa/Johannesburg")).year  # the job's own today
    with app.app_context():
        for year, code in ((this_year - 2, "OLDOLDAA"), (this_year - 1, "LASTYRAA"), (this_year, "THISYRAA")):
            db.session.add(ModuleClass(university="up", campus="hatfield", module_code="ANA201", year=year, invite_code=code))
        db.session.flush()
        kept = ModuleClass.query.filter_by(invite_code="LASTYRAA").one()
        db.session.add(RepInvite(class_id=kept.id, code_hash="a" * 64, expires_at=datetime.now(UTC) - timedelta(minutes=1)))
        db.session.add(RepInvite(class_id=kept.id, code_hash="b" * 64, expires_at=datetime.now(UTC) + timedelta(hours=1)))
        db.session.commit()

        result = forget_old_classes.run()
        assert result.success and result.count == 2
        assert sorted(c.invite_code for c in ModuleClass.query) == ["LASTYRAA", "THISYRAA"]
        assert [r.code_hash for r in RepInvite.query] == ["b" * 64]
        assert ClassMember.query.count() == 0
