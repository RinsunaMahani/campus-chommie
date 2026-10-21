"""Either/or subjects, percentage minimums and programme-specific points tables.

The university below is made up. Its rules copy the shapes found in real prospectuses
(docs/research): Maths or Maths Literacy with different points, two either/or choices,
options that need two subjects, percentage minimums and a programme with its own table.
"""
import pytest
from pydantic import ValidationError

from campus_engine.matching import MEETS_MINIMUM, NOT_YET, assess
from campus_engine.points import compute_points
from campus_engine.schemas import PointsRule, Requirements, University

SCALE = [
    {"min_percent": 80, "level": 7},
    {"min_percent": 70, "level": 6},
    {"min_percent": 60, "level": 5},
    {"min_percent": 50, "level": 4},
    {"min_percent": 40, "level": 3},
    {"min_percent": 30, "level": 2},
    {"min_percent": 0, "level": 1},
]
MATHS_OR_LIT = {
    "one_of": [
        {"subjects": {"mathematics": 5}},
        {"subjects": {"technical_mathematics": 5}},
        {"subjects": {"mathematical_literacy": 7}, "min_points": 28},
    ]
}


def programme(pid, requirements, **extra):
    return {"id": pid, "name": pid.replace("_", " ").title(), "requirements": {"source": "s", **requirements}, **extra}


@pytest.fixture(scope="module")
def uni():
    return University.model_validate(
        {
            "university": "routes",
            "name": "Routes University (fictional, for tests)",
            "city": "Pretoria",
            "academic_year": 2027,
            "points_rules": {
                "source": "s",
                "subjects_counted": 6,
                "life_orientation": "exclude",
                "count_from_level": 2,
                "scale": SCALE,
            },
            "programmes": [
                programme("dip_cs", {"min_points": 26, "subject_minimums": {"english": 4}, "choices": [MATHS_OR_LIT]}),
                programme(
                    "public_finance",
                    {
                        "min_points": 22,
                        "subject_minimums": {"english": 4},
                        "choices": [
                            {
                                "one_of": [
                                    {"subjects": {"accounting": 4}, "min_points": 23},
                                    {"subjects": {"mathematics": 3}},
                                    {"subjects": {"mathematical_literacy": 5}, "min_points": 24},
                                ]
                            }
                        ],
                    },
                ),
                programme(
                    "engtech",
                    {
                        "min_points": 28,
                        "subject_minimums": {"english": 4},
                        "choices": [
                            {"one_of": [{"subjects": {"mathematics": 5}}, {"subjects": {"technical_mathematics": 5}}]},
                            {"one_of": [{"subjects": {"physical_sciences": 5}}, {"subjects": {"technical_sciences": 5}}]},
                        ],
                    },
                ),
                programme(
                    "bed_maths",
                    {
                        "min_points": 24,
                        "subject_minimums": {"english": 4},
                        "choices": [
                            {
                                "one_of": [
                                    {"subjects": {"mathematics": 4, "life_sciences": 4}},
                                    {"subjects": {"mathematics": 4, "physical_sciences": 4}},
                                ]
                            }
                        ],
                    },
                ),
                programme(
                    "beng_extended",
                    {"min_points": 33, "subject_min_percents": {"english": 65, "mathematics": 65, "physical_sciences": 65}},
                ),
                programme(
                    "oral_hygiene",
                    {
                        "min_points": 20,
                        "subject_minimums": {"english": 4},
                        "choices": [
                            {"one_of": [{"subjects": {"mathematics": 4}}, {"subjects": {"mathematical_literacy": 7}}]}
                        ],
                        "additional_minimums": [4, 4],
                    },
                ),
                programme(
                    "pharmacy",
                    {"min_points": 32, "subject_minimums": {"english": 5, "mathematics": 5}},
                    points_rules={
                        "source": "s",
                        "subjects_counted": 7,
                        "life_orientation": "full",
                        "scale": [{"min_percent": 90, "level": 8}] + SCALE,
                    },
                ),
            ],
            "sources": [{"id": "s", "url": "https://example.org", "publisher": "Routes"}],
        }
    )


