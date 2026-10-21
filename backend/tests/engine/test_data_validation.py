from datetime import date

import pytest

from campus_engine.catalogue import FUNDING_PATH, DataPackError, load_catalogue, load_university
from campus_engine.i18n import t
from scripts.validate_data import _campus_ids, check, check_funding, check_maps, main

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
    assert any("how to apply not verified yet" in e for e in errors)


FUNDING_RELEASE_INCOMPLETE = """
release: true
funders:
  - id: fund
    name: Example Fund
    short_name: Fund
    sector: government
    fields: any
    stages: [first_year]
    applications: {source: s, url: "https://example.org/fund"}
sources:
  - {id: s, url: "https://example.org/fund", publisher: Example Fund}
"""


def test_shipped_funding_pack_has_no_errors():
    errors, warnings = check_funding(FUNDING_PATH, TODAY)
    assert errors == [], errors
    assert any("never verified" in w for w in warnings)  # a draft: warnings until a person checks it


def test_shipped_funding_pack_names_only_universities_we_have():
    from campus_engine.catalogue import UNIVERSITIES_DIR
    from scripts.validate_data import _university_ids

    ids = _university_ids(UNIVERSITIES_DIR)
    assert ids == {"up", "tut", "smu"}
    errors, _ = check_funding(FUNDING_PATH, TODAY, ids)
    assert errors == [], errors


FUNDING_ELSEWHERE = """
funders:
  - id: fund
    name: Example Fund
    short_name: Fund
    sector: company
    fields: any
    stages: [first_year]
    study_at: [hogwarts]
    applications: {windows: []}
  - id: award
    name: Example Award
    short_name: Award
    kind: merit_award
    sector: university
    fields: any
    stages: [first_year]
    applying: automatic
    who_can_apply: {items: [First-years], source: s}
    applications: {source: s, how: "There's no application."}
sources:
  - {id: s, url: "https://example.org/fund", publisher: Example Fund}
"""


def test_a_funder_at_a_university_we_dont_have_is_an_error(tmp_path):
    path = tmp_path / "funding.yaml"
    path.write_text(FUNDING_ELSEWHERE)
    errors, warnings = check_funding(path, TODAY, {"up"})
    assert errors == ["funding/fund: study_at names unknown university 'hogwarts'"]
    assert "funding/fund: who can apply not verified yet" in warnings
    assert not any(w.startswith("funding/award:") for w in warnings)  # an automatic award has no dates or fee to check


def test_incomplete_release_funding_pack_is_an_error(tmp_path):
    path = tmp_path / "funding.yaml"
    path.write_text(FUNDING_RELEASE_INCOMPLETE)
    errors, _ = check_funding(path, TODAY)
    assert "funding/fund: the application fee not verified yet" in errors
    assert "funding/fund: documents not verified yet" in errors
    assert "funding/fund: no application dates yet" in errors


def test_a_broken_funding_pack_fails_the_run(tmp_path, capsys):
    universities = tmp_path / "universities"
    universities.mkdir()
    path = tmp_path / "funding.yaml"
    path.write_text(FUNDING_RELEASE_INCOMPLETE.replace("source: s, url", "source: missing, url"))
    assert main([str(universities), "--funding", str(path)]) == 1
    out = capsys.readouterr().out
    assert "ERROR funding.yaml" in out and "unknown source 'missing'" in out


def test_unknown_language_falls_back_to_english():
    assert t("title", "zu") == t("title", "en") == "Find my course"
    assert "Physical sciences" in t("duplicate", subject="Physical sciences")


MAP = """
university: UNI
campuses:
  - campus: CAMPUS
    source: s-osm
    outline: [[[-25.75, 28.22], [-25.75, 28.23], [-25.76, 28.23]]]
sources:
  - {id: s-osm, url: "https://www.openstreetmap.org/way/1", publisher: OpenStreetMap contributors}
"""


def test_shipped_maps_have_no_errors():
    from campus_engine.catalogue import MAPS_DIR, UNIVERSITIES_DIR

    errors, warnings = check_maps(MAPS_DIR, TODAY, _campus_ids(UNIVERSITIES_DIR))
    assert errors == [], errors
    assert any("never verified" in w for w in warnings)  # a draft until a person checks it


def test_a_map_names_only_universities_and_campuses_we_have(tmp_path):
    (tmp_path / "osm_campuses.yaml").write_text("smu: {}")  # the fetch config is not a map
    (tmp_path / "smu.yaml").write_text(MAP.replace("UNI", "smu").replace("CAMPUS", "atlantis"))
    (tmp_path / "zz.yaml").write_text(MAP.replace("UNI", "hogwarts").replace("CAMPUS", "main"))
    errors, _ = check_maps(tmp_path, TODAY, {"smu": {"ga_rankuwa"}})
    assert errors == ["maps/smu: unknown campus 'atlantis'", "maps/zz.yaml: no pack for university 'hogwarts'"]
