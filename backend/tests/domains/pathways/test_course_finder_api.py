"""
The course finder end to end: marks in, tier cards and the three-choice plan
out, each with its plain-words reasons and source. No account needed.
"""
from __future__ import annotations

from course_finder_helpers import ASSESS, PLAN, STRONG, marks


def test_m1_acceptance_the_strong_smu_learners_plan(client):
    """The brief's M1 check. It holds while SMU is the only pack; once UP's pack lands, the
    team agreed (9 Oct 2026) that slot 3 moves to the related programme without competitive
    selection, so this test changes with it."""
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

    assert plan["safe"]["match"]["programme"] == "brad"
    assert any("not a safe choice yet" in n for n in plan["safe"]["notes"])


def test_every_card_has_its_reasons_source_and_check_status(client):
    r = client.post(PLAN, json={"university": "smu", "goal": "mbchb", "marks": STRONG})
    plan = r.get_json()["data"]["plan"]
    for slot in [plan["goal"], plan["bridge"], plan["safe"], *plan["other_routes"]]:
        match = slot["match"]
        assert match["explanation"]
        assert match["confirmed"] is False and match["notice"] == "Not yet confirmed by the team."
        if match["tier"] != "unverified":
            assert match["source_url"].startswith("https://www.smu.ac.za/")
    assert plan["bridge"]["bridge"]["source_url"].startswith("https://www.smu.ac.za/")


def test_assess_lists_every_programme_best_tiers_first(client):
    r = client.post(ASSESS, json={"university": "smu", "marks": STRONG})
    assert r.status_code == 200
    data = r.get_json()["data"]
    assert data["university"]["id"] == "smu" and data["university"]["confirmed"] is False
    tiers = [m["tier"] for m in data["matches"]]
    assert tiers[0] == "reach" and tiers[-1] == "unverified"
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
