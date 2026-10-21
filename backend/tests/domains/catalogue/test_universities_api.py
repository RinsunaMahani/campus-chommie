"""
The university catalogue: public, read-only, straight from the data packs,
and honest about packs nobody has checked yet. Also a new student's first
steps, from accepting an offer to the first lecture.
"""
from __future__ import annotations

from datetime import date

import pytest

from src.domains.catalogue.universities.services import university_service
from src.shared.rate_limit.limiter import limiter

BASE = "/api/v1/universities"


@pytest.fixture
def on_10_october(monkeypatch):
    """Today is fixed, so these answers don't change as real dates pass."""
    monkeypatch.setattr(university_service, "_today", lambda: date(2026, 10, 10))


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
    assert {"smu", "tut", "up", "wits", "uj", "unisa"} <= set(universities)
    smu = universities["smu"]
    assert smu["name"] == "Sefako Makgatho Health Sciences University"
    assert smu["programmes"] == 17
    # A university whose programmes aren't added yet is still listed, with none.
    assert universities["uj"]["programmes"] == 0
    assert universities["wits"]["programmes"] > 0
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


@pytest.mark.parametrize("path", [BASE, f"{BASE}/smu", f"{BASE}/smu/first-steps"])
def test_query_parameters_are_refused(client, path):
    assert client.get(path, query_string={"include": "secrets"}).status_code == 422


def test_the_templates_never_show_up(client):
    ids = {u["id"] for u in client.get(BASE).get_json()["data"]["universities"]}
    assert "example" not in ids
    assert client.get(f"{BASE}/example").status_code == 404


def test_the_catalogue_is_limited_per_ip(client, limits_on):
    codes = [client.get(BASE).status_code for _ in range(121)]
    assert codes[:120] == [200] * 120 and codes[120] == 429


def test_first_steps_from_acceptance_to_the_first_lecture(client, on_10_october):
    r = client.get(f"{BASE}/tut/first-steps")
    assert r.status_code == 200
    data = r.get_json()["data"]
    assert data["today"] == "2026-10-10" and data["university"]["id"] == "tut"
    assert data["university"]["confirmed"] is False
    (intake,) = data["first_steps"]
    assert intake["intake"] == 2027 and intake["notes"] == []
    steps = {s["key"]: s for s in intake["steps"]}
    assert list(steps) == ["accept", "register", "orientation", "first_lecture"]
    assert steps["accept"]["status"] == "when_offered" and "R1 500" in steps["accept"]["lines"][0]
    register = steps["register"]
    assert (register["status"], register["starts"], register["ends"], register["days"]) == ("ahead", "2027-01-14", "2027-01-31", 96)
    assert register["lines"][-1].startswith("If NSFAS finds you eligible")
    assert register["source_urls"][0].startswith("https://www.tut.ac.za/")
    assert register["source_urls"][-1].startswith("https://nsfas.org.za/")
    assert (steps["first_lecture"]["starts"], steps["first_lecture"]["label"]) == ("2027-02-01", "Coming up")


def test_first_steps_say_when_dates_arent_published(client, on_10_october):
    (intake,) = client.get(f"{BASE}/smu/first-steps").get_json()["data"]["first_steps"]
    assert intake["notes"] == ["Sefako Makgatho Health Sciences University hasn't published its 2027 dates yet."]
    assert {s["status"] for s in intake["steps"][1:]} == {"not_published"}
    assert intake["steps"][1]["lines"][1] == "For 2026: First-year registration: Wed 21 to Fri 30 Jan 2026."


def test_first_steps_for_an_unknown_university_is_a_404(client):
    r = client.get(f"{BASE}/hogwarts/first-steps")
    assert r.status_code == 404 and r.get_json()["code"] == "UNIVERSITY_NOT_FOUND"


def test_first_steps_are_limited_per_ip(client, limits_on):
    codes = [client.get(f"{BASE}/up/first-steps").status_code for _ in range(121)]
    assert codes[:120] == [200] * 120 and codes[120] == 429


def test_province_and_type_show_only_where_a_cited_page_states_them(client):
    unis = {u["id"]: u for u in client.get("/api/v1/universities").get_json()["data"]["universities"]}
    assert (unis["cut"]["province"], unis["cut"]["institution_type_label"]) == ("Free State", "University of technology")
    assert (unis["univen"]["province"], unis["univen"]["institution_type_label"]) == ("Limpopo", "Comprehensive university")
    assert (unis["ufs"]["province"], unis["ufs"]["institution_type"]) == ("Free State", None)  # its page states no type
    assert (unis["up"]["province"], unis["up"]["institution_type"]) == (None, None)  # not confirmed on a source yet
