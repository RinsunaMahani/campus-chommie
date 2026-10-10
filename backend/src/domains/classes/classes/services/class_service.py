"""
Classes and reps. A class is only ever reached through the signed-in
student's membership: a class they're not in is the same 404 as one that
doesn't exist. Other features (events, the week) ask `membership()` and
`memberships()`, and get plain Membership values, never rows.

Who is in a class is never listed, not even to its reps: views carry counts
only. A rep names the next rep with a one-time rep code, kept as a hash.
"""
from __future__ import annotations

import hashlib
import secrets
import uuid
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.exc import IntegrityError

from campus_engine.text import long_day
from src.core.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError
from src.domains.catalogue.universities.services import university_service as catalogue
from src.extensions import db

from ..constants import (
    CODE_ALPHABET,
    INVITE_LENGTH,
    MAX_CLASSES,
    MAX_REPS,
    REP_CODE_HOURS,
    REP_CODE_LENGTH,
    TIMEZONE,
)
from ..models import ClassMember, ModuleClass, RepInvite
from ..repositories import class_repository as repo

CODE_NOT_FOUND = "That code doesn't match a class, or it has expired."


@dataclass(frozen=True)
class Membership:
    """What other features may know about one of the student's classes."""

    class_id: uuid.UUID
    role: str
    module_code: str
    module_name: str | None
    university: str
    campus: str | None
    year: int

    @property
    def is_rep(self) -> bool:
        return self.role == "rep"


def _today() -> date:
    """Today in South Africa: every student's day."""
    return datetime.now(ZoneInfo(TIMEZONE)).date()


def _now() -> datetime:
    return datetime.now(UTC)


def _field_error(field: str, message: str) -> ValidationError:
    return ValidationError("Please check the highlighted fields.", errors=[{field: [message]}])


def _random_code(length: int) -> str:
    return "".join(secrets.choice(CODE_ALPHABET) for _ in range(length))


