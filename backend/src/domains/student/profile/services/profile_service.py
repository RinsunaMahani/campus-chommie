"""
The student's profile. The university and campus must exist in the data
packs; the 18-or-older confirmation comes from the consent records kept by
identity, read through account_service (never identity's tables).
"""
from __future__ import annotations

from src.core.exceptions import NotFoundError, ValidationError
from src.domains.catalogue.universities.services import university_service as catalogue
from src.domains.identity.accounts.services import account_service
from src.extensions import db

from ..constants import AGE_CONFIRMATION
from ..repositories import profile_repository as repo


def _field_error(field: str, message: str) -> ValidationError:
    return ValidationError("Please check the highlighted fields.", errors=[{field: [message]}])


def university_of(user) -> str | None:
    """The student's university id, or None before they've chosen one."""
    profile = repo.for_user(user.id)
    return profile.university if profile else None


def place_of(user) -> tuple[str | None, str | None]:
    """The student's university and campus ids: (None, None) before they've chosen."""
    profile = repo.for_user(user.id)
    return (profile.university, profile.campus) if profile else (None, None)


def export_for(user) -> dict | None:
    """POPIA export: the university and campus the student chose."""
    profile = repo.for_user(user.id)
    return {"university": profile.university, "campus": profile.campus} if profile else None


def erase_for(user) -> None:
    """The student's university and campus choice, deleted: the demo's daily reset (and DELETE /me's later)."""
    repo.erase(user.id)
    db.session.commit()


def view(user) -> dict:
    profile = repo.for_user(user.id)
    consents = account_service.consents_view(user)
    age = next((c for c in consents if c["document"] == AGE_CONFIRMATION), None)
    out = {
        "university": None,
        "university_name": None,
        "campus": None,
        "campus_name": None,
        "confirmed_18_or_older_at": age["accepted_at"] if age else None,
        "consents": consents,
    }
    if profile:
        uni = catalogue.packs().get(profile.university)
        campuses = {c.id: c.name for c in uni.campuses} if uni else {}
        out.update(
            university=profile.university,
            university_name=uni.name if uni else None,
            campus=profile.campus,
            campus_name=campuses.get(profile.campus) if profile.campus else None,
        )
    return out


def update(user, university: str, campus: str | None) -> dict:
    """Save the university and campus, both checked against the packs."""
    try:
        uni = catalogue.get(university)
    except NotFoundError:
        raise _field_error("university", "We don't have that university.") from None
    campus_ids = [c.id for c in uni.campuses]
    if campus is None and campus_ids:
        raise _field_error("campus", "Choose your campus.")
    if campus is not None and campus not in campus_ids:
        raise _field_error("campus", f"{uni.name} has no such campus.")
    repo.save(user.id, uni.university, campus)
    db.session.commit()
    return view(user)
