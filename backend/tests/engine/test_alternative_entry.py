from campus_engine.matching import assess


def test_external_music_qualifications_are_not_assumed_or_rejected(catalogue):
    uni=catalogue['up']
    programme=uni.programme('bmus')
    marks=dict(english=70,mathematics=70,physical_sciences=70,life_sciences=70,geography=70,other_language=70)
    assert assess(uni,programme,marks).tier == 'unverified'
    marks['music']=50
    result=assess(uni,programme,marks)
    assert result.tier == 'reach'
    assert any('audition' in line for line in result.explanation)
    marks['english']=49
    assert assess(uni,programme,marks).tier == 'not_yet'


def test_music_alternative_does_not_waive_published_aps(catalogue):
    uni=catalogue['up']
    marks=dict(english=60,mathematics=40,geography=40,history=40,other_language=40,life_sciences=40)
    assert assess(uni,uni.programme('bmus'),marks).tier == 'not_yet'


def test_public_accountability_experience_route_requires_manual_assessment(catalogue):
    uni=catalogue['su']
    programme=uni.programme('dip_public_accountability')
    marks=dict(english=40,mathematics=40,geography=40,history=40)
    assert assess(uni,programme,marks).tier == 'subjects_met'
    marks['english']=30
    assert assess(uni,programme,marks).tier == 'unverified'
