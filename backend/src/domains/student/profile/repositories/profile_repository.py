"""All database access for profiles, scoped to the signed-in student."""
from __future__ import annotations

import uuid

from src.extensions import db

from ..models import StudentProfile


def for_user(user_id: uuid.UUID) -> StudentProfile | None:
    return StudentProfile.query.filter_by(user_id=user_id, is_deleted=False).first()


def save(user_id: uuid.UUID, university: str, campus: str | None) -> StudentProfile:
    profile = for_user(user_id) or StudentProfile(user_id=user_id)
    profile.university, profile.campus = university, campus
    db.session.add(profile)
    return profile


def erase(user_id: uuid.UUID) -> None:
    StudentProfile.query.filter_by(user_id=user_id).delete(synchronize_session=False)
