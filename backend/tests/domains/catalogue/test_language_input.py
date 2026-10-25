import pytest

from src.core.exceptions import ValidationError
from src.domains.pathways.course_finder.schemas.course_finder_schemas import PointsSchema, load
from src.domains.pathways.course_finder.services.course_finder_service import _english_level, _marks


def test_english_role_survives_request_validation_without_becoming_an_extra_mark():
    rows = load(PointsSchema(), {'marks': [{'subject': 'english', 'percent': 55, 'language_level': 'home'}]})['marks']
    assert _english_level(rows) == 'home'
    assert _marks(rows) == {'english': 55}


@pytest.mark.parametrize('subject,role', [('mathematics', 'home'), ('english', 'second_additional'), ('english', None)])
def test_invalid_language_metadata_is_rejected(subject, role):
    with pytest.raises(ValidationError):
        load(PointsSchema(), {'marks': [{'subject': subject, 'percent': 55, 'language_level': role}]})
