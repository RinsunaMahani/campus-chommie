"""
Spot checks on the shipped data packs against their sources (docs/research/*.md give the
document and page). A failing check means a pack and its source disagree: fix whichever is
wrong, with the source in hand, never the test alone.
"""
from __future__ import annotations

from datetime import date

import pytest

from campus_engine.applications import CLOSED, apply_guide
from campus_engine.bridges import build_plan
from campus_engine.catalogue import load_funding
from campus_engine.matching import COMPETITIVE, MEETS_MINIMUM, NOT_YET, REACH, assess
from campus_engine.points import compute_points

STRONG = {
    "english": 82,
    "mathematics": 81,
    "physical_sciences": 80,
    "life_sciences": 85,
    "life_orientation": 88,
    "geography": 74,
    "other_language": 79,
}


@pytest.fixture(scope="module")
def up(catalogue):
    return catalogue["up"]


@pytest.fixture(scope="module")
def tut(catalogue):
    return catalogue["tut"]


@pytest.fixture(scope="module")
def smu(catalogue):
    return catalogue["smu"]


def test_every_draft_pack_stays_unreleased_until_a_person_checks_it(catalogue):
    for uni in ("up", "tut"):
        pack = catalogue[uni]
        assert pack.release is False
        assert all(s.verified_by == "agent draft, needs human check" for s in pack.sources)


# UP: s-up-req-2027 (2027 requirements tables) and s-up-mbchb-2027 (MBChB selection)


def test_up_counts_six_subjects_without_life_orientation(up):
    result = compute_points(STRONG, up.points_rules)
    assert result.total == 7 + 7 + 7 + 7 + 6 + 6  # highest possible is 42
    assert "life_orientation" not in result.counted


@pytest.mark.parametrize(
    "pid,aps,minimums",
    [
        ("mbchb", 35, {"english": 5, "mathematics": 6, "physical_sciences": 5}),
        ("bds", 35, {"english": 5, "mathematics": 6, "physical_sciences": 5}),
        ("llb", 35, {"english": 6}),
        ("beng_civil", 35, {"english": 5, "mathematics": 6, "physical_sciences": 6}),
        ("bcom_accounting_sciences", 34, {"english": 5, "mathematics": 6}),
        ("bsc_computer_science", 30, {"english": 5, "mathematics": 6}),
        ("b_nursing", 28, {"english": 4, "mathematics": 4, "life_sciences": 4}),
        ("bsc_actuarial_financial_mathematics", 36, {"english": 5, "mathematics": 7}),
        ("dip_theology", 24, {"english": 4}),
    ],
)
def test_up_minimums_match_the_requirements_tables(up, pid, aps, minimums):
    req = up.programme(pid).requirements
    assert (req.min_points, req.subject_minimums) == (aps, minimums)


def test_up_extended_programmes_use_percentages(up):
    assert up.programme("beng_extended").requirements.subject_min_percents == {
        "english": 65, "mathematics": 65, "physical_sciences": 65,
    }
    assert up.programme("bsc_mathematics_extended").requirements.subject_min_percents == {"english": 58, "mathematics": 65}


def test_up_badmin_takes_maths_or_maths_literacy(up):
    marks = {"english": 65, "mathematical_literacy": 55, "geography": 65, "history": 65, "economics": 60, "tourism": 60}
    m = assess(up, up.programme("badmin_public_admin"), marks)  # 5+4+5+5+5+5 = 29
    assert m.tier == MEETS_MINIMUM


def test_up_mbchb_places_and_route_after_a_degree_year(up):
    mbchb = up.programme("mbchb")
    assert mbchb.places == 300 and mbchb.selective
    route = up.programme("bsc_medical_sciences").bridges_to[0]
    assert (route.to, route.guarantee, route.max_places) == ("mbchb", "considered", 36)
    assert "66 more for designated groups" in route.eligibility_note


