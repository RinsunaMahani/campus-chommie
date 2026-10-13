"""
Your points at every university: each counted by its own rule, in name order, with how many
programmes the marks meet and how that university counts.
"""
from __future__ import annotations

from campus_engine.matching import COMPETITIVE, MEETS_MINIMUM, NOT_YET, REACH, UNVERIFIED
from campus_engine.overview import _how, _summary, points_everywhere, university_points
from campus_engine.schemas import PointsRule, University


def test_the_same_marks_give_each_universitys_own_points(catalogue, strong_marks):
    points = {u.university: u.points for u in points_everywhere(catalogue, strong_marks)}
    # SMU counts seven subjects with Life Orientation; UP and TUT count six without it.
    assert points == {"smu": 47, "tut": 40, "up": 40}


def test_universities_come_in_name_order_so_none_is_ranked_above_another(catalogue, strong_marks):
    names = [u.name for u in points_everywhere(catalogue, strong_marks)]
    assert names == sorted(names)


def test_every_programme_is_counted_in_one_tier(catalogue, strong_marks):
    for u in points_everywhere(catalogue, strong_marks):
        assert sum(u.tiers.values()) == len(catalogue[u.university].programmes)


def test_each_university_says_how_it_counts(catalogue, strong_marks):
    by_id = {u.university: u for u in points_everywhere(catalogue, strong_marks)}
    assert by_id["smu"].lines[0] == "Counts 7 subjects: Life Orientation and your best 6 others."
    assert by_id["up"].lines[0] == "Counts your best 6 subjects, leaving out Life Orientation."
    assert any("until TUT confirms" in line for line in by_id["tut"].lines)
    # SMU Pharmacy and the BSc count their own way: say so instead of hiding it.
    assert by_id["smu"].lines[-1] == "Some programmes count points their own way: their cards show those points."
    assert by_id["up"].source_url.startswith("https://")


def test_a_reach_programme_counts_as_meeting_the_minimum(catalogue, strong_marks):
    smu = university_points(catalogue["smu"], strong_marks)
    assert smu.tiers[REACH] == 17
    assert smu.summary == "You meet the minimum for 17 of 17 programmes. 17 of them select competitively, so each is a reach."


def test_the_summary_in_plain_words():
    tiers = {COMPETITIVE: 1, MEETS_MINIMUM: 2, REACH: 1, UNVERIFIED: 2, NOT_YET: 4}
    assert _summary(tiers) == (
        "You meet the minimum for 4 of 10 programmes. 1 of them selects competitively, so it's a reach. "
        "We can't check 2 yet."
    )
    assert _summary({COMPETITIVE: 0, MEETS_MINIMUM: 0, REACH: 0, UNVERIFIED: 0, NOT_YET: 1}) == (
        "You meet the minimum for 0 of 1 programme."
    )
    # A university whose programmes we haven't added yet: its points still show.
    assert _summary({COMPETITIVE: 0, MEETS_MINIMUM: 0, REACH: 0, UNVERIFIED: 0, NOT_YET: 0}) == (
        "We haven't added this university's programmes yet."
    )


def test_each_subjects_level_and_points_add_up_to_the_total(catalogue, strong_marks):
    for u in points_everywhere(catalogue, strong_marks):
        assert [s.subject for s in u.subjects] == list(strong_marks)
        assert sum(s.points for s in u.subjects) == u.points
        assert {s.subject for s in u.subjects if s.counted} == set(u.counted)
    tut = university_points(catalogue["tut"], strong_marks)
    lo = next(s for s in tut.subjects if s.subject == "life_orientation")
    assert (lo.level, lo.points, lo.counted) == (7, 0.0, False)  # TUT leaves Life Orientation out


def test_life_orientation_at_half_adds_half_its_points():
    uni = University.model_validate(
        {"university": "ex", "name": "Example University", "city": "Pretoria", "academic_year": 2027,
         "programmes": [{"id": "a", "name": "A"}],
         "sources": [{"id": "s", "url": "https://example.org", "publisher": "Example"}],
         "points_rules": {"source": "s", "subjects_counted": 3, "life_orientation": "half",
                          "scale": [{"min_percent": 0, "level": 1}, {"min_percent": 70, "level": 6}]}}
    )
    u = university_points(uni, {"english": 75, "mathematics": 72, "history": 40, "life_orientation": 80})
    assert [(s.subject, s.level, s.points, s.counted) for s in u.subjects] == [
        ("english", 6, 6.0, True),
        ("mathematics", 6, 6.0, True),
        ("history", 1, 0.0, False),
        ("life_orientation", 6, 3.0, True),
    ]
    assert u.points == 15.0


def test_a_university_without_a_points_rule_says_so():
    uni = University.model_validate(
        {"university": "ex", "name": "Example University", "city": "Pretoria", "academic_year": 2027,
         "programmes": [{"id": "a", "name": "A"}]}
    )
    u = university_points(uni, {"english": 70})
    assert u.points is None and u.source_url is None
    assert u.lines == ["We don't have this university's points rule yet."]
    assert u.tiers[UNVERIFIED] == 1


def test_each_way_of_counting_life_orientation_is_said_plainly():
    def rule(life_orientation: str) -> PointsRule:
        return PointsRule(source="s", subjects_counted=6, life_orientation=life_orientation, scale=[{"min_percent": 0, "level": 1}])

    assert _how(rule("exclude")) == "Counts your best 6 subjects, leaving out Life Orientation."
    assert _how(rule("half")) == "Counts 6 subjects: Life Orientation at half its points, and your best 5 others."
    assert _how(rule("full")) == "Counts 6 subjects: Life Orientation and your best 5 others."
