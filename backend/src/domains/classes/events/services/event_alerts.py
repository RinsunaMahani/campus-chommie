"""
Class updates: when a rep confirms a new, moved or cancelled event, every
other member of the class gets an alert, never the rep who confirmed it.
The wording is platform/notifications' fixed templates, with only the
module, the kind and the dates in it: never who, and never what someone
typed (a title or a venue). Called after the commit; publishing never
raises, and a student can switch class updates off.
"""
from __future__ import annotations

import uuid
from datetime import date, time

from campus_engine.text import long_day
from src.shared.notifications.notification_types import NotificationEvent
from src.shared.notifications.notifications import publish_notification, safely


def when(kind: str, on: date, at: time | None) -> str:
    """The date as the alerts say it: "on Tue 20 Oct 2026 at 08:00", or "due ..." for an assignment."""
    return ("due " if kind == "assignment" else "on ") + long_day(on) + (f" at {at:%H:%M}" if at else "")


@safely
def tell_class(
    member_ids: list[uuid.UUID],
    *,
    template: str,
    class_id: uuid.UUID,
    event_id: uuid.UUID,
    version: int,
    module: str,
    kind: str,
    on: date,
    at: time | None,
    was: tuple[date, time | None] | None = None,
) -> None:
    params = {"module": module, "kind": kind, "when": when(kind, on, at)}
    if was is not None:
        params["was"] = when(kind, *was)
    for user_id in member_ids:
        publish_notification(
            NotificationEvent(
                recipient_user_id=user_id,
                template=template,
                dedupe_key=f"class_event:{event_id}:v{version}",
                params=params,
                link_type="class",
                link_id=str(class_id),
            )
        )
