import pytest

from campus_engine.matching import assess


@pytest.mark.parametrize('role,percent,tier', [
    ('home', 50, 'reach'), ('first_additional', 50, 'not_yet'),
    ('first_additional', 60, 'reach'), (None, 50, 'unverified'),
    (None, 60, 'reach'), (None, 49, 'not_yet'),
])
def test_uwc_english_language_role_boundary(catalogue, role, percent, tier):
    uni = catalogue['uwc']
    marks = dict(english=percent, other_language=80, mathematics=80, life_sciences=80,
                 geography=80, history=80, life_orientation=80)
    result = assess(uni, uni.programme('uwc_social_work'), marks, role)
    assert result.tier == tier
    assert result.source_url


def test_english_role_does_not_add_a_second_subject_to_points(catalogue):
    uni = catalogue['uwc']
    marks = dict(english=60, other_language=80, mathematics=80, life_sciences=80,
                 geography=80, history=80, life_orientation=80)
    programme = uni.programme('uwc_social_work')
    assert assess(uni, programme, marks, 'home').points == assess(uni, programme, marks, 'first_additional').points


def test_uj_foundation_phase_uses_its_own_language_thresholds(catalogue):
    uni = catalogue['uj']
    programme = uni.programme('uj_b5bfpq')
    marks = dict(english=60, mathematics=70, geography=70, history=70, other_language=70, life_sciences=70)
    assert assess(uni, programme, marks, 'home').tier == 'reach'
    assert assess(uni, programme, marks, 'first_additional').tier == 'not_yet'
    assert assess(uni, programme, marks).tier == 'unverified'


def test_unpublished_technical_maths_aps_does_not_become_a_pass(catalogue):
    uni = catalogue['cput']
    programme = uni.programme('dip_clothing_textile_technology')
    marks = dict(english=70, technical_mathematics=70, geography=70, history=70, other_language=70, life_sciences=70)
    assert assess(uni, programme, marks).tier == 'subjects_met'
    marks['mathematics'] = marks.pop('technical_mathematics')
    assert assess(uni, programme, marks).tier in ('reach', 'meets_minimum')
