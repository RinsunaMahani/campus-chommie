import pytest

from campus_engine.matching import assess
from campus_engine.overview import university_points
from campus_engine.points import compute_points


def marks_at(percent):
    return dict(english=percent, mathematics=percent, other_language=percent,
                history=percent, geography=percent, life_sciences=percent, life_orientation=percent)


@pytest.mark.parametrize("percent,total", [
    (0, 6), (29, 6), (30, 12), (39, 12), (40, 20), (49, 20),
    (50, 26), (59, 26), (60, 35), (69, 35), (70, 42), (79, 42),
    (80, 49), (89, 49), (90, 56), (100, 56),
])
def test_spu_table_boundaries(catalogue, percent, total):
    result = compute_points(marks_at(percent), catalogue['spu'].points_rules, 'home',
                            {'other_language': (percent, 'first_additional')})
    assert result.complete
    assert result.total == total
    assert len(result.counted) == 7
    assert sum(result.adds.values()) == total
    assert result.levels['english'] <= 7  # NSC levels remain separate from APS points.


def test_spu_bonus_follows_language_role_and_excludes_maths_literacy(catalogue):
    marks = marks_at(60)
    marks['mathematical_literacy'] = marks.pop('mathematics')
    uni = catalogue['spu']
    result = university_points(uni, marks, 'first_additional', {'other_language': (60, 'home')})
    assert result.points == 33
    adds = {s.subject: s.points for s in result.subjects}
    assert adds['english'] == 5
    assert adds['other_language'] == 7
    assert adds['mathematical_literacy'] == 5
    match = assess(uni, uni.programmes[0], marks, 'first_additional', {'other_language': (60, 'home')})
    assert match.points == result.points


@pytest.mark.parametrize('change', ['missing_role', 'six', 'eight', 'missing_lo'])
def test_spu_needs_complete_seven_subject_input(catalogue, change):
    marks = marks_at(90)
    languages = {'other_language': (90, 'first_additional')}
    if change == 'missing_role':
        languages = {}
    elif change == 'six':
        marks.pop('history')
    elif change == 'eight':
        marks['accounting'] = 90
    else:
        marks['accounting'] = marks.pop('life_orientation')
    uni = catalogue['spu']
    assert university_points(uni, marks, 'home', languages).points is None
    assert assess(uni, uni.programmes[0], marks, 'home', languages).points is None


def test_spu_source_exception_does_not_claim_official_provenance(catalogue):
    source = catalogue['spu'].source('s-spu-seven-subjects')
    assert source.verified
    assert source.verification_basis is None
    assert 'Rinsuna' in source.verified_by


def test_spu_english_fal_minimum_is_enforced(catalogue):
    uni = catalogue['spu']
    marks = marks_at(90)
    marks['english'] = 50
    languages = {'other_language': (90, 'home')}
    result = assess(uni, uni.programmes[0], marks, 'first_additional', languages)
    assert result.tier == 'not_yet'
    assert any('English first additional' in line for line in result.failed)