OTHERS = {"geography": 60, "history": 60, "life_sciences": 60, "life_orientation": 90}


def test_maths_route_keeps_the_programme_minimum(uni):
    marks = {"english": 55, "mathematics": 65, "physical_sciences": 60, **OTHERS}  # 4+5+5+5+5+5 = 29
    m = assess(uni, uni.programme("dip_cs"), marks)
    assert m.tier == MEETS_MINIMUM
    assert m.min_points == 26
    assert "Counted Mathematics (level 5) for an either/or requirement." in m.explanation
    assert not any("instead of" in line for line in m.explanation)


def test_maths_literacy_route_needs_more_points(uni):
    marks = {"english": 55, "mathematical_literacy": 80, "geography": 55, "history": 55, "life_sciences": 55, "tourism": 50}
    m = assess(uni, uni.programme("dip_cs"), marks)  # 4+7+4+4+4+4 = 27
    assert m.tier == NOT_YET
    assert (m.points, m.min_points, m.gap) == (27, 28, 1)
    assert m.explanation[0] == "Your points: 27 (minimum 28)."
    assert "With Mathematical literacy level 7, the minimum is 28 points instead of 26." in m.explanation
    assert "You need 1 more point to meet the minimum." in m.explanation


def test_unmet_choice_names_every_option_and_what_the_learner_has(uni):
    marks = {"english": 55, "mathematical_literacy": 75, **OTHERS}
    m = assess(uni, uni.programme("dip_cs"), marks)
    assert m.tier == NOT_YET
    assert (
        "Needs one of: Mathematics level 5, Technical mathematics level 5 or Mathematical literacy level 7. "
        "You have Mathematical literacy at level 6."
    ) in m.failed


def test_the_route_with_the_lowest_minimum_is_used(uni):
    both = {"english": 55, "accounting": 55, "mathematics": 45, **OTHERS}
    m = assess(uni, uni.programme("public_finance"), both)
    assert m.min_points == 22
    assert "Counted Mathematics (level 3) for an either/or requirement." in m.explanation

    accounting_only = {"english": 55, "accounting": 55, **OTHERS}
    m = assess(uni, uni.programme("public_finance"), accounting_only)
    assert m.min_points == 23
    assert "With Accounting level 4, the minimum is 23 points instead of 22." in m.explanation


def test_every_choice_must_be_met(uni):
    technical = {"english": 55, "technical_mathematics": 65, "technical_sciences": 60, **OTHERS}
    m = assess(uni, uni.programme("engtech"), technical)  # 4+5+5+5+5+5 = 29
    assert m.tier == MEETS_MINIMUM
    assert sum("for an either/or requirement" in line for line in m.explanation) == 2

    no_science = {"english": 55, "technical_mathematics": 65, **OTHERS}
    m = assess(uni, uni.programme("engtech"), no_science)
    assert m.tier == NOT_YET
    assert "Needs one of: Physical sciences level 5 or Technical sciences level 5." in m.failed


def test_an_option_can_need_two_subjects(uni):
    marks = {"english": 55, "mathematics": 50, "physical_sciences": 50, "life_sciences": 40, "geography": 60, "history": 60}
    m = assess(uni, uni.programme("bed_maths"), marks)  # 4+4+4+3+5+5 = 25
    assert m.tier == MEETS_MINIMUM
    assert "Counted Mathematics (level 4) and Physical sciences (level 4) for an either/or requirement." in m.explanation

    marks = dict(marks, physical_sciences=40)
    m = assess(uni, uni.programme("bed_maths"), marks)
    assert m.tier == NOT_YET
    assert m.failed[0].startswith(
        "Needs one of: Mathematics level 4 and Life sciences level 4; or Mathematics level 4 and Physical sciences level 4."
    )


