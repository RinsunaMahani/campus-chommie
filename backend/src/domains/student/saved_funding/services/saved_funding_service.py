"""
Saved funding: what a student saved, each funder with today's status from the funding pack, and
the reminders that go with it. The funding feature owns the pack and its cards; this feature owns
only the student's list.

  mine(user)                 the saved funders, open first
  save(user, funder_id)      saving again is fine; a funder the pack doesn't list is a 404
  unsave(user, funder_id)    one the student hasn't saved is a 404
  daily_reminders(user)      the first poll of a student's day: an alert for each saved funder that
                             opened after they saved it or closes within 7 or 1 days (config), each
                             once; off when the student switches funding reminders off
  export_for / erase_all_for POPIA's export, and the demo's daily reset

Every call acts on the signed-in student only.
"""
from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

from sqlalchemy.exc import IntegrityError

from src.core.exceptions import NotFoundError, ValidationError
from src.domains.catalogue.funding.services import funding_service as funding
from src.extensions import db
from src.shared.notifications.notification_types import NotificationEvent
from src.shared.notifications.notifications import publish_notification

from ..constants import MAX_SAVED, TIMEZONE
from ..repositories import saved_funding_repository as repo


def _today() -> date:
    """Today in South Africa: every application date is SAST."""
    return datetime.now(ZoneInfo(TIMEZONE)).date()


def mine(user) -> dict:
    return funding.saved_list({row.funder_id: row.saved_on for row in repo.for_user(user.id)}, _today())


def save(user, funder_id: str) -> dict:
    if not funding.has(funder_id):
        raise NotFoundError("We don't have that funder.", code="FUNDER_NOT_FOUND")
    today = _today()
    row = repo.one(user.id, funder_id)
    if row is None:
        if repo.count(user.id) >= MAX_SAVED:
            raise ValidationError("Please check the highlighted fields.", errors=[{"funding": [f"You can save up to {MAX_SAVED}."]}])
        row = repo.add(user.id, funder_id, today)
        try:
            db.session.commit()
        except IntegrityError:  # saved twice at once: the other request kept it
            db.session.rollback()
            row = repo.one(user.id, funder_id)
    return {"funder": funding.saved_card(funder_id, row.saved_on, today)}


def unsave(user, funder_id: str) -> dict:
    row = repo.one(user.id, funder_id)
    if row is None:
        raise NotFoundError("You haven't saved that funder.", code="SAVED_FUNDER_NOT_FOUND")
    repo.delete(row)
    db.session.commit()
    return {}


def daily_reminders(user) -> None:
    """Registered as a daily check (src/__init__.py): runs on the student's first poll of the day."""
    saved = {row.funder_id: row.saved_on for row in repo.for_user(user.id)}
    if not saved:
        return
    for r in funding.reminders(saved, _today()):
        params = {"funder": r.funder, "intake": r.intake} | ({"when": r.when} if r.when else {})
        publish_notification(
            NotificationEvent(
                recipient_user_id=user.id,
                template=f"funding.{r.template}",
                dedupe_key=f"funding:{r.key}",
                params=params,
                link_type="funding",
                link_id=r.funder_id,
            )
        )


def export_for(user) -> dict:
    """POPIA export: every funder the student saved, and when."""
    return {
        "saved": [
            {"funder": row.funder_id, "name": funding.short_name(row.funder_id), "saved_on": row.saved_on.isoformat()}
            for row in repo.for_user(user.id)
        ]
    }


def erase_all_for(user) -> None:
    """Every saved funder of this student, deleted for real: the demo's daily reset."""
    repo.erase_all(user.id)
    db.session.commit()
