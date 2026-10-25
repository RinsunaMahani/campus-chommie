from datetime import date

import pytest

from campus_engine.schemas import Source
from pydantic import ValidationError
from scripts.validate_data import _check_sources, check

TODAY = date(2026, 10, 24)


def test_official_university_provenance_is_sufficient_without_claiming_human_review():
    source = Source(id="s", url="https://www.uj.ac.za/admission-aid/", publisher="UJ",
                    retrieved=TODAY, verification_basis="official_university",
                    verified_by="agent draft, needs human check")
    assert source.verified and not source.human_verified
    assert source.last_verified is None
    problems = []
    _check_sources("uj", [source], TODAY, problems.append, [])
    assert problems == []


@pytest.mark.parametrize("url", ["https://uj.ac.za.example.org", "https://fakeuj.ac.za",
                              "https://uj.ac.za@evil.org", "http://uj.ac.za", "https://example.org"])
def test_official_verification_rejects_unrelated_and_spoofed_domains(url):
    with pytest.raises(ValidationError):
        Source(id="s", url=url, publisher="UJ", retrieved=TODAY, verification_basis="official_university")


def test_official_verification_needs_a_retrieval_date():
    with pytest.raises(ValidationError):
        Source(id="s", url="https://uj.ac.za", publisher="UJ", verification_basis="official_university")


@pytest.mark.parametrize("reviewer", [None, "", "  ", "agent draft, needs human check", " Agent draft", "AI", "Codex", "Claude", "ChatGPT", "GPT-6", "automated review"])
def test_a_date_does_not_turn_an_automated_or_unnamed_review_into_human_signoff(reviewer):
    source = Source(id="s", url="https://example.org", publisher="Example", last_verified=TODAY, verified_by=reviewer)
    assert not source.human_verified
    problems = []
    _check_sources("example", [source], TODAY, problems.append, [])
    assert problems == ["example/s: verification needs a named human reviewer, not an agent"]


@pytest.mark.parametrize("reviewer", ["Rinsuna Mahani", "Aisha Smith"])
def test_a_named_dated_human_review_is_recognised(reviewer):
    source = Source(id="s", url="https://example.org", publisher="Example", last_verified=TODAY, verified_by=reviewer)
    assert source.human_verified
    assert not source.model_copy(update={"last_verified": None}).human_verified


def test_stale_verification_is_a_release_problem():
    source = Source(id="s", url="https://example.org", publisher="Example", last_verified=date(2025, 1, 1), verified_by="Rinsuna Mahani")
    problems = []
    _check_sources("example", [source], TODAY, problems.append, [])
    assert problems == ["example/s: last verified 2025-01-01, re-check it"]


@pytest.mark.parametrize("release", [False, True])
def test_an_empty_catalogue_is_reported_for_drafts_and_releases(tmp_path, release):
    path = tmp_path / "empty.yaml"
    path.write_text(f"university: empty\nname: Empty University\ncity: Example\nacademic_year: 2027\nrelease: {str(release).lower()}\nprogrammes: []\nsources: []\n")
    errors, warnings = check(path, TODAY)
    assert "empty: no programmes yet" in (errors if release else warnings)
    assert "empty: no sources" in (errors if release else warnings)