def test_up_rules_the_schema_cannot_hold_yet_stay_unverified(up):
    for pid in ("bmus", "bmus_extended", "bconsumer_food_management"):
        assert up.programme(pid).requirements is None


# TUT: s-tut-courses-2027 (course list), s-tut-guide-2027 (programme pages), s-tut-rules-2026 (APS rule)


def test_tut_excludes_life_orientation_scores_level_one_as_nothing_and_says_what_it_assumes(tut):
    marks = dict(STRONG, geography=25)  # level 1
    result = compute_points(marks, tut.points_rules)
    assert result.total == 7 + 7 + 7 + 7 + 6 + 0
    assert any("we count the six besides Life Orientation" in n for n in result.notes)


def test_tut_computer_science_asks_more_points_with_maths_literacy(tut):
    dip = tut.programme("dip_computer_science")
    others = {"english": 55, "geography": 65, "history": 55, "tourism": 55, "life_sciences": 55}
    m = assess(tut, dip, dict(others, geography=55, mathematical_literacy=82))  # 4+7+4+4+4+4 = 27
    assert (m.tier, m.min_points) == (NOT_YET, 28)
    m = assess(tut, dip, dict(others, mathematics=65))  # 4+5+5+4+4+4 = 26
    assert (m.tier, m.min_points) == (MEETS_MINIMUM, 26)


def test_tut_nursing_band_and_published_cut_off(tut):
    nursing = tut.programme("b_nursing").requirements
    assert (nursing.min_points, nursing.competitive_points) == (27, 30)
    m = assess(tut, tut.programme("b_nursing"), STRONG)
    assert m.tier == COMPETITIVE


def test_tut_management_diplomas_admit_from_24_and_test_from_20(tut):
    req = tut.programme("dip_hospitality").requirements
    assert (req.min_points, req.competitive_points) == (20, 24)
    assert tut.programme("dip_marketing").requirements.min_points == 24


def test_tut_leaves_out_programmes_only_for_people_already_employed(tut):
    with pytest.raises(KeyError):
        tut.programme("dip_fire_technology")


# SMU: s-smu-apply-2027, s-smu-med, s-smu-dent, s-smu-pharm, s-smu-hcs, s-smu-sst


def test_smu_application_and_mbchb_facts(smu):
    assert smu.max_choices == 2
    assert smu.programme("mbchb").places == 250
    assert smu.programme("bds").places == 42


def test_smu_bsc_counts_six_subjects_without_life_orientation(smu):
    bsc = smu.programme("bsc_y1")
    assert bsc.requirements.min_points == 25
    assert bsc.points_rules.life_orientation == "exclude" and bsc.points_rules.subjects_counted == 6
    assert assess(smu, bsc, STRONG).points == 7 + 7 + 7 + 7 + 6 + 6


def test_smu_pharmacy_scores_90_percent_as_8(smu):
    marks = dict(STRONG, english=92, mathematics=91)
    assert assess(smu, smu.programme("bpharm"), marks).points == 8 + 8 + 7 + 7 + 7 + 6 + 6


def test_smu_oral_hygiene_asks_31_points_with_maths_literacy(smu):
    boh = smu.programme("boh").requirements
    lit = next(o for o in boh.choices[0].one_of if "mathematical_literacy" in o.subjects)
    assert (boh.min_points, lit.subjects["mathematical_literacy"], lit.min_points) == (28, 7, 31)


def test_smu_foundation_year_note_uses_smus_own_words(smu):
    note = smu.programme("mbchb_ecp").bridges_to[0].eligibility_note
    assert note.startswith("In SMU's words")


# Across the packs: the plan's safer related choice (decided 9 Oct 2026: tag fields honestly)


