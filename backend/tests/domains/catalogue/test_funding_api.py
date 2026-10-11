"""
Funding: the list and one funder in full. Public and read-only, straight from the funding pack,
honest about a pack nobody has checked yet, never asking anything about the learner, and
refusing anything it doesn't expect.
"""
from __future__ import annotations

from datetime import date

import pytest
from sqlalchemy import event

from src.domains.catalogue.funding.services import funding_service
from src.extensions import db
from src.shared.rate_limit.limiter import limiter

BASE = "/api/v1/funding"


@pytest.fixture
def on_11_october(monkeypatch):
    """Today is fixed, so these answers don't change as real dates pass."""
    monkeypatch.setattr(funding_service, "_today", lambda: date(2026, 10, 11))


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


def _ids(r) -> list[str]:
    return [f["id"] for f in r.get_json()["data"]["funders"]]


# ------------------------------------------------------------------------- the list


def test_the_list_needs_no_account_and_counts_whats_open(client, on_11_october):
    r = client.get(BASE)
    assert r.status_code == 200
    data = r.get_json()["data"]
    assert data["today"] == "2026-10-11"
    assert data["summary"] == "19 funding options: 3 open now."
    assert data["counts"] == {"total": 19, "open_now": 3, "closing_soon": 0}
    assert (data["confirmed"], data["notice"]) == (False, "Not yet confirmed by the team.")
    assert _ids(r)[:3] == ["clicks_foundation", "nsfas", "funza_lushaka"]

    clicks = data["funders"][0]
    assert (clicks["status"], clicks["label"], clicks["days"], clicks["closes"]) == ("open", "Open", 20, "2026-10-31")
    assert (clicks["kind"], clicks["kind_label"], clicks["sector_label"]) == ("bursary", "Bursary", "Company")
    assert (clicks["any_field"], clicks["fields"]) == (False, [{"id": "pharmacy", "label": "Pharmacy"}])
    assert clicks["stages"] == [{"id": "senior", "label": "Already studying"}] and clicks["study_at"] == "any"
    assert clicks["lines"][0] == "Open now. Closes on Sat 31 Oct 2026 (in 20 days)."
    assert clicks["url"] == "https://careers.clicksgroup.co.za/" and clicks["checked"] == "2026-10-11"
    assert clicks["source_url"].startswith("https://careers.clicksgroup.co.za/") and clicks["why"] is None

    fields = {f["id"]: f for f in data["fields"]}
    assert fields["accounting"] == {"id": "accounting", "label": "Accounting", "funders": 3}
    assert fields["education"]["funders"] == 1


def test_closed_funding_says_so_and_what_comes_next(client, on_11_october):
    funders = {f["id"]: f for f in client.get(BASE).get_json()["data"]["funders"]}
    thuthuka = funders["thuthuka"]
    assert (thuthuka["status"], thuthuka["intake"], thuthuka["closes"]) == ("closed", 2027, "2026-08-31")
    assert thuthuka["lines"][:2] == ["Closed on Mon 31 Aug 2026.", "Funding for 2028: Thuthuka hasn't published these dates yet."]
    assert funders["isfap"]["lines"][0] == "Closed: ISFAP's own page said so on Sun 11 Oct 2026."
    flyup = funders["up_flyup_awards"]
    assert (flyup["status"], flyup["label"], flyup["intake"], flyup["study_at"]) == ("automatic", "No application needed", None, ["up"])


@pytest.mark.parametrize(
    "query, expected",
    [
        ({"status": "open"}, ["clicks_foundation", "nsfas", "funza_lushaka"]),
        ({"kind": "loan"}, ["nsfas_loans"]),
        ({"kind": "merit_award"}, ["up_flyup_awards"]),
        ({"field": "pharmacy", "status": "open"}, ["clicks_foundation", "nsfas"]),
        ({"field": "education", "stage": "first_year", "status": "open"}, ["funza_lushaka", "nsfas"]),
        ({"field": "disaster_and_fire", "status": "closed"}, ["ndmc"]),
    ],
)
def test_filters(client, on_11_october, query, expected):
    r = client.get(BASE, query_string=query)
    assert r.status_code == 200
    assert _ids(r)[: len(expected)] == expected


def test_a_field_search_puts_that_fields_own_funders_first_and_says_why(client, on_11_october):
    r = client.get(BASE, query_string={"field": "accounting,law"})
    funders = r.get_json()["data"]["funders"]
    closed = [f for f in funders if f["status"] == "closed"]
    assert [f["id"] for f in closed[:4]] == ["allan_gray_fellowship", "ey_ca_bursary", "national_treasury", "thuthuka"]
    assert (closed[0]["why"], closed[2]["why"]) == ("Funds law.", "Funds accounting and law.")
    assert {f["why"] for f in funders if f["any_field"]} == {"Open to any field."}


def test_postgraduates_and_students_already_studying_have_their_own_lists(client, on_11_october):
    postgrad = _ids(client.get(BASE, query_string={"stage": "postgraduate"}))
    assert "csir" in postgrad and "national_treasury" in postgrad and "thuthuka" not in postgrad
    senior = _ids(client.get(BASE, query_string={"stage": "senior"}))
    assert senior[0] == "clicks_foundation" and "sarb" not in senior