def _hash(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def _membership(m: ClassMember) -> Membership:
    c = m.module_class
    return Membership(c.id, m.role, c.module_code, c.module_name, c.university, c.campus, c.year)


# ----------------------------------------------------- for other features


def membership(user, class_id: uuid.UUID) -> Membership:
    """The student's place in a class; 404 if they're not in it."""
    m = repo.membership(user.id, class_id)
    if m is None:
        raise NotFoundError("We couldn't find that class.", code="CLASS_NOT_FOUND")
    return _membership(m)


def require_rep(user, class_id: uuid.UUID) -> Membership:
    """As membership(), and only a rep gets past: a member who isn't one gets 403."""
    m = membership(user, class_id)
    if not m.is_rep:
        raise ForbiddenError("Only a class rep can do that.", code="REP_ONLY")
    return m


def memberships(user) -> list[Membership]:
    return [_membership(m) for m in repo.memberships(user.id)]


# ------------------------------------------------------------- the routes


def mine(user) -> dict:
    rows = repo.memberships(user.id)
    counts = repo.counts([m.class_id for m in rows])
    return {"classes": [_view(m.module_class, m.role, counts.get(m.class_id, (0, 0))) for m in rows]}


def create(user, body: dict) -> dict:
    """A new class, with the student who made it as its first rep."""
    try:
        uni = catalogue.get(body["university"])
    except NotFoundError:
        raise _field_error("university", "We don't have that university.") from None
    campus_ids = [c.id for c in uni.campuses]
    campus = body["campus"]
    if campus is None and campus_ids:
        raise _field_error("campus", "Choose the class's campus.")
    if campus is not None and campus not in campus_ids:
        raise _field_error("campus", f"{uni.name} has no such campus.")
    this_year = _today().year
    if body["year"] not in (this_year, this_year + 1):
        raise _field_error("year", f"Choose {this_year} or {this_year + 1}.")
    _check_room(user)

    row = ModuleClass(
        university=uni.university,
        campus=campus,
        module_code=" ".join(body["module_code"].split()).upper(),
        module_name=" ".join(body["module_name"].split()) if body["module_name"] else None,
        year=body["year"],
        invite_code=_new_invite_code(),
    )
    repo.add(row)
    db.session.flush()
    repo.add(ClassMember(class_id=row.id, user_id=user.id, role="rep"))
    db.session.commit()
    return {"class": _view(row, "rep", (1, 1))}


def join(user, raw_code: str) -> dict:
    """Join with the class's invite code, or become a rep with a rep code."""
    code = "".join(ch for ch in raw_code.upper() if ch in CODE_ALPHABET)
    if len(code) == INVITE_LENGTH:
        return _join_class(user, code)
    if len(code) == REP_CODE_LENGTH:
        return _join_as_rep(user, code)
    raise NotFoundError(CODE_NOT_FOUND, code="CODE_NOT_FOUND")


def rep_code(user, class_id: uuid.UUID) -> dict:
    """A one-time code for the next rep. Shown once: only its hash is kept."""
    require_rep(user, class_id)
    repo.lock_class(class_id)
    now = _now()
    reps = repo.count_reps(class_id)
    if reps >= MAX_REPS:
        raise ConflictError(f"This class already has {MAX_REPS} reps.", code="REPS_FULL")
    if reps + repo.count_open_rep_invites(class_id, now) >= MAX_REPS:
        raise ConflictError(
            f"The rep codes already waiting would fill the class's {MAX_REPS} rep places. "
            f"A code that isn't used expires after {REP_CODE_HOURS} hours.",
            code="REP_CODES_WAITING",
        )
    code = _random_code(REP_CODE_LENGTH)
    expires = now + timedelta(hours=REP_CODE_HOURS)
    repo.add(RepInvite(class_id=class_id, code_hash=_hash(code), expires_at=expires))
    db.session.commit()
    local = expires.astimezone(ZoneInfo(TIMEZONE))
    return {
        "code": code,
        "expires_at": expires.isoformat(),
        "lines": [
            "Give this code to the classmate who'll be a rep: they enter it where they'd join a class. "
            f"It works once, until {long_day(local.date())} at {local:%H:%M}."
        ],
    }


def leave(user, class_id: uuid.UUID) -> dict:
    m = repo.membership(user.id, class_id)
    if m is None:
        raise NotFoundError("We couldn't find that class.", code="CLASS_NOT_FOUND")
    repo.delete(m)
    db.session.commit()
    return {}


def leave_all(user) -> list[uuid.UUID]:
    """The student leaves every class they're in: the demo's daily reset (and DELETE /me's later).
    Returns the classes they left."""
    rows = repo.memberships(user.id)
    left = [m.class_id for m in rows]
    for m in rows:
        repo.delete(m)
    db.session.commit()
    return left


def delete_if_empty(class_ids: list[uuid.UUID]) -> int:
    """Of these classes, the ones nobody is in any more go, with their events."""
    n = repo.delete_empty(class_ids)
    db.session.commit()
    return n


# ---------------------------------------------------------------- helpers


def _check_room(user) -> None:
    if repo.count_memberships(user.id) >= MAX_CLASSES:
        raise _field_error("classes", f"You can be in up to {MAX_CLASSES} classes: leave an old one first.")


def _new_invite_code() -> str:
    for _ in range(10):
        code = _random_code(INVITE_LENGTH)
        if not repo.invite_code_taken(code):
            return code
    raise RuntimeError("couldn't find a free invite code")  # 31^8 codes: never in practice


def _join_class(user, code: str) -> dict:
    row = repo.class_by_invite(code)
    if row is None:
        raise NotFoundError(CODE_NOT_FOUND, code="CODE_NOT_FOUND")
    existing = repo.membership(user.id, row.id)
    if existing is not None:
        return {"class": _view(row, existing.role), "joined": False}
    _check_room(user)
    repo.add(ClassMember(class_id=row.id, user_id=user.id, role="student"))
    try:
        db.session.commit()
    except IntegrityError:  # the same tap twice at once: they're in either way
        db.session.rollback()
        return {"class": _view(row, repo.membership(user.id, row.id).role), "joined": False}
    return {"class": _view(row, "student"), "joined": True}


def _join_as_rep(user, code: str) -> dict:
    invite = repo.rep_invite(_hash(code))
    if invite is None or invite.expires_at <= _now():
        raise NotFoundError(CODE_NOT_FOUND, code="CODE_NOT_FOUND")
    row = repo.lock_class(invite.class_id)
    if repo.count_reps(row.id) >= MAX_REPS:
        raise ConflictError(f"This class already has {MAX_REPS} reps.", code="REPS_FULL")
    existing = repo.membership(user.id, row.id)
    if existing is not None and existing.role == "rep":
        raise ConflictError("You're already a rep for this class.", code="ALREADY_REP")
    if existing is not None:
        existing.role = "rep"
    else:
        _check_room(user)
        repo.add(ClassMember(class_id=row.id, user_id=user.id, role="rep"))
    repo.delete(invite)
    db.session.commit()
    return {"class": _view(row, "rep"), "joined": True}


def _view(row: ModuleClass, role: str, count: tuple[int, int] | None = None) -> dict:
    uni = catalogue.packs().get(row.university)
    campuses = {c.id: c.name for c in uni.campuses} if uni else {}
    members, reps = count if count is not None else repo.counts([row.id]).get(row.id, (0, 0))
    return {
        "id": str(row.id),
        "university": row.university,
        "university_name": uni.name if uni else None,
        "campus": row.campus,
        "campus_name": campuses.get(row.campus) if row.campus else None,
        "module_code": row.module_code,
        "module_name": row.module_name,
        "year": row.year,
        "invite_code": row.invite_code,
        "role": role,
        "members": members,
        "reps": reps,
    }
