import pytest
from course_finder_helpers import ASSESS, PLAN, POINTS, STRONG


def test_language_in_additional_slot_reaches_all_assessment_paths(client):
    rows = [dict(row) for row in STRONG] + [dict(subject='another_subject_1', percent=55)]
    summaries = []
    for role, tier in [(None, 'unverified'), ('home', 'reach'), ('first_additional', 'not_yet')]:
        if role:
            rows[-1].update(language_name='afrikaans', language_level=role)
        for endpoint in (ASSESS, PLAN):
            body = dict(university='uj', marks=rows)
            if endpoint == PLAN:
                body['goal'] = 'uj_b5lafq'
            response = client.post(endpoint, json=body)
            assert response.status_code == 200
            data = response.get_json()['data']
            match = data['plan']['goal']['match'] if endpoint == PLAN else next(m for m in data['matches'] if m['programme'] == 'uj_b5lafq')
            assert match['tier'] == tier
        response = client.post(POINTS, json=dict(marks=rows))
        assert response.status_code == 200
        summaries.append(next(u for u in response.get_json()['data']['universities'] if u['university'] == 'uj'))
    assert summaries[1]['tiers']['unverified'] == summaries[0]['tiers']['unverified'] - 1
    assert summaries[2]['tiers']['not_yet'] == summaries[1]['tiers']['not_yet'] + 1


@pytest.mark.parametrize('rows', [
    [dict(subject='mathematics', percent=80, language_name='afrikaans')],
    [dict(subject='other_language', percent=80, language_level='home')],
    [dict(subject='other_language', percent=80, language_name='english')],
    [dict(subject='other_language', percent=80, language_name='afrikaans', language_level='second_additional')],
    [dict(subject=s, percent=80, language_name='afrikaans') for s in ('other_language', 'another_subject_1')],
])
def test_invalid_language_metadata_is_rejected(client, rows):
    response = client.post(ASSESS, json=dict(university='uj', marks=rows))
    assert response.status_code == 422
