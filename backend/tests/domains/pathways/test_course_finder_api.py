"""
The course finder end to end: marks in, tier cards and the three-choice plan
out, each with its plain-words reasons and source, and how to apply on
today's date. No account needed.
"""
from __future__ import annotations

from datetime import date

import pytest
from course_finder_helpers import ASSESS, PLAN, POINTS, STRONG, marks

from src.domains.pathways.course_finder.services import course_finder_service


@pytest.fixture
def on_10_october(monkeypatch):
    """Today is fixed, so these answers don't change as real dates pass."""
    monkeypatch.setattr(course_finder_service, "_today", lambda: date(2026, 10, 10))


def test_m1_acceptance_the_strong_smu_learners_plan(client):
    """The brief's M1 check, as the team changed it on 9 Oct 2026 (fields tagged honestly):
    slot 3 is no longer SMU's selective B Rad but the closest related programme without
    competitive selection, UP's BSc Medical Sciences."""
    r = client.post(PLAN, json={"university": "smu", "goal": "mbchb", "marks": STRONG})
    assert r.status_code == 200
    plan = r.get_json()["data"]["plan"]

    goal = plan["goal"]["match"]
    assert (goal["programme"], goal["tier"], goal["label"]) == ("mbchb", "reach", "Reach")

    bridge = plan["bridge"]
    assert bridge["match"]["programme"] == "bsc_y1"
    assert bridge["bridge"]["guarantee"] == "considered" and bridge["bridge"]["max_places"] == 5
    assert "Places on this route: 5." in bridge["notes"]

    assert [r["match"]["programme"] for r in plan["other_routes"]] == ["mbchb_ecp"]
    assert plan["other_routes"][0]["bridge"]["eligibility_note"]
    assert any(n.startswith("Eligibility:") for n in plan["other_routes"][0]["notes"])

    safe = plan["safe"]
    assert (safe["match"]["university"], safe["match"]["programme"]) == ("up", "bsc_medical_sciences")
    assert safe["match"]["tier"] == "meets_minimum"
    assert safe["notes"][0].endswith("through health sciences and medical sciences.")


def test_every_card_has_its_reasons_source_and_check_status(client):
    r = client.post(PLAN, json={"university": "smu", "goal": "mbchb", "marks": STRONG})
    plan = r.get_json()["data"]["plan"]
    for slot in [plan["goal"], plan["bridge"], plan["safe"], *plan["other_routes"]]:
        match = slot["match"]
        assert match["explanation"]
        assert match["confirmed"] is False and match["notice"] == "Not yet confirmed by the team."
        assert match["source_url"].startswith("https://")
    assert plan["goal"]["match"]["source_url"].startswith("https://www.smu.ac.za/")
    assert plan["safe"]["match"]["source_url"].startswith("https://drupalwebprod-files.up.ac.za/")
    assert plan["bridge"]["bridge"]["source_url"].startswith("https://www.smu.ac.za/")


def test_assess_lists_every_programme_best_tiers_first(client):
    r = client.post(ASSESS, json={"university": "smu", "marks": STRONG})
    assert r.status_code == 200
    data = r.get_json()["data"]
    assert data["university"]["id"] == "smu" and data["university"]["confirmed"] is False
    order = ["competitive", "meets_minimum", "reach", "unverified", "not_yet"]
    ranks = [order.index(m["tier"]) for m in data["matches"]]
    assert ranks == sorted(ranks) and len(ranks) == 17
    mbchb = next(m for m in data["matches"] if m["programme"] == "mbchb")
    assert mbchb["points"] == 47
    assert mbchb["explanation"][0] == "Your points: 47 (minimum 38)."


def test_a_weak_subject_explains_what_is_missing(client):
    r = client.post(ASSESS, json={"university": "smu", "marks": marks(mathematics=65)})
    mbchb = next(m for m in r.get_json()["data"]["matches"] if m["programme"] == "mbchb")
    assert mbchb["tier"] == "not_yet"
    assert "Mathematics: level 5, needs 6." in mbchb["failed"]


