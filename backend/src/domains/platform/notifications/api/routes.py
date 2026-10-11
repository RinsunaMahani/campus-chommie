"""
/api/v1/me/notifications -- the signed-in student's own alerts.

  GET  /me/notifications?before=<id>&limit=20   {notifications, next_before}
  GET  /me/notifications/unread                 {unread: {count, latest_id}}
  POST /me/notifications/<id>/read              {notification, unread}
  POST /me/notifications/read-all               -> {unread}
  GET  /me/notifications/switches               {switches}: the topics a student may switch off
  PUT  /me/notifications/switches               {class_updates: false, funding_reminders: false} -> {switches}

Thin: validate -> service -> answer. Rate-limited per user; another
user's alert is the same 404 as one that doesn't exist.
"""
from __future__ import annotations

import uuid

from flask import request

from src.api import api_bp
from src.core.decorators import auth_required, current_user
from src.core.responses import success_response
from src.shared.rate_limit.keys import per_user
from src.shared.rate_limit.limiter import limiter

from ..constants import CHANGE_LIMIT, READ_LIMIT
from ..schemas.notification_schemas import ListQuerySchema, NoQuerySchema, ReadAllSchema, SwitchesSchema, load
from ..services import notification_service as service

BASE = "/me/notifications"


@api_bp.get(BASE)
@limiter.limit(READ_LIMIT, key_func=per_user)
@auth_required
def my_notifications():
    q = load(ListQuerySchema(), request.args.to_dict())
    items, next_before = service.list_for(current_user(), q["before"], q["limit"])
    return success_response({"notifications": items, "next_before": next_before})


@api_bp.get(f"{BASE}/unread")
@limiter.limit(READ_LIMIT, key_func=per_user)
@auth_required
def my_unread_notifications():
    return success_response({"unread": service.unread(current_user())})


@api_bp.post(f"{BASE}/<uuid:notification_id>/read")
@limiter.limit(READ_LIMIT, key_func=per_user)
@auth_required
def read_notification(notification_id: uuid.UUID):
    item, unread = service.read(current_user(), notification_id)
    return success_response({"notification": item, "unread": unread})


@api_bp.post(f"{BASE}/read-all")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def read_all_notifications():
    load(ReadAllSchema(), request.get_json(silent=True))
    return success_response({"unread": service.read_all(current_user())})


@api_bp.get(f"{BASE}/switches")
@limiter.limit(READ_LIMIT, key_func=per_user)
@auth_required
def my_notification_switches():
    load(NoQuerySchema(), request.args.to_dict())
    return success_response(service.switches(current_user()))


@api_bp.put(f"{BASE}/switches")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def change_my_notification_switches():
    changes = load(SwitchesSchema(), request.get_json(silent=True))
    return success_response(service.set_switches(current_user(), changes))
