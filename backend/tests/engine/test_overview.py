"""
Your points at every university: each counted by its own rule, in name order, with how many
programmes the marks meet and how that university counts.
"""
from __future__ import annotations

from campus_engine.matching import COMPETITIVE, MEETS_MINIMUM, NOT_YET, REACH, UNVERIFIED
import pytest

from campus_engine.overview import _how, _summary, points_everywhere, university_points
from campus_engine.schemas import PointsRule, University


def test_the_same_marks_give_each_universitys_own_points(catalogue, strong_marks):
    points = {u.university: u.points for u in points_everywhere(catalogue, strong_marks)}
    # SMU counts seven subjects with Life Orientation; UP and TUT count six without it.
    assert {k: points[k] for k in ("smu", "tut", "up")} == {"smu": 47, "tut": 40, "up": 40}


def test_universities_without_programmes_still_count_points_their_own_way(catalogue, strong_marks):
    by_id = {u.university: u for u in points_everywhere(catalogue, strong_marks)}
    # Wits: the best seven with Life Orientation on its own table, and 2 more for English and Mathematics:
    # 9 + 9 + 7 + 7 + 6 + 6, and Life Orientation 3 for 88%.
    assert by_id["wits"].points == 47
    assert by_id["wits"].lines[1] == "English, Mathematics and Life Orientation count on their own points tables here."
    # UNIVEN scores the marks themselves: 8.2 + 8.1 + 8.0 + 8.5 + 7.4 + 7.9.
    assert by_id["univen"].points == pytest.approx(48.1)
    assert by_id["univen"].lines[1] == "Each subject scores a tenth of its percentage, and nothing under 40%."
    # UMP: the best six, and Life Orientation at half its level 7.
    assert by_id["ump"].points == 43.5
    for uni in ("uj", "unisa", "ul", "nwu", "vut"):
        assert by_id[uni].points == 40, uni
    # NMU adds the six percentages, out of 600: 82 + 81 + 80 + 85 + 74 + 79.
    assert by_id["nmu"].points == 481
    # UWC: English and Mathematics 13 each at 80%+, others 7, 7, 6, 6, Life Orientation 3.
    assert by_id["uwc"].points == 13 + 13 + 7 + 7 + 6 + 6 + 3
    # No points rule: say so, and why.
    assert by_id["uct"].points is None
    assert by_id["uct"].lines[0] == "We don't have this university's points rule yet."
    assert "Faculty Points Score" in by_id["uct"].lines[1]
    # No programmes yet: points, and the summary says why there's nothing to meet.
    assert by_id["wits"].summary == "We haven't added this university's programmes yet."
    assert sum(by_id["wits"].subjects[i].points for i in range(len(strong_marks))) == 47


def test_a_subjects_own_points_table_and_points_from_the_percentage():
    def uni(rule: dict) -> University:
        return University.model_validate(
            {"university": "ex", "name": "Example University", "city": "Pretoria", "academic_year": 2027,
             "sources": [{"id": "s", "url": "https://example.org", "publisher": "Example"}],
             "points_rules": {"source": "s", "subjects_counted": 2, "life_orientation": "exclude",
                              "scale": [{"min_percent": 0, "level": 1}, {"min_percent": 60, "level": 5}], **rule}}
        )

    table = uni({"subject_points": {"mathematics": [{"min_percent": 0, "points": 0}, {"min_percent": 60, "points": 9}]}})
    u = university_points(table, {"english": 65, "mathematics": 61, "history": 70})
    # Mathematics is worth 9 here, so it beats history's level 5 for the second place.
    assert [(s.subject, s.points, s.counted) for s in u.subjects] == [
        ("english", 5.0, True), ("mathematics", 9.0, True), ("history", 0.0, False)
    ]
    assert u.points == 14
    marks = uni({"percent_points": {"per_percent": 0.1, "from_percent": 40}})
    assert university_points(marks, {"english": 65, "mathematics": 39}).points == 6.5
    # A general table for every subject without its own: nothing under 20% here.
    general = uni({"other_points": [{"min_percent": 0, "points": 0}, {"min_percent": 20, "points": 1}, {"min_percent": 60, "points": 5}]})
    assert university_points(general, {"english": 65, "history": 15}).points == 5


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
        if u.points is None:  # no points rule yet: nothing to break down
            assert u.subjects == []
            continue
        assert [s.subject for s in u.subjects] == list(strong_marks)
        assert sum(s.points for s in u.subjects) == pytest.approx(u.points)
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