def test_another_subject_rows_count_towards_points(client):
    rows = [m for m in STRONG if m["subject"] != "geography"] + [{"subject": "another_subject_1", "percent": 74}]
    r = client.post(ASSESS, json={"university": "smu", "marks": rows})
    mbchb = next(m for m in r.get_json()["data"]["matches"] if m["programme"] == "mbchb")
    assert mbchb["points"] == 47


def test_decimal_marks_are_fine(client):
    r = client.post(ASSESS, json={"university": "smu", "marks": marks(mathematics=79.5)})
    assert r.status_code == 200


def test_a_preview_on_a_test_date_finds_applications_open_and_says_so(client, app, monkeypatch):
    """CAMPUS_PREVIEW_TODAY (development only, shared/clock) moves "today" for a preview: on Mon 1 Jun 2026 SMU's
    applications to start in 2027 are open, and the plan says its dates come from a test date."""
    monkeypatch.setitem(app.config, "PREVIEW_TODAY", date(2026, 6, 1))
    plan = client.post(PLAN, json={"university": "smu", "goal": "mbchb", "marks": STRONG}).get_json()["data"]["plan"]
    assert (plan["apply"]["today"], plan["apply"]["test_date"]) == ("2026-06-01", True)
    goal = plan["goal"]["apply"][0]
    assert (goal["intake"], goal["status"], goal["closes"]) == (2027, "open", "2026-07-31")


def test_a_plan_says_how_to_apply_on_todays_date(client, on_10_october):
    r = client.post(PLAN, json={"university": "smu", "goal": "mbchb", "marks": STRONG})
    plan = r.get_json()["data"]["plan"]
    apply = plan["apply"]
    assert (apply["today"], apply["test_date"]) == ("2026-10-10", False)

    goal = plan["goal"]["apply"]
    assert [(w["intake"], w["status"], w["label"]) for w in goal] == [
        (2027, "closed", "Closed"),
        (2028, "not_published", "Dates not published yet"),
    ]
    assert goal[0]["lines"] == ["Closed on Fri 31 Jul 2026.", "No late applications."]
    assert goal[0]["closes"] == "2026-07-31" and goal[0]["source_url"].startswith("https://www.smu.ac.za/")
    for slot in [plan["bridge"], plan["safe"], *plan["other_routes"]]:
        assert [w["intake"] for w in slot["apply"]] == [2027, 2028]

    assert apply["deadlines"][0] == {
        "date": "2026-10-31",
        "days": 21,
        "text": "NSFAS: applications for 2027 funding close at 23:59.",
        "intake": 2027,
        "who": "nsfas",
        "programme": None,
        "source_url": "https://nsfas.org.za/content/how-to-apply.html",
    }

    smu, up = apply["universities"]
    assert (smu["id"], smu["fee_cents"], smu["max_choices"]) == ("smu", 30000, 2)
    assert smu["documents"]["items"][0] == "A certified copy of your ID or passport (compulsory)"
    assert up["id"] == "up" and "Where to apply: not verified yet." in up["lines"]

    nsfas = apply["funding"][0]
    assert (nsfas["id"], nsfas["fee_cents"]) == ("nsfas", 0)
    assert (nsfas["windows"][0]["status"], nsfas["windows"][0]["days"]) == ("open", 21)
    assert nsfas["warnings"]["items"][0] == "Never pay anyone to apply. NSFAS will never ask for your password or OTP."
    for guide in apply["universities"] + apply["funding"]:
        assert guide["confirmed"] is False and guide["notice"] == "Not yet confirmed by the team."
    assert apply["notes"]


