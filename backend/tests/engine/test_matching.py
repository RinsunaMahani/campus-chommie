import pytest
from pydantic import ValidationError

from campus_engine.matching import (
    COMPETITIVE,
    MEETS_MINIMUM,
    NO_GUARANTEE,
    NOT_YET,
    REACH,
    SUBJECTS_MET,
    TIER_RANK,
    UNVERIFIED,
    assess,
    assess_all,
)
from campus_engine.schemas import Choice, Programme, Requirements, University

SCALE = [
    {"min_percent": 80, "level": 7},
    {"min_percent": 70, "level": 6},
    {"min_percent": 60, "level": 5},
    {"min_percent": 50, "level": 4},
    {"min_percent": 40, "level": 3},
    {"min_percent": 30, "level": 2},
    {"min_percent": 0, "level": 1},
]


@pytest.fixture
def open_uni():
    """A made-up university with a non-selective programme and a published cut-off."""
    return University.model_validate(
        {
            "university": "test",
            "name": "Test University",
            "city": "Pretoria",
            "academic_year": 2027,
            "points_rules": {"source": "s", "subjects_counted": 6, "life_orientation": "exclude", "scale": SCALE},
            "programmes": [
                {
                    "id": "bcom",
                    "name": "BCom",
                    "fields": ["commerce"],
                    "requirements": {
                        "source": "s",
                        "min_points": 28,
                        "competitive_points": 34,
                        "subject_minimums": {"mathematics": 4},
                    },
                }
            ],
            "sources": [{"id": "s", "url": "https://example.org", "publisher": "Test"}],
        }
    )


def test_strong_learner_is_a_reach_for_selective_mbchb(smu, strong_marks):
    m = assess(smu, smu.programme("mbchb"), strong_marks)
    assert m.tier == REACH
    assert m.points == 47
    assert NO_GUARANTEE in m.explanation
    assert m.source_url.startswith("https://www.smu.ac.za/")


def test_one_subject_below_minimum_is_not_yet(smu, strong_marks):
    marks = dict(strong_marks, mathematics=65)  # level 5, MBChB needs 6
    m = assess(smu, smu.programme("mbchb"), marks)
    assert m.tier == NOT_YET
    assert "Mathematics: level 5, needs 6." in m.failed


def test_missing_required_subject_is_named(smu, strong_marks):
    marks = {k: v for k, v in strong_marks.items() if k != "physical_sciences"}
    m = assess(smu, smu.programme("brad"), marks)
    assert m.tier == NOT_YET
    assert any("Physical sciences is required" in f for f in m.failed)


def test_unverified_programme(smu, strong_marks):
    unchecked = smu.programme("brad").model_copy(update={"requirements": None, "selection_note": "Ask about auditions."})
    m = assess(smu, unchecked, strong_marks)
    assert m.tier == UNVERIFIED
    assert m.points is None
    assert m.explanation[0].startswith("We can't check this programme's requirements against your marks yet.")
    assert m.explanation[1] == "Ask about auditions."


def test_gap_in_points_is_reported(open_uni):
    marks = {"mathematics": 55, "english": 55, "geography": 55, "history": 55, "accounting": 55, "economics": 55}
    m = assess(open_uni, open_uni.programme("bcom"), marks)  # 6 x level 4 = 24
    assert m.tier == NOT_YET
    assert m.gap == 4
    assert any("4 more points" in line for line in m.explanation)


def test_meets_minimum_and_competitive(open_uni):
    meets = {"mathematics": 65, "english": 65, "geography": 60, "history": 60, "accounting": 50, "economics": 50}
    strong = {"mathematics": 75, "english": 75, "geography": 70, "history": 70, "accounting": 70, "economics": 60}
    assert assess(open_uni, open_uni.programme("bcom"), meets).tier == MEETS_MINIMUM  # 28 points
    assert assess(open_uni, open_uni.programme("bcom"), strong).tier == COMPETITIVE  # 35 points


def test_assess_all_puts_best_tiers_first(smu, strong_marks):
    weaker = dict(strong_marks, mathematics=55)  # level 4: below MBChB's 6, enough for others
    ranks = [TIER_RANK[m.tier] for m in assess_all(smu, weaker)]
    assert ranks == sorted(ranks)
    assert ranks[0] == TIER_RANK[REACH] and ranks[-1] == TIER_RANK[NOT_YET]


def _no_minimum(uni, **update):
    """open_uni's BCom as if the university published no points minimum for it."""
    bcom = uni.programme("bcom")
    req = bcom.requirements.model_copy(update={"min_points": None, "competitive_points": None, **update})
    return bcom.model_copy(update={"requirements": req})


def test_min_points_is_required_but_may_say_nothing_is_published():
    with pytest.raises(ValidationError):
        Requirements.model_validate({"source": "s"})
    assert Requirements.model_validate({"source": "s", "min_points": None}).min_points is None