def test_percentage_minimums(uni):
    beng = uni.programme("beng_extended")
    meets = {"english": 65, "mathematics": 65, "physical_sciences": 65, "geography": 70, "history": 70, "accounting": 70}
    assert assess(uni, beng, meets).tier == MEETS_MINIMUM  # 5+5+5+6+6+6 = 33

    m = assess(uni, beng, dict(meets, english=64.5))
    assert "English: 64.5%, needs 65%." in m.failed
    m = assess(uni, beng, {k: v for k, v in meets.items() if k != "physical_sciences"})
    assert "Physical sciences is required (65% or higher)." in m.failed


def test_the_counted_option_is_not_an_additional_subject(uni):
    marks = {"english": 55, "mathematical_literacy": 80, "geography": 55, "history": 45}
    m = assess(uni, uni.programme("oral_hygiene"), marks)
    # Without Maths Literacy, the additional subjects are Geography (4) and History (3).
    assert "Additional subject 2: level 3, needs 4." in m.failed


def test_a_programme_can_use_its_own_points_table(uni):
    marks = {
        "english": 92,
        "mathematics": 92,
        "physical_sciences": 60,
        "life_sciences": 60,
        "life_orientation": 50,
        "geography": 50,
        "history": 50,
    }
    m = assess(uni, uni.programme("pharmacy"), marks)
    assert m.points == 8 + 8 + 5 + 5 + 4 + 4 + 4  # the university's own rule would give 7+7+5+5+4+4 = 32
    assert "This programme uses its own points table, not the university's usual one." in m.explanation


def test_a_points_rule_can_carry_a_note():
    rule = PointsRule(source="s", subjects_counted=6, life_orientation="exclude", note="We assume six subjects.", scale=SCALE)
    assert "We assume six subjects." in compute_points({"english": 80}, rule).notes


def test_subjects_below_the_lowest_counted_level_add_nothing():
    rule = PointsRule(source="s", subjects_counted=3, life_orientation="exclude", count_from_level=2, scale=SCALE)
    result = compute_points({"english": 80, "history": 60, "mathematics": 25}, rule)
    assert result.total == 7 + 5 + 0
    assert "Subjects below level 2 add no points here." in result.notes
    assert not any("below level" in n for n in compute_points({"english": 80}, rule).notes)


@pytest.mark.parametrize(
    "requirements,message",
    [
        ({"min_points": 20, "subject_minimums": {"maths": 4}}, "unknown subject 'maths'"),
        (
            {"min_points": 20, "subject_minimums": {"mathematics": 4}, "choices": [MATHS_OR_LIT]},
            "'mathematics' appears in more than one rule (a minimum level, choice 1)",
        ),
        (
            {"min_points": 20, "subject_minimums": {"english": 4}, "subject_min_percents": {"english": 65}},
            "'english' appears in more than one rule",
        ),
        ({"min_points": 30, "competitive_points": 25}, "competitive_points is below min_points"),
        ({"min_points": 20, "choices": [{"one_of": [{"subjects": {"mathematics": 4}}]}]}, "at least 2 items"),
        ({"min_points": 20, "subject_minimums": {"english": 9}}, "less than or equal to 8"),
        ({"min_points": 20, "subject_min_percents": {"english": 101}}, "less than or equal to 100"),
        ({"min_points": 20, "choices": [{"one_of": [{"subjects": {}}, {"subjects": {"english": 4}}]}]}, "at least 1 item"),
        ({"min_points": -1}, "greater than or equal to 0"),
        ({"min_points": 20, "unknown_field": 1}, "Extra inputs are not permitted"),
    ],
)
def test_requirements_that_cannot_be_right_are_rejected(requirements, message):
    with pytest.raises(ValidationError) as exc:
        Requirements.model_validate({"source": "s", **requirements})
    assert message in str(exc.value)


def test_a_programme_points_table_must_cite_a_known_source():
    with pytest.raises(ValidationError) as exc:
        University.model_validate(
            {
                "university": "u",
                "name": "U",
                "city": "Pretoria",
                "academic_year": 2027,
                "programmes": [
                    {"id": "p", "name": "P", "points_rules": {"source": "missing", "scale": SCALE}},
                ],
                "sources": [],
            }
        )
    assert "p: points_rules cite unknown source 'missing'" in str(exc.value)