def test_an_smu_mbchb_goal_gets_ups_bsc_medical_sciences_as_the_safer_choice(catalogue):
    plan = build_plan(catalogue, "smu", "mbchb", STRONG)
    assert plan.goal.match.tier == REACH
    assert plan.bridge.match.programme_id == "bsc_y1"
    assert (plan.safe.match.university, plan.safe.match.programme_id) == ("up", "bsc_medical_sciences")
    assert plan.safe.match.tier == MEETS_MINIMUM
    assert plan.safe.notes[0].endswith("through health sciences and medical sciences.")


# How to apply: s-up-req-2027, s-tut-cal-2026, s-tut-courses-2027, s-tut-cal-2027, s-tut-guide-2027,
# s-smu-apply-2027, and NSFAS's 2027 pages (s-nsfas-apply-2027, s-nsfas-home-2027)


def test_up_closes_on_30_june_and_veterinary_science_on_31_may(up):
    window = up.applications.windows[0]
    assert (window.intake, window.opens, window.closes) == (2027, None, date(2026, 6, 30))
    assert [(g.closes, g.programmes) for g in window.programme_closes] == [(date(2026, 5, 31), ["bvsc", "b_veterinary_nursing"])]
    # UP's own application page couldn't be read: nothing from it is in the pack.
    apps = up.applications
    assert (apps.url, apps.fee_cents, apps.documents) == (None, None, None)


def test_tut_closing_dates_follow_the_course_list_and_the_calendar(tut):
    window = next(w for w in tut.applications.windows if w.intake == 2027)
    assert (window.opens, window.closes) == (date(2026, 4, 1), date(2026, 9, 30))
    groups = {g.closes: g.programmes for g in window.programme_closes}
    assert len(groups[date(2026, 6, 15)]) == 7 and "b_nursing" in groups[date(2026, 6, 15)]
    assert len(groups[date(2026, 7, 31)]) == 54 and "dip_economics" in groups[date(2026, 7, 31)]
    assert (window.late.opens, window.late.closes) == (date(2027, 1, 14), date(2027, 1, 22))
    later = next(w for w in tut.applications.windows if w.intake == 2028)
    assert later.opens == date(2027, 4, 1) and later.closes is None
    assert later.closes_one_of == [date(2027, 6, 15), date(2027, 7, 31), date(2027, 9, 30)]


def test_tut_fee_and_documents(tut):
    apps = tut.applications
    assert apps.fee_cents == 24000
    assert len(apps.documents.items) == 3


def test_smu_closed_on_31_july_with_no_late_applications(smu):
    apps = smu.applications
    window = apps.windows[0]
    assert (window.intake, window.opens, window.closes, window.no_late_applications) == (
        2027, date(2026, 4, 1), date(2026, 7, 31), True
    )
    assert apps.fee_cents == 30000 and len(apps.documents.items) == 5


def test_nsfas_2027_window_and_free_application():
    funding = load_funding()
    assert funding.release is False
    assert all(s.verified_by == "agent draft, needs human check" for s in funding.sources)
    nsfas = funding.funder("nsfas")
    window = nsfas.applications.windows[0]
    assert (window.intake, window.opens, window.closes, window.closing_time) == (
        2027, date(2026, 9, 18), date(2026, 10, 31), "23:59"
    )
    assert window.no_late_applications and nsfas.applications.fee_cents == 0
    assert len(nsfas.tips.items) == 8  # NSFAS's "eight most common reasons a document is sent back"


def test_on_10_october_2026_the_smu_learner_should_apply_to_nsfas_first(catalogue):
    guide = apply_guide(catalogue, load_funding(), build_plan(catalogue, "smu", "mbchb", STRONG), date(2026, 10, 10))
    first = guide.deadlines[0]
    assert (first.on, first.days, first.text) == (date(2026, 10, 31), 21, "NSFAS: applications for 2027 funding close at 23:59.")
    goal_2027 = guide.windows[("smu", "mbchb")][0]
    assert (goal_2027.intake, goal_2027.status) == (2027, CLOSED)
    assert goal_2027.lines == ["Closed on Fri 31 Jul 2026.", "No late applications."]
