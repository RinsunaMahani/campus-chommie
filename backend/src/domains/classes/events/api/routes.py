"""
/api/v1 -- class announcements, the rep's confirmation, verified events,
flags and the week strip.

  POST   /classes/<id>/announcements     member: {text, sent_on?} -> 201 {candidate}: what we read, what to check
  GET    /classes/<id>/candidates        waiting for a rep: all of them for a rep, your own otherwise
  POST   /candidates/<id>/confirm        rep only: the edited event -> {event, lines}; a change updates the event
  POST   /candidates/<id>/discard        a rep, or the student who sent it
  GET    /classes/<id>/events?from=&to=  member: verified events with their changes (reps also see flag counts)
  POST   /events/<id>/flag               member: {reason}
  DELETE /events/<id>/flag
  GET    /week?weeks=8&from=YYYY-MM-DD   the week strip: Manageable, Busy or Heavy, with the calendar

Thin: validate -> service -> answer. Rate-limited per student; a class,
candidate or event you can't see is the same 404 as one that doesn't exist.
"""
from __future__ import annotations

import uuid

from flask import request

from src.api import api_bp
from src.core.decorators import auth_required, current_user
from src.core.responses import success_response
from src.shared.rate_limit.keys import per_user
from src.shared.rate_limit.limiter import limiter

from ..constants import ANNOUNCE_LIMIT, CHANGE_LIMIT, READ_LIMIT
from ..schemas.events_schemas import (
    AnnouncementSchema,
    ConfirmSchema,
    EventsQuerySchema,
    FlagSchema,
    NoBodySchema,
    NoQuerySchema,
    WeekQuerySchema,
    load,
)
from ..services import events_service as service
from ..services import week_service


@api_bp.post("/classes/<uuid:class_id>/announcements")
@limiter.limit(ANNOUNCE_LIMIT, key_func=per_user)
@auth_required
def add_announcement(class_id: uuid.UUID):
    body = load(AnnouncementSchema(), request.get_json(silent=True))
    return success_response(service.announce(current_user(), class_id, body), status_code=201)


@api_bp.get("/classes/<uuid:class_id>/candidates")
@limiter.limit(READ_LIMIT, key_func=per_user)
@auth_required
def class_candidates(class_id: uuid.UUID):
    load(NoQuerySchema(), request.args.to_dict())
    return success_response(service.candidates(current_user(), class_id))


@api_bp.post("/candidates/<uuid:candidate_id>/confirm")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def confirm_candidate(candidate_id: uuid.UUID):
    body = load(ConfirmSchema(), request.get_json(silent=True))
    return success_response(service.confirm(current_user(), candidate_id, body))


@api_bp.post("/candidates/<uuid:candidate_id>/discard")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def discard_candidate(candidate_id: uuid.UUID):
    load(NoBodySchema(), request.get_json(silent=True))
    return success_response(service.discard(current_user(), candidate_id))


@api_bp.get("/classes/<uuid:class_id>/events")
@limiter.limit(READ_LIMIT, key_func=per_user)
@auth_required
def class_events(class_id: uuid.UUID):
    query = load(EventsQuerySchema(), request.args.to_dict())
    return success_response(service.events(current_user(), class_id, query))


@api_bp.post("/events/<uuid:event_id>/flag")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def flag_event(event_id: uuid.UUID):
    body = load(FlagSchema(), request.get_json(silent=True))
    return success_response(service.flag(current_user(), event_id, body["reason"]))


@api_bp.delete("/events/<uuid:event_id>/flag")
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def unflag_event(event_id: uuid.UUID):
    return success_response(service.unflag(current_user(), event_id))


@api_bp.get("/week")
@limiter.limit(READ_LIMIT, key_func=per_user)
@auth_required
def my_week():
    query = load(WeekQuerySchema(), request.args.to_dict())
    return success_response(week_service.week(current_user(), query["weeks"], query["start"]))
