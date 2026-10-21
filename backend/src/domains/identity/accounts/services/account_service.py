"""
accounts -- the user record. The ONLY writer of identity.users and
identity.consents; auth/ and devices/ call these functions.
"""
from __future__ import annotations

import uuid
from typing import Optional

from flask import current_app

from src.core.base_model import utcnow
from src.core.exceptions import ValidationError
from src.shared.security.security import validate_password_complexity
from src.shared.validation.identifiers import normalize_email

from ..models import AccountStatus, Consent, LegalDocument, SignUpMethod, User
from ..repositories import user_repository


def normalized(email: str) -> str:
    return normalize_email(email or "")


def get(user_id: uuid.UUID | str) -> Optional[User]:
    try:
        return user_repository.get_by_id(uuid.UUID(str(user_id)))
    except ValueError:
        return None


def find_by_email(email: str) -> Optional[User]:
    return user_repository.get_by_email(normalized(email))


def create_unverified(email: str, method: SignUpMethod = SignUpMethod.EMAIL) -> User:
    return user_repository.add(
        User(
            email=normalized(email),
            status=AccountStatus.UNVERIFIED.value,
            signed_up_with=method.value,
        )
    )


def restart_unverified(user: User) -> User:
    """Someone signs up again with an email that was never verified. The
    earlier attempt proved nothing about who owns the address, so it
    starts over (the caller replaces the password)."""
    return user


def mark_verified(user: User) -> None:
    if user.status == AccountStatus.UNVERIFIED.value:
        user.status = AccountStatus.ACTIVE.value
    user.email_verified_at = user.email_verified_at or utcnow()


def record_login(user: User) -> None:
    user.last_login_at = utcnow()


def check_consent_versions(privacy_version: str, terms_version: str) -> None:
    """The app must send the versions the user actually saw. An old app
    showing an older document must not record consent to the new one."""
    cfg = current_app.config
    if privacy_version != cfg["PRIVACY_POLICY_VERSION"] or terms_version != cfg["TERMS_VERSION"]:
        raise ValidationError(
            "Please update the app and accept the latest Privacy Policy and Terms of Use.",
            code="CONSENT_OUTDATED",
        )


#: The wording of the "I am 18 or older" confirmation. Bump it if the
#: sign-up wording changes, so the records say which wording was confirmed.
AGE_CONFIRMATION_VERSION = "18-or-older.v1"


def check_age_confirmed(confirmed: object) -> None:
    """Accounts are for people aged 18 or older (POPIA: a child's personal
    information needs a guardian's consent, so we don't take it). The
    schema already insists on true; this is the rule itself."""
    if confirmed is not True:
        raise ValidationError("You must be 18 or older to create an account.", code="AGE_NOT_CONFIRMED")


def record_consents(user: User, privacy_version: str, terms_version: str, ip: Optional[str], user_agent: Optional[str]) -> None:
    """The documents accepted and the age confirmed at sign-up, one row
    each, all stamped with the same moment, IP and app."""
    now = utcnow()
    for document, version in (
        (LegalDocument.PRIVACY_POLICY, privacy_version),
        (LegalDocument.TERMS_OF_USE, terms_version),
        (LegalDocument.AGE_CONFIRMATION, AGE_CONFIRMATION_VERSION),
    ):
        user_repository.add_consent(
            Consent(
                user_id=user.id,
                document=document.value,
                version=version,
                accepted_at=now,
                ip_address=ip,
                user_agent=(user_agent or "")[:300] or None,
            )
        )


def public_view(user: User) -> dict:
    """What the app may see about the signed-in user. Never secrets."""
    return {
        "id": str(user.id),
        "email": user.email,
        "status": user.status,
        "signed_up_with": user.signed_up_with,
        "email_verified": user.email_verified_at is not None,
        # The app shows "Demo data: fictional student" on these.
        "demo": user.is_demo,
    }


def deactivate(user: User) -> None:
    """Closed by its owner. Personal data is removed later by the retention
    job, keeping only what the law requires (see the Privacy Policy)."""
    user.status = AccountStatus.DEACTIVATED.value


def consents_view(user: User) -> list[dict]:
    return [
        {"document": c.document, "version": c.version, "accepted_at": c.accepted_at.isoformat()}
        for c in user_repository.consents_for(user.id)
    ]


def unverified_older_than(cutoff) -> list[User]:
    """Sign-ups whose email was never confirmed, created before `cutoff`."""
    return User.query.filter(User.status == AccountStatus.UNVERIFIED.value, User.created_at < cutoff).all()


def delete_unverified(user: User) -> None:
    """Hard delete (cascades to its credentials, codes and consents). Only
    for never-verified sign-ups: a real account is closed, not deleted."""
    if user.status != AccountStatus.UNVERIFIED.value:
        raise ValueError("Only unverified sign-ups can be deleted this way.")
    from src.extensions import db

    db.session.delete(user)


#: Recorded with a demo account's consents, so nobody mistakes them for a person's.
DEMO_USER_AGENT = "flask seed: demo account (fictional student)"


def ensure_demo_account(email: str, password: str) -> User:
    """A demo account for the judges, made or refreshed by `flask seed`: verified, consented, flagged as
    demo, with the shared password from the environment. A real account is never turned into one.
    The caller commits."""
    user = find_by_email(email)
    if user is not None and not user.is_demo:
        raise ValueError(f"{normalized(email)} belongs to a real account, so it can't be a demo account.")
    if user is None:
        user = user_repository.add(
            User(
                email=normalized(email),
                status=AccountStatus.UNVERIFIED.value,
                signed_up_with=SignUpMethod.EMAIL.value,
                is_demo=True,
            )
        )
        mark_verified(user)
        cfg = current_app.config
        record_consents(user, cfg["PRIVACY_POLICY_VERSION"], cfg["TERMS_VERSION"], None, DEMO_USER_AGENT)
    # auth owns passwords; imported here because auth imports this module.
    from src.domains.identity.auth.services import auth_service

    auth_service.set_demo_password(user, password)
    return user


def check_demo_password(password: str) -> list[str]:
    """What's wrong with a demo password, by the same rule as everyone's (empty: nothing)."""
    return validate_password_complexity(password or "")


def create_verified(email: str, method: SignUpMethod) -> User:
    """A new account whose email is already proven (e.g. by Google)."""
    user = user_repository.add(
        User(
            email=normalized(email),
            status=AccountStatus.UNVERIFIED.value,
            signed_up_with=method.value,
        )
    )
    mark_verified(user)
    return user


def claim_unverified_with(user: User, method: SignUpMethod) -> None:
    """The real owner of the email (proven by Google) takes over a sign-up
    that was never verified. Whoever started it proved nothing."""
    user.signed_up_with = method.value
    mark_verified(user)
