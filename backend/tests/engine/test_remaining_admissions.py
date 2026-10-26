from datetime import date

import pytest
from pydantic import ValidationError

from campus_engine.matching import assess
from campus_engine.schemas import LanguageGroup, Programme
from scripts.data_readiness import report


@pytest.mark.parametrize('language', ['sepedi', 'setswana', 'xitsonga', 'isizulu'])
def test_tut_foundation_language_and_maths_boundaries(catalogue, language):
    uni = catalogue['tut']
    p = uni.programme('bed_foundation_phase')
    marks = dict(english=50, other_language=60, mathematics=50, history=80, geography=80, life_sciences=80)
    assert assess(uni, p, marks, 'first_additional', {language:(60,'home')}).tier == 'reach'
    assert assess(uni, p, marks, 'first_additional', {language:(59,'home')}).tier == 'not_yet'
    assert assess(uni, p, marks, 'first_additional', {language:(60,'first_additional')}).tier == 'not_yet'
    assert assess(uni, p, marks, 'first_additional', {language:(60,None)}).tier == 'unverified'
    assert assess(uni, p, marks, 'first_additional').tier == 'unverified'
    marks['mathematical_literacy'] = marks.pop('mathematics')
    assert assess(uni, p, marks, 'first_additional', {language:(60,'home')}).tier == 'not_yet'
    marks['mathematical_literacy'] = 60
    assert assess(uni, p, marks, 'first_additional', {language:(60,'home')}).tier == 'reach'


def test_tut_requires_a_first_additional_language_as_well_as_home(catalogue):
    uni = catalogue['tut']
    marks = dict(english=80, other_language=80, mathematics=80, history=80, geography=80, life_sciences=80)
    result = assess(uni, uni.programme('bed_foundation_phase'), marks, 'home', {'sepedi':(80,'home')})
    assert result.tier == 'not_yet'
    assert any('first additional' in message for message in result.failed)


@pytest.mark.parametrize('uni_key,pid', [('ru','pgce'),('su','ba_extended'),('su','bsc_extended'),('ufs','bed_extended')])
def test_published_manual_routes_never_qualify_from_school_marks(catalogue, uni_key, pid):
    uni = catalogue[uni_key]
    marks = dict(english=100, other_language=100, mathematics=100, history=100, geography=100, life_sciences=100)
    result = assess(uni, uni.programme(pid), marks)
    assert result.tier == 'unverified'
    assert result.points is None
    assert result.source_url
    assert 'School marks alone' in result.explanation[-1]
    row = next(u for u in report(date(2026,10,26))['universities'] if u['id'] == uni_key)
    assert pid in row['manual_admission']
    assert pid not in row['requirements_missing']


@pytest.mark.parametrize('pid', ['uj_b2p77q','uj_b2p78q'])
def test_uj_physics_course_and_faculty_requirements(catalogue, pid):
    uni = catalogue['uj']
    marks = dict(english=60, mathematics=70, physical_sciences=60, history=80, geography=80, other_language=80)
    assert assess(uni, uni.programme(pid), marks).tier == 'reach'
    marks['mathematics'] = 69
    assert assess(uni, uni.programme(pid), marks).tier == 'not_yet'
    marks['mathematics'] = 70
    marks['physical_sciences'] = 59
    assert assess(uni, uni.programme(pid), marks).tier == 'not_yet'


def test_language_group_rejects_unknown_names():
    with pytest.raises(ValidationError):
        LanguageGroup(role='home', min_level=5, languages=['sepedii'])


def test_manual_route_cannot_also_claim_school_mark_eligibility():
    with pytest.raises(ValidationError):
        Programme(id='x',name='X', requirements={'source':'s','min_points':25},
                  manual_admission={'source':'s','reason':'prior_qualification','text':'A degree is required.'})


def test_ufh_commerce_known_pair_and_unknown_business_equivalence(catalogue):
    uni = catalogue['ufh']
    p = uni.programme('ufh_500492')
    marks = dict(english=50, mathematics=40, accounting=50, economics=50, history=50, geography=50, life_orientation=50)
    assert assess(uni,p,marks).tier == 'subjects_met'
    marks['business_studies'] = marks.pop('economics')
    assert assess(uni,p,marks).tier == 'unverified'
    marks['english'] = 49
    assert assess(uni,p,marks).tier == 'not_yet'


@pytest.mark.parametrize('science', ['physical_sciences','life_sciences','geography'])
def test_ufh_science_known_subjects_without_inventing_it_equivalence(catalogue, science):
    uni = catalogue['ufh']
    p = uni.programme('ufh_500493')
    marks = dict(english=50, mathematics=50, accounting=50, history=50, other_language=50, life_orientation=50)
    marks[science] = 50
    assert assess(uni,p,marks).tier == 'subjects_met'
    marks['information_technology'] = marks.pop(science)
    assert assess(uni,p,marks).tier == 'unverified'
