"""
The university catalogue: public, read-only, straight from the data packs,
and honest about packs nobody has checked yet.
"""
from __future__ import annotations

import pytest

from src.shared.rate_limit.limiter import limiter

BASE = "/api/v1/universities"


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


def test_the_list_needs_no_account_and_flags_unchecked_packs(client):
    r = client.get(BASE)
    assert r.status_code == 200
    universities = {u["id"]: u for u in r.get_json()["data"]["universities"]}
    assert set(universities) == {"smu", "tut", "up"}
    smu = universities["smu"]
    assert smu["name"] == "Sefako Makgatho Health Sciences University"
    assert smu["programmes"] == 17
    assert all(u["confirmed"] is False and u["notice"] == "Not yet confirmed by the team." for u in universities.values())


def test_one_university_shows_its_pack_and_sources(client):
    r = client.get(f"{BASE}/smu")
    assert r.status_code == 200
    uni = r.get_json()["data"]["university"]
    assert uni["id"] == "smu" and "release" not in uni and uni["confirmed"] is False
    mbchb = next(p for p in uni["programmes"] if p["id"] == "mbchb")
    assert mbchb["requirements"]["min_points"] == 38
    assert mbchb["requirements"]["subject_minimums"]["mathematics"] == 6
    assert uni["sources"][0]["url"].startswith("https://www.smu.ac.za/")


def test_an_unknown_university_is_a_404(client):
    r = client.get(f"{BASE}/hogwarts")
    assert r.status_code == 404
    assert r.get_json()["code"] == "UNIVERSITY_NOT_FOUND"


@pytest.mark.parametrize("path", [BASE, f"{BASE}/smu"])
def test_query_parameters_are_refused(client, path):
    assert client.get(path, query_string={"include": "secrets"}).status_code == 422


def test_the_templates_never_show_up(client):
    ids = {u["id"] for u in client.get(BASE).get_json()["data"]["universities"]}
    assert "example" not in ids
    assert client.get(f"{BASE}/example").status_code == 404


def test_the_catalogue_is_limited_per_ip(client, limits_on):
    codes = [client.get(BASE).status_code for _ in range(121)]
    assert codes[:120] == [200] * 120 and codes[120] == 429
