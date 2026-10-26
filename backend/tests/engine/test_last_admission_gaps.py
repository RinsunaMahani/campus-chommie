from datetime import date

import pytest
from pydantic import ValidationError

from campus_engine.matching import assess
from campus_engine.schemas import Requirements
from scripts.data_readiness import report


@pytest.mark.parametrize('technical', ['civil_technology','electrical_technology','mechanical_technology','physical_sciences','technical_sciences'])
@pytest.mark.parametrize('paired', ['engineering_graphics_and_design','mathematics','technical_mathematics'])
def test_tut_technology_requires_a_valid_specialisation_pair(catalogue,technical,paired):
    uni=catalogue['tut']
    programme=uni.programme('bed_sp_fet_technology')
    marks={technical:50,paired:50,'english':50,'history':90,'geography':90,'other_language':90}
    assert assess(uni,programme,marks).tier == 'reach'
    marks[paired]=49
    assert assess(uni,programme,marks).tier == 'not_yet'
    marks[paired]=50
    marks[technical]=49
    assert assess(uni,programme,marks).tier == 'not_yet'


@pytest.mark.parametrize('science',['life_sciences','geography','agricultural_sciences','information_technology'])
def test_ufh_crop_science_english_and_other_subject_boundaries(catalogue,science):
    uni=catalogue['ufh']
    programme=uni.programme('ufh_71524')
    marks=dict(english=50,mathematics=50,physical_sciences=50,life_orientation=50,accounting=50,other_language=50)
    marks[science]=50
    assert assess(uni,programme,marks).tier == 'subjects_met'
    marks['english']=49
    assert assess(uni,programme,marks).tier == 'not_yet'
    marks['english']=50
    marks['accounting']=49
    assert assess(uni,programme,marks).tier == 'not_yet'


@pytest.mark.parametrize('subject,percent,aps',[('mathematics',40,24),('mathematical_literacy',50,26)])
def test_banking_checks_known_minima_without_claiming_full_eligibility(catalogue,subject,percent,aps):
    uni=catalogue['cput']
    programme=uni.programme('dip_banking')
    marks={subject:percent,'english':50,'economics':90,'accounting':90,'history':90,'other_language':90}
    result=assess(uni,programme,marks)
    assert result.tier == 'unverified'
    assert any(str(aps)+' points' in line for line in result.explanation)
    assert not any(line == "Your subjects meet this programme's minimums." for line in result.explanation)
    assert any('NQF Level 4 is not' in line for line in result.explanation)
    marks[subject]=percent-1
    assert assess(uni,programme,marks).tier == 'not_yet'


def test_cput_bed_checks_language_roles_but_refers_electives(catalogue):
    uni=catalogue['cput']
    programme=uni.programme('bed_senior_phase_fet')
    marks=dict(english=40,other_language=50,mathematics=90,physical_sciences=90,accounting=90,history=90)
    result=assess(uni,programme,marks,'first_additional',{'isixhosa':(50,'home')})
    assert result.tier == 'unverified'
    assert any('campus language' in line for line in result.explanation)
    assert assess(uni,programme,marks,'first_additional',{'isixhosa':(49,'home')}).tier == 'not_yet'
    assert assess(uni,programme,marks,'first_additional',{'sepedi':(90,'home')}).tier == 'not_yet'
    assert assess(uni,programme,marks,'first_additional').tier == 'unverified'


def test_partial_conditions_remain_in_readiness_queue():
    row=next(u for u in report(date(2026,10,26))['universities'] if u['id']=='cput')
    assert {'dip_banking','bed_senior_phase_fet'} <= set(row['partial_requirements'])
    assert not row['requirements_missing']


def test_unassessed_conditions_must_explain_the_gap():
    with pytest.raises(ValidationError):
        Requirements(source='s',min_points=20,unassessed_conditions=[''])
