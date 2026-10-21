import pytest

from campus_engine.matching import (
    COMPETITIVE,
    MEETS_MINIMUM,
    NO_GUARANTEE,
    NOT_YET,
    REACH,
    TIER_RANK,
    UNVERIFIED,
    assess,
    assess_all,
)
from campus_engine.schemas import University

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