def test_no_published_minimum_checks_the_subjects_only(open_uni):
    marks = {"mathematics": 55, "english": 45, "geography": 40, "history": 40, "accounting": 40, "economics": 40}
    m = assess(open_uni, _no_minimum(open_uni), marks)  # 4 + 5 x 3 = 19 points: low, but no minimum is published
    assert (m.tier, m.points, m.min_points, m.gap) == (MEETS_MINIMUM, 19, None, None)
    assert m.explanation[0] == (
        "Your points: 19. The university publishes no points minimum for this programme, "
        "so only your subjects were checked."
    )
    assert m.explanation[-1] == NO_GUARANTEE


def test_no_published_minimum_still_needs_the_subjects(open_uni):
    marks = {"mathematics": 45, "english": 75, "geography": 75, "history": 75, "accounting": 75, "economics": 75}
    m = assess(open_uni, _no_minimum(open_uni), marks)
    assert (m.tier, m.gap) == (NOT_YET, None)
    assert "Mathematics: level 3, needs 4." in m.explanation


def test_a_route_can_publish_a_minimum_the_programme_doesnt(open_uni):
    either = Choice.model_validate(
        {"one_of": [{"subjects": {"mathematics": 4}}, {"subjects": {"mathematical_literacy": 5}, "min_points": 22}]}
    )
    programme = _no_minimum(open_uni, subject_minimums={}, choices=[either])
    marks = {"mathematical_literacy": 65, "english": 55, "geography": 55, "history": 55, "accounting": 55}
    m = assess(open_uni, programme, marks)  # 5 + 4 x 4 = 21 points: one short of the route's 22
    assert (m.tier, m.min_points, m.gap) == (NOT_YET, 22, 1)
    assert "With Mathematical literacy level 5, the minimum is 22 points." in m.explanation


def test_a_result_names_its_faculty_and_fields(open_uni):
    bcom = open_uni.programme("bcom").model_copy(update={"faculty": "Faculty of Commerce"})
    m = assess(open_uni, bcom, {"mathematics": 65, "english": 65})
    assert (m.faculty, m.fields) == ("Faculty of Commerce", ["commerce"])
    assert assess(open_uni, open_uni.programme("bcom"), {"mathematics": 65}).faculty is None


def test_a_faculty_name_is_never_empty():
    with pytest.raises(ValidationError):
        Programme.model_validate({"id": "x", "name": "X", "faculty": ""})



def _no_rule_uni(**extra) -> University:
    """A made-up university that counts points its own way (no rule we can apply), like CUT or Stellenbosch."""
    return University.model_validate({
        "university": "own", "name": "Own Way University", "city": "Kimberley", "academic_year": 2027,
        "points_rules": None,
        "programmes": [
            {"id": "bsc", "name": "BSc", "requirements": {
                "source": "s", "min_points": 30, "subject_minimums": {"mathematics": 5},
                "choices": [{"one_of": [{"subjects": {"physical_sciences": 4}}, {"subjects": {"life_sciences": 4}}]}],
            }},
            {"id": "none", "name": "Not added", "requirements": None},
        ],
        "sources": [{"id": "s", "url": "https://example.org/own", "publisher": "Own"}],
    } | extra)


def test_without_a_points_rule_subjects_are_still_checked_on_the_national_levels():
    uni = _no_rule_uni(points_how={"source": "s", "text": "Own Way counts 2 to 8 points a subject."})
    m = assess(uni, uni.programme("bsc"), {"mathematics": 62, "life_sciences": 55, "english": 70})
    assert m.tier == SUBJECTS_MET and m.label == "Subjects met" and m.points is None
    assert m.explanation[0] == "Your subjects meet this programme's minimums."
    assert "It also asks for 30 points, counted Own Way University's own way, which we can't add up for you." in m.explanation
    assert "Own Way counts 2 to 8 points a subject." in m.explanation and m.explanation[-1] == NO_GUARANTEE
    assert m.source_url == "https://example.org/own"
    assert assess(uni, uni.programme("none"), {}).tier == UNVERIFIED  # nothing published to check


def test_without_a_points_rule_a_missing_subject_is_still_not_yet():
    uni = _no_rule_uni()
    m = assess(uni, uni.programme("bsc"), {"mathematics": 55, "english": 70})
    assert m.tier == NOT_YET
    assert "Mathematics: level 4, needs 5." in m.failed
    assert m.failed[1].startswith("Needs one of: Physical sciences level 4 or Life sciences level 4.")


def test_where_a_university_selects_on_an_average_the_learner_sees_theirs():
    uni = _no_rule_uni(points_how={"source": "s", "text": "Selects on your average.", "average_of_best": 3})
    marks = {"mathematics": 80, "life_sciences": 70, "english": 60, "geography": 50, "life_orientation": 95}
    m = assess(uni, uni.programme("bsc"), marks)
    assert "Your average of your best 3 subjects, without Life Orientation: 70%." in m.explanation
    few = assess(uni, uni.programme("bsc"), {"mathematics": 80, "life_sciences": 70})
    assert not any("Your average" in line for line in few.explanation)  # fewer subjects than it averages


def test_subjects_met_ranks_after_the_points_checked_tiers():
    assert TIER_RANK[REACH] < TIER_RANK[SUBJECTS_MET] < TIER_RANK[UNVERIFIED] < TIER_RANK[NOT_YET]
