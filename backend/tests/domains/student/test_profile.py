"""
The student's profile: university and campus checked against the data packs,
the 18-or-older confirmation from sign-up, nothing else stored, nobody
else's profile.
"""
from __future__ import annotations

import pytest
from student_helpers import PROFILE, student

from src.shared.rate_limit.limiter import limiter


@pytest.fixture
def me(client, outbox):
    return student(client, outbox, "lindiwe@example.com")


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


@pytest.mark.parametrize("method", ["get", "put"])
def test_the_profile_needs_a_token(client, method):
    assert getattr(client, method)(PROFILE, json={}).status_code == 401


def test_a_new_profile_shows_the_18_or_older_confirmation_from_sign_up(client, me):
    profile = client.get(PROFILE, headers=me.headers).get_json()["data"]["profile"]
    assert (profile["university"], profile["campus"]) == (None, None)
    assert profile["confirmed_18_or_older_at"] is not None
    assert {c["document"] for c in profile["consents"]} >= {"age_confirmation"}


def test_university_and_campus_are_saved_with_their_names(client, me):
    r = client.put(PROFILE, json={"university": "tut", "campus": "soshanguve_south"}, headers=me.headers)
    assert r.status_code == 200
    profile = r.get_json()["data"]["profile"]
    assert profile["university_name"] == "Tshwane University of Technology"
    assert (profile["campus"], profile["campus_name"]) == ("soshanguve_south", "Soshanguve South")
    assert client.get(PROFILE, headers=me.headers).get_json()["data"]["profile"]["campus"] == "soshanguve_south"


@pytest.mark.parametrize(
    "body, field",
    [
        ({"university": "hogwarts", "campus": "main"}, "university"),
        ({"university": "up", "campus": "soshanguve_south"}, "campus"),  # a TUT campus, not UP's
        ({"university": "up"}, "campus"),  # UP lists its campuses, so choose one
        ({"university": "up", "campus": "hatfield", "id_number": "0001015009087"}, "id_number"),
        ({"university": "up", "campus": "hatfield", "race": "x"}, "race"),
        ({"university": "", "campus": "hatfield"}, "university"),
        ({"university": ["up"], "campus": "hatfield"}, "university"),
    ],
)
def test_odd_profiles_are_refused(client, me, body, field):
    r = client.put(PROFILE, json=body, headers=me.headers)
    assert r.status_code == 422
    assert field in r.get_json()["errors"][0]


def test_each_student_sees_only_their_own_profile(client, outbox, me):
    client.put(PROFILE, json={"university": "smu", "campus": "ga_rankuwa"}, headers=me.headers)
    other = student(client, outbox, "sipho@example.com")
    assert client.get(PROFILE, headers=other.headers).get_json()["data"]["profile"]["university"] is None


def test_profile_changes_are_limited_per_student(client, me, limits_on):
    body = {"university": "smu", "campus": "ga_rankuwa"}
    codes = [client.put(PROFILE, json=body, headers=me.headers).status_code for _ in range(31)]
    assert codes[:30] == [200] * 30 and codes[30] == 429
