import pytest

from campus_engine.matching import assess


@pytest.mark.parametrize('code,minimum', [('b6sc0q', 60), ('b6cx3q', 50), ('b6ix2q', 60), ('b6mx2q', 60)])
@pytest.mark.parametrize('maths', ['mathematics', 'technical_mathematics'])
@pytest.mark.parametrize('science', ['physical_sciences', 'technical_sciences'])
def test_uj_extended_engineering_accepts_each_published_alternative(catalogue, code, minimum, maths, science):
    uni = catalogue['uj']
    programme = uni.programme('uj_' + code)
    marks = dict(english=50, other_language=80, history=80, geography=80)
    marks.update({maths: minimum, science: minimum})
    assert assess(uni, programme, marks).tier == 'reach'
    marks[science] = minimum - 1
    assert assess(uni, programme, marks).tier == 'not_yet'
    marks[science] = minimum
    marks[maths] = minimum - 1
    assert assess(uni, programme, marks).tier == 'not_yet'


def test_spu_2027_first_year_calendar_is_not_shifted_from_2026(catalogue):
    rows = [r for r in catalogue['spu'].calendar if r.source == 's-spu-calendar-2027']
    assert len(rows) == 21
    registration = next(r for r in rows if r.step == 'register')
    assert str(registration.start) == '2027-01-25'
    assert str(registration.end) == '2027-02-05'
    assert str(next(r for r in rows if r.step == 'first_lecture').start) == '2027-02-08'
    assert not any('NSC' in r.name for r in rows)
