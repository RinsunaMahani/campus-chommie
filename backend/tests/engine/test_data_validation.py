from datetime import date

import pytest

from campus_engine.catalogue import DataPackError, load_catalogue, load_university
from campus_engine.i18n import t
from scripts.validate_data import check

TODAY = date(2026, 10, 9)

BROKEN = """
university: broken
name: Broken University
city: Pretoria
academic_year: 2027
programmes:
  - id: a
    name: A
    requirements: {source: missing, min_points: 30}
    bridges_to:
      - {to: nowhere, guarantee: by_rule, conditions: x, source: missing}
sources: []
"""

RELEASE_INCOMPLETE = """
university: early
name: Early University
city: Pretoria
academic_year: 2027
release: true
programmes:
  - {id: a, name: A, requirements: null}
sources:
  - {id: s, url: "https://example.org", publisher: Early}
"""


def test_shipped_packs_have_no_errors():
    from campus_engine.catalogue import UNIVERSITIES_DIR

    for path in UNIVERSITIES_DIR.glob("*.yaml"):
        errors, _ = check(path, TODAY)
        assert errors == [], errors


def test_template_is_skipped_by_the_app():
    assert "example" not in load_catalogue()


def test_broken_references_fail(tmp_path):
    path = tmp_path / "broken.yaml"
    path.write_text(BROKEN)
    with pytest.raises(DataPackError) as exc:
        load_university(path)
    message = str(exc.value)
    assert "unknown source 'missing'" in message
    assert "unknown programme 'nowhere'" in message


def test_incomplete_release_pack_is_an_error(tmp_path):
    path = tmp_path / "early.yaml"
    path.write_text(RELEASE_INCOMPLETE)
    errors, _ = check(path, TODAY)
    assert any("requirements not verified" in e for e in errors)
    assert any("never verified" in e for e in errors)


def test_unknown_language_falls_back_to_english():
    assert t("title", "zu") == t("title", "en") == "Find my course"
    assert "Physical sciences" in t("duplicate", subject="Physical sciences")
