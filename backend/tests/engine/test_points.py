import pytest

from campus_engine.points import compute_points, level_for
from campus_engine.schemas import PointsRule

SEVEN_LEVELS = [
    {"min_percent": 80, "level": 7},
    {"min_percent": 70, "level": 6},
    {"min_percent": 60, "level": 5},
    {"min_percent": 50, "level": 4},
    {"min_percent": 40, "level": 3},
    {"min_percent": 30, "level": 2},
    {"min_percent": 0, "level": 1},
]


@pytest.mark.parametrize(
    "percent,level",
    [(100, 7), (80, 7), (79.9, 6), (70, 6), (60, 5), (50, 4), (40, 3), (30, 2), (29, 1), (0, 1)],
)
def test_smu_scale(smu, percent, level):
    assert level_for(percent, smu.points_rules) == level


def test_percentages_outside_0_to_100_are_rejected(smu):
    with pytest.raises(ValueError):
        level_for(101, smu.points_rules)
    with pytest.raises(ValueError):
        level_for(-1, smu.points_rules)


def test_exact_mbchb_minimum_profile_scores_38(smu):
    marks = {
        "english": 70,
        "mathematics": 70,
        "physical_sciences": 70,
        "life_sciences": 70,
        "life_orientation": 60,
        "geography": 60,
        "history": 50,
    }
    result = compute_points(marks, smu.points_rules)
    assert result.total == 38  # 6+6+6+6 + LO 5 + 5 + 4
    assert "life_orientation" in result.counted


def test_only_the_best_subjects_count(smu, strong_marks):
    marks = dict(strong_marks, accounting=35)  # an eighth, weaker subject must not count
    result = compute_points(marks, smu.points_rules)
    assert result.total == 47
    assert "accounting" not in result.counted


def test_missing_subjects_are_noted(smu):
    result = compute_points({"english": 80, "mathematics": 80}, smu.points_rules)
    assert result.total == 14
    assert any("this university counts 7" in n for n in result.notes)


def test_life_orientation_half_and_excluded():
    marks = {"english": 80, "mathematics": 80, "life_orientation": 80}
    half = PointsRule(source="s", subjects_counted=3, life_orientation="half", scale=SEVEN_LEVELS)
    excluded = PointsRule(source="s", subjects_counted=2, life_orientation="exclude", scale=SEVEN_LEVELS)
    assert compute_points(marks, half).total == 7 + 7 + 3.5
    assert compute_points(marks, excluded).total == 14
    assert "life_orientation" not in compute_points(marks, excluded).counted


def test_scale_must_start_at_zero():
    with pytest.raises(ValueError):
        PointsRule(source="s", scale=[{"min_percent": 50, "level": 4}])