# ---------------------------------------------------------------------- one funder


def test_one_funder_in_full_with_its_sources(client, on_11_october):
    r = client.get(f"{BASE}/funza_lushaka")
    assert r.status_code == 200
    data = r.get_json()["data"]
    funza = data["funder"]
    assert (funza["status"], funza["closes"], funza["days"]) == ("open", "2027-01-31", 112)
    assert funza["who_can_apply"]["items"][0] == "South African citizens with a valid South African ID card"
    assert funza["covers"]["items"][0] == "Tuition fees" and funza["covers"]["source_url"].endswith(".pdf")
    assert funza["obligations"]["items"][0] == "Teach one year for every year the bursary paid for."
    apply = funza["apply"]
    assert apply["url"] == "https://www.funzalushaka.doe.gov.za/" and apply["tips"]["items"]
    assert [(w["intake"], w["status"]) for w in apply["windows"]] == [(2027, "open"), (2028, "not_published")]
    assert apply["windows"][0]["lines"][-1] == "Students already funded re-apply by Mon 30 Nov 2026."
    assert {s["url"] for s in funza["sources"]} == {
        "https://www.funzalushaka.doe.gov.za/",
        "https://www.funzalushaka.doe.gov.za/Content/Documents/Funza%20Lushaka%20Bursary%20Application%20Notes%202027.pdf",
    }
    assert all(s["retrieved"] == "2026-10-11" and s["last_verified"] is None for s in funza["sources"])
    assert data["confirmed"] is False


def test_an_automatic_award_has_no_dates_or_fees_to_show(client, on_11_october):
    flyup = client.get(f"{BASE}/up_flyup_awards").get_json()["data"]["funder"]
    assert flyup["apply"]["windows"] == []
    assert flyup["apply"]["lines"] == ["There's no application: UP makes these awards automatically to first-time first-years who qualify."]
    assert flyup["covers"]["items"][0].startswith("In 2026: R18 000")


def test_nsfas_keeps_its_fee_tips_and_warnings(client, on_11_october):
    nsfas = client.get(f"{BASE}/nsfas").get_json()["data"]["funder"]
    assert nsfas["apply"]["fee_cents"] == 0 and len(nsfas["apply"]["tips"]["items"]) == 8
    assert nsfas["apply"]["warnings"]["items"][0].startswith("Never pay anyone to apply.")


def test_an_unknown_funder_is_a_404_that_doesnt_repeat_the_id(client):
    for funder_id in ("hogwarts", "NSFAS", "nsfas' OR '1'='1", "x" * 300):
        r = client.get(f"{BASE}/{funder_id}")
        assert r.status_code == 404 and r.get_json()["code"] == "FUNDER_NOT_FOUND"
        assert funder_id not in r.get_data(as_text=True)


# --------------------------------------------------------------------- hostile input


@pytest.mark.parametrize(
    "query",
    [
        {"include": "secrets"},
        {"income": "350000"},  # never a filter about the learner
        {"race": "any"},
        {"status": "everything"},
        {"status": ""},
        {"kind": "grant"},
        {"stage": "matric"},
        {"field": ""},
        {"field": "enginering"},
        {"field": "engineering,"},
        {"field": "engineering,engineering"},
        {"field": ",".join(["engineering", "computing", "law", "finance", "economics", "accounting", "commerce",
                            "management", "education", "pharmacy", "nursing"])},
        {"field": "x" * 401},
        {"field": "engineering;DROP TABLE users"},
    ],
)
def test_odd_filters_are_refused(client, query):
    assert client.get(BASE, query_string=query).status_code == 422


def test_a_filter_given_twice_is_refused(client):
    r = client.get(f"{BASE}?status=open&status=closed")
    assert r.status_code == 422
    assert client.get(f"{BASE}/nsfas?x=1&x=2").status_code == 422


def test_one_funder_takes_no_query_parameters(client):
    assert client.get(f"{BASE}/nsfas", query_string={"status": "open"}).status_code == 422


def test_funding_never_touches_the_database(app, client):
    with app.app_context():
        engine = db.engine
    statements: list[str] = []

    def record(conn, cursor, statement, *args):
        statements.append(statement)

    event.listen(engine, "before_cursor_execute", record)
    try:
        assert client.get(BASE).status_code == 200
        assert client.get(BASE, query_string={"field": "engineering", "status": "open"}).status_code == 200
        assert client.get(f"{BASE}/nsfas").status_code == 200
        assert client.get(f"{BASE}/hogwarts").status_code == 404
        assert client.get(BASE, query_string={"status": "x"}).status_code == 422
    finally:
        event.remove(engine, "before_cursor_execute", record)
    assert statements == []


def test_funding_is_limited_per_ip(client, limits_on):
    codes = [client.get(BASE).status_code for _ in range(121)]
    assert codes[:120] == [200] * 120 and codes[120] == 429
    codes = [client.get(f"{BASE}/nsfas").status_code for _ in range(121)]
    assert codes[:120] == [200] * 120 and codes[120] == 429