def test_each_choice_shows_the_funding_its_fields_point_to(client, on_10_october):
    plan = client.post(PLAN, json={"university": "smu", "goal": "mbchb", "marks": STRONG}).get_json()["data"]["plan"]
    goal = plan["goal"]["funding"]
    assert goal["fields"] == ["health_sciences", "medicine", "medical_sciences"]
    assert 0 < len(goal["funders"]) <= 5 and goal["count"] >= len(goal["funders"])
    subject = "health sciences, medicine and medical sciences"
    assert goal["lines"][0].startswith(f"{goal['count']} funding options for {subject}, besides NSFAS: ")
    ids = [f["id"] for f in goal["funders"]]
    assert "nsfas" not in ids  # shown once, under apply
    assert all("first_year" in [s["id"] for s in f["stages"]] for f in goal["funders"])
    assert all(f["study_at"] == "any" or "smu" in f["study_at"] for f in goal["funders"])
    up_choice = plan["safe"]  # UP's BSc Medical Sciences
    assert up_choice["match"]["university"] == "up" and "up_flyup_awards" in [f["id"] for f in up_choice["funding"]["funders"]]
    assert [g["id"] for g in plan["apply"]["funding"]] == ["nsfas"]
    assert {d["who"] for d in plan["apply"]["deadlines"]} <= {"nsfas", "smu", "up"}  # no bursary dates in the plan's list


def test_a_tut_plan_shows_the_january_late_window(client, on_10_october):
    r = client.post(PLAN, json={"university": "tut", "goal": "b_nursing", "marks": STRONG})
    late, next_year = r.get_json()["data"]["plan"]["goal"]["apply"]
    assert (late["status"], late["late_opens"], late["late_closes"]) == ("late_ahead", "2027-01-14", "2027-01-22")
    assert (next_year["status"], next_year["opens"], next_year["closes"]) == ("opens_later", "2027-04-01", None)
    assert next_year["closes_one_of"] == ["2027-06-15", "2027-07-31", "2027-09-30"]


def test_points_at_every_university_before_picking_one(client):
    r = client.post(POINTS, json={"marks": STRONG})
    assert r.status_code == 200
    universities = r.get_json()["data"]["universities"]
    by_id = {u["university"]: u for u in universities}
    # In name order: none is ranked above another.
    names = [u["university_name"] for u in universities]
    assert names == sorted(names)
    assert {k: by_id[k]["points"] for k in ("smu", "tut", "up")} == {"smu": 47, "tut": 40, "up": 40}
    for u in universities:
        assert u["lines"] and u["source_url"].startswith("https://")
        assert u["confirmed"] is False and u["notice"] == "Not yet confirmed by the team."
        assert set(u["tiers"]) == {"competitive", "meets_minimum", "reach", "not_yet", "unverified"}
    for k in ("smu", "tut", "up"):
        assert by_id[k]["summary"].startswith("You meet the minimum for ")
    assert sum(by_id["smu"]["tiers"].values()) == 17
    # A university whose programmes aren't added yet: its points, and why there's nothing to meet.
    assert by_id["wits"]["points"] == 47
    assert by_id["wits"]["summary"] == "We haven't added this university's programmes yet."
    # Each subject's level and points there, in the order sent: together they make the total.
    for u in universities:
        assert [s["subject"] for s in u["subjects"]] == [m["subject"] for m in STRONG]
        assert sum(s["points"] for s in u["subjects"]) == pytest.approx(u["points"])
    tut_lo = next(s for s in by_id["tut"]["subjects"] if s["subject"] == "life_orientation")
    assert (tut_lo["level"], tut_lo["points"], tut_lo["counted"]) == (7, 0.0, False)


def test_assess_says_how_to_apply_there_on_todays_date(client, on_10_october):
    """A university's How to apply tab: its fee, documents and link, and each intake's usual dates."""
    apply = client.post(ASSESS, json={"university": "tut", "marks": STRONG}).get_json()["data"]["apply"]
    assert (apply["today"], apply["test_date"]) == ("2026-10-10", False)
    guide = apply["guide"]
    assert (guide["id"], guide["kind"], guide["confirmed"]) == ("tut", "university", False)
    late, later = guide["windows"]
    assert (late["intake"], late["status"], late["late_opens"], late["late_closes"]) == (2027, "late_ahead", "2027-01-14", "2027-01-22")
    assert (later["intake"], later["status"], later["opens"]) == (2028, "opens_later", "2027-04-01")
    assert guide["lines"] and guide["source_url"].startswith("https://")
