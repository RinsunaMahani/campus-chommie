"""Confirmation and crisis gates need no app or database to exercise."""
from datetime import date

import pytest

from campus_engine.schemas import FundingPack, Source, University
from src.domains.catalogue.funding.services.funding_service import confirmation as funding_confirmation
from src.domains.catalogue.universities.services.university_service import confirmation as university_confirmation
from src.domains.student.alerts.services.alert_service import _checked


@pytest.mark.parametrize("reviewer,date_checked,expected", [
    ("Rinsuna Mahani", date(2026, 10, 24), True),
    ("agent draft, needs human check", date(2026, 10, 24), False),
    ("Codex", date(2026, 10, 24), False),
    ("Rinsuna Mahani", None, False),
    (None, date(2026, 10, 24), False),
])
def test_release_flag_cannot_bypass_source_verification(reviewer, date_checked, expected):
    source = Source(id="s", url="https://example.org", publisher="Example", verified_by=reviewer, last_verified=date_checked)
    uni = University(university="example", name="Example", city="Example", academic_year=2027, release=True, sources=[source])
    funding = FundingPack.model_validate({
        "release": True, "sources": [source],
        "funders": [{"id": "example", "name": "Example", "short_name": "Example", "sector": "government",
                     "fields": "any", "stages": ["first_year"], "applications": {"source": "s"}}],
    })
    assert university_confirmation(uni)["confirmed"] is expected
    assert funding_confirmation(funding)["confirmed"] is expected
    assert _checked(source) is expected
    assert university_confirmation(uni.model_copy(update={"release": False}))["confirmed"] is False
    assert funding_confirmation(funding.model_copy(update={"sources": []}))["confirmed"] is False
    assert not _checked(None)


def test_official_university_source_is_accepted_without_enabling_unrelated_funding():
    source = Source(id="s", url="https://www.uj.ac.za/", publisher="UJ", retrieved=date(2026, 10, 25),
                    verification_basis="official_university", verified_by="agent")
    uni = University(university="uj", name="UJ", city="Johannesburg", academic_year=2027, release=True, sources=[source])
    assert university_confirmation(uni)["confirmed"]
    assert _checked(source)
    assert not source.human_verified


def test_official_funder_source_still_requires_pack_release():
    source = Source(id="s", url="https://www.nsfas.org.za/", publisher="NSFAS",
                    retrieved=date(2026, 10, 25), verification_basis="official_publisher")
    funding = FundingPack.model_validate({
        "release": True, "sources": [source],
        "funders": [{"id": "example", "name": "Example", "short_name": "Example", "sector": "government",
                     "fields": "any", "stages": ["first_year"], "applications": {"source": "s"}}],
    })
    assert funding_confirmation(funding)["confirmed"]
    assert not source.human_verified
    assert not _checked(source)  # Funder/venue acceptance must not widen the crisis-contact gate.
    assert not funding_confirmation(funding.model_copy(update={"release": False}))["confirmed"]
