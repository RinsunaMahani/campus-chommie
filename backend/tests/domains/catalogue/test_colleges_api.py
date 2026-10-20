"""
Colleges: the list, one college in full, and "is this college registered?". Public and read-only,
straight from the colleges pack, honest about a pack nobody has checked yet, storing and logging
nothing, and refusing anything it doesn't expect.
"""
from __future__ import annotations

import logging

import pytest
from sqlalchemy import event

from src.extensions import db
from src.shared.rate_limit.limiter import limiter

BASE = "/api/v1/colleges"


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


# ------------------------------------------------------------------------- the list


def test_the_list_needs_no_account_and_counts_every_status(client):
    r = client.get(BASE)
    assert r.status_code == 200
    data = r.get_json()["data"]
    assert data["summary"] == "357 colleges: 50 public, 141 registered, 59 provisionally registered, 107 cancelled."
    assert data["counts"]["total"] == data["total"] == 357
    assert (data["page"], data["pages"], len(data["colleges"])) == (1, 9, 40)
    assert (data["confirmed"], data["notice"]) == (False, "Not yet confirmed by the team.")
    first = data["colleges"][0]
    assert set(first) == {"id", "name", "kind", "kind_label", "status", "label", "registration_number",
                          "provinces", "website", "lines"}


def test_a_search_finds_tvet_colleges_by_the_trade_they_teach(client):
    data = client.get(BASE, query_string={"q": "electrician"}).get_json()["data"]
    assert data["total"] == 35 and data["summary"] == "35 colleges: 35 public."
    assert all(c["kind"] == "tvet" for c in data["colleges"])


def test_filters_and_pages(client):
    tvet = client.get(BASE, query_string={"kind": "tvet", "province": "Limpopo"}).get_json()["data"]
    assert tvet["total"] == 7 and all(c["provinces"] == ["Limpopo"] for c in tvet["colleges"])
    last = client.get(BASE, query_string={"page": 9}).get_json()["data"]
    assert len(last["colleges"]) == 357 - 8 * 40
    assert client.get(BASE, query_string={"page": 10}).get_json()["data"]["colleges"] == []


def test_one_college_in_full_with_its_source(client):
    data = client.get(f"{BASE}/the-independent-institute-of-education").get_json()["data"]
    c = data["college"]
    assert (c["status"], c["registration_number"], c["kind_label"]) == (
        "registered", "2007/HE07/002", "Private higher education institution")
    assert c["qualifications"] and c["sites"] and c["occupational"] == []
    assert c["sources"][0]["publisher"] == "Department of Higher Education and Training"
    assert data["warning_signs"] is None


def test_a_tvet_college_lists_its_occupational_qualifications(client):
    c = client.get(f"{BASE}/port-elizabeth-tvet-college").get_json()["data"]["college"]
    electrician = next(q for q in c["occupational"] if q["saqa_id"] == "91761")
    assert electrician == {"saqa_id": "91761", "name": "Occupational Certificate: Electrician",
                           "nsfas_allowances": False, "centre_of_specialisation": True}
    assert c["phone"] and c["head_office"] and c["website"].startswith("www.")
    assert len(c["sources"]) == 2


def test_a_cancelled_college_carries_dhets_warning_signs(client):
    ids = [c["id"] for c in client.get(BASE, query_string={"status": "cancelled", "kind": "private_college"})
           .get_json()["data"]["colleges"]]
    data = client.get(f"{BASE}/{ids[0]}").get_json()["data"]
    assert "will not sit for examinations nor be certificated" in data["college"]["lines"][0]
    assert len(data["warning_signs"]["items"]) == 11


def test_an_unknown_college_is_a_404_that_doesnt_repeat_the_id(client):
    for college_id in ("hogwarts", "x" * 300, "' OR '1'='1"):
        r = client.get(f"{BASE}/{college_id}")
        assert r.status_code == 404 and r.get_json()["code"] == "COLLEGE_NOT_FOUND"
        assert college_id not in r.get_data(as_text=True)


# ------------------------------------------------------------------------- the check


