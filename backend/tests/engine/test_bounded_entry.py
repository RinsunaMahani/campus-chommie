import pytest
from pydantic import ValidationError

from campus_engine.matching import assess
from campus_engine.schemas import Requirements


@pytest.mark.parametrize("english,history,expected_points,tier", [
    (60, 40, 24, "reach"),
    (60, 60, 26, "reach"),
    (60, 70, 27, "reach"),
    (60, 80, 28, "unverified"),
    (50, 70, 26, "not_yet"),
    (50, 80, 27, "reach"),
    (40, 80, 26, "not_yet"),
])
def test_uj_extended_ba_published_bands(catalogue, english, history, expected_points, tier):
    uni = catalogue["uj"]
    marks = dict(english=english, history=history, mathematics=50, life_sciences=50,
                 geography=50, other_language=50)
    for programme_id in ("uj_b7ex2q", "uj_b7ex3q", "uj_b7ex4q", "uj_b7ex5q"):
        result = assess(uni, uni.programme(programme_id), marks)
        assert result.points == expected_points
        assert result.tier == tier
        if tier == "unverified":
            assert any("above those bands" in line for line in result.explanation)


def test_assessed_maximum_cannot_exclude_every_route():
    with pytest.raises(ValidationError, match="below a route minimum"):
        Requirements(source="s", min_points=28, max_assessed_points=27)
