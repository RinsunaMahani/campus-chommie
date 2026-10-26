import pytest

from campus_engine.matching import assess


@pytest.mark.parametrize('maths,mark', [('mathematics',50),('technical_mathematics',50),('mathematical_literacy',70)])
@pytest.mark.parametrize('science', ['physical_sciences','life_sciences'])
def test_uj_geography_needs_maths_science_and_geography(catalogue, maths, mark, science):
    uni = catalogue['uj']
    programme = uni.programme('uj_b5sgeq')
    marks = {maths:mark,science:40,'geography':40,'english':70,'history':90,'other_language':90}
    assert assess(uni,programme,marks,'first_additional').tier == 'reach'
    marks[science] = 39
    assert assess(uni,programme,marks,'first_additional').tier == 'not_yet'
    marks[science] = 40
    marks[maths] = mark - 1
    assert assess(uni,programme,marks,'first_additional').tier == 'not_yet'
    marks[maths] = mark
    marks['english'] = 60
    assert assess(uni,programme,marks,'home').tier == 'reach'
    assert assess(uni,programme,marks,'first_additional').tier == 'not_yet'


@pytest.mark.parametrize('pid',['uj_b2p82q','uj_b2p83q'])
def test_geology_follows_faculty_table(catalogue,pid):
    uni=catalogue['uj']
    marks=dict(english=60,mathematics=70,physical_sciences=60,history=90,geography=90,other_language=90)
    assert assess(uni,uni.programme(pid),marks).tier == 'reach'
    marks['physical_sciences']=59
    assert assess(uni,uni.programme(pid),marks).tier == 'not_yet'


@pytest.mark.parametrize('subject,percent',[('mathematics',30),('mathematical_literacy',60)])
def test_ufs_specific_extended_admission_table(catalogue,subject,percent):
    uni=catalogue['ufs']
    programme=uni.programme('b_sustainable_food_systems_extended')
    marks={subject:percent,'english':50,'history':80,'geography':80,'life_sciences':80,'other_language':80}
    assert assess(uni,programme,marks).tier == 'reach'
    marks[subject]=percent-1
    assert assess(uni,programme,marks).tier == 'not_yet'


@pytest.mark.parametrize('subjects',[
    {'agricultural_sciences':50},{'consumer_studies':50},
    {'life_sciences':50,'geography':50},{'life_sciences':50,'economics':50},
    {'life_sciences':50,'business_studies':50},
])
def test_mut_registrar_subject_alternatives(catalogue,subjects):
    uni=catalogue['mut']
    programme=uni.programme('dip_community_extension')
    marks=dict(english=50,mathematics=40,history=90,other_language=90,accounting=90,**subjects)
    assert assess(uni,programme,marks).tier == 'reach'
    marks[next(iter(subjects))]=49
    assert assess(uni,programme,marks).tier == 'not_yet'


def test_reopening_does_not_claim_first_lecture(catalogue):
    entry=next(e for e in catalogue['smu'].calendar if e.name == 'University resumes for 2027')
    assert entry.start.isoformat() == '2027-01-05'
    assert entry.step is None
    assert entry.end is None