def test_checking_a_bogus_college(client):
    data = client.get(f"{BASE}/check", query_string={"name": "Barkley University"}).get_json()["data"]
    assert (data["verdict"], data["label"]) == ("bogus", "Illegal (bogus) college")
    assert data["unregistered"][0]["name"] == "Barkley University"
    assert len(data["warning_signs"]["items"]) == 11 and len(data["sources"]) == 4


def test_checking_by_registration_number(client):
    data = client.get(f"{BASE}/check", query_string={"name": "2007/HE07/002"}).get_json()["data"]
    assert data["verdict"] == "registered"
    assert [c["id"] for c in data["colleges"]] == ["the-independent-institute-of-education"]


def test_a_name_we_dont_have_is_not_called_bogus(client):
    data = client.get(f"{BASE}/check", query_string={"name": "Hogwarts"}).get_json()["data"]
    assert data["verdict"] == "not_found" and "doesn't make a college bogus" in data["lines"][1]


# --------------------------------------------------------------------- hostile input


@pytest.mark.parametrize("query", [
    {"include": "secrets"},
    {"kind": "university"},
    {"province": "Gautng"},
    {"status": "bogus"},
    {"page": "0"},
    {"page": "101"},
    {"page": "two"},
    {"q": ""},
    {"q": "ab"},  # shorter than the config's minimum
    {"q": "x" * 121},
    {"q": "dam\nelin"},
])
def test_odd_searches_are_refused(client, query):
    assert client.get(BASE, query_string=query).status_code == 422


@pytest.mark.parametrize("query", [{}, {"name": ""}, {"name": "ab"}, {"name": "x" * 121}, {"name": "a\x07bc"},
                                   {"name": "acme", "q": "acme"}])
def test_odd_checks_are_refused(client, query):
    assert client.get(f"{BASE}/check", query_string=query).status_code == 422


def test_a_nul_character_is_refused_before_any_route(client):
    r = client.get(BASE, query_string={"q": "damelin" + chr(0)})
    assert r.status_code == 400 and r.get_json()["code"] == "INVALID_CHARACTERS"


def test_a_parameter_given_twice_is_refused(client):
    assert client.get(f"{BASE}?q=acme&q=beta").status_code == 422
    assert client.get(f"{BASE}/check?name=acme&name=beta").status_code == 422


def test_one_college_takes_no_query_parameters(client):
    assert client.get(f"{BASE}/the-independent-institute-of-education", query_string={"q": "x"}).status_code == 422


def test_odd_but_harmless_searches_are_only_words(client):
    """A search is read as words to find at the start of words in a name, never run as anything."""
    for q in ("' OR '1'='1", "<script>alert(1)</script>", "../../etc/passwd"):
        r = client.get(BASE, query_string={"q": q})
        assert r.status_code == 200 and r.get_json()["data"]["total"] < 357
    assert client.get(BASE, query_string={"q": "%%%"}).get_json()["data"]["total"] == 0


def test_colleges_never_touch_the_database_or_log_a_search(app, client, caplog):
    with app.app_context():
        engine = db.engine
    statements: list[str] = []

    def record(conn, cursor, statement, *args):
        statements.append(statement)

    event.listen(engine, "before_cursor_execute", record)
    caplog.set_level(logging.DEBUG)
    try:
        assert client.get(BASE, query_string={"q": "zebra-learner-search"}).status_code == 200
        assert client.get(f"{BASE}/check", query_string={"name": "zebra-learner-check"}).status_code == 200
        assert client.get(f"{BASE}/port-elizabeth-tvet-college").status_code == 200
        assert client.get(f"{BASE}/hogwarts").status_code == 404
    finally:
        event.remove(engine, "before_cursor_execute", record)
    assert statements == []
    assert "zebra-learner" not in caplog.text


def test_colleges_are_limited_per_ip(client, limits_on):
    for path, query in ((BASE, {}), (f"{BASE}/check", {"name": "acme"}), (f"{BASE}/port-elizabeth-tvet-college", {})):
        codes = [client.get(path, query_string=query).status_code for _ in range(121)]
        assert codes[:120] == [200] * 120 and codes[120] == 429
