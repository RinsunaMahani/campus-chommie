"""
Notification event contract -- neutral ground, mirroring shared/audit's
own audit_types.py (living in shared/ keeps the dependency arrow right:
any publisher imports this; the persisting domain,
domains/platform/notifications, imports this too; neither imports the
other).

An event names a TEMPLATE and fills its params; it never carries
ready-made wording. The persisting side owns the templates, so a
publisher can't invent an alert. The title is fixed text; params only
ever reach the body.

dedupe_key makes an event land once per recipient, however often the
action behind it is retried (e.g. f"order:{id}:{status}").
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional
from uuid import UUID


@dataclass
class NotificationEvent:
    """One alert for one user. link_type / link_id: what tapping it opens
    (e.g. "order" and the order's id); both None for an alert that only
    informs."""

    recipient_user_id: str | UUID
    template: str
    dedupe_key: str
    params: dict[str, Any] = field(default_factory=dict)
    link_type: Optional[str] = None
    link_id: Optional[str] = None
