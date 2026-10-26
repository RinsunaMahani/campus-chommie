import pytest
from pydantic import ValidationError

from campus_engine.matching import assess
from campus_engine.schemas import Requirements


@pytest.mark.parametrize('programme,language', [
    ('uj_b5lafq', 'afrikaans'), ('uj_b5lazq', 'isizulu'), ('uj_b5lasq', 'sepedi'),
])
@pytest.mark.parametrize('percent,role,tier', [
    (55, 'home', 'reach'), (55, 'first_additional', 'not_yet'),
    (55, None, 'unverified'), (65, None, 'reach'), (45, None, 'not_yet'),
])
def test_named_language_thresholds(catalogue, programme, language, percent, role, tier):
    uni = catalogue['uj']
    marks = dict(english=80, mathematics=80, other_language=80, geography=80,
                 life_sciences=80, another_subject_1=percent)
    before = assess(uni, uni.programme(programme), marks)
    result = assess(uni, uni.programme(programme), marks, 'home', {language: (percent, role)})
    assert before.tier == 'unverified'
    assert result.tier == tier
    assert result.points == before.points  # Metadata never adds another subject to APS.


def test_unrelated_language_does_not_satisfy_named_rule(catalogue):
    uni = catalogue['uj']
    marks = dict(english=80, mathematics=80, other_language=80, geography=80, life_sciences=80)
    assert assess(uni, uni.programme('uj_b5lafq'), marks, 'home', {'sepedi': (80, 'home')}).tier == 'unverified'
    marks['english'] = 60
    assert assess(uni, uni.programme('uj_b5lafq'), marks, 'first_additional', {'afrikaans': (80, 'home')}).tier == 'not_yet'


@pytest.mark.parametrize('levels', [{'unknown': {'home': 4}}, {'afrikaans': {}}, {'afrikaans': {'second_additional': 4}}])
def test_invalid_named_language_rules_rejected(levels):
    with pytest.raises(ValidationError):
        Requirements(source='s', named_language_levels=levels)
