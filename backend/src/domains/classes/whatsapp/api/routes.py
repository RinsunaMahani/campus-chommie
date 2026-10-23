"""
The WhatsApp bot's routes.

  GET    /webhooks/whatsapp   Meta's handshake: hub.mode=subscribe and our verify token -> the challenge, as text
  POST   /webhooks/whatsapp   Meta's messages, signed (X-Hub-Signature-256); always 200 once the signature holds
  GET    /me/whatsapp         {available, linked, linked_on, bot}
  POST   /me/whatsapp/code    a one-time link code -> {code, message, expires_at, minutes, bot, send_link}
  DELETE /me/whatsapp         unlink every number of this account -> {}

With the bot switched off (a secret missing) the webhook is a 404, as if it didn't exist. Thin: validate ->
service -> answer. The webhook is limited per address (Meta's servers), each sender inside the service.
"""
from __future__ import annotations

from flask import Response, request

from src.api import api_bp
from src.core.decorators import auth_required, current_user
from src.core.exceptions import ForbiddenError, NotFoundError
from src.core.responses import success_response
from src.shared.rate_limit.keys import per_user
from src.shared.rate_limit.limiter import limiter

from ..constants import CHANGE_LIMIT, CODE_LIMIT, READ_LIMIT, WEBHOOK_LIMIT
from ..schemas.whatsapp_schemas import HandshakeSchema, NothingSchema, load
from ..services import signature
from ..services import whatsapp_service as service

WEBHOOK = "/webhooks/whatsapp"
BASE = "/me/whatsapp"


def _bot_on() -> None:
    if not signature.available():
        raise NotFoundError("Resource not found", code="NOT_FOUND")


def _nothing_sent() -> None:
    load(NothingSchema(), request.args.to_dict())
    if request.get_data(cache=True):
        body = request.get_json(silent=True)
        load(NothingSchema(), body if body is not None else "not JSON")


@api_bp.get(WEBHOOK)
@limiter.limit(WEBHOOK_LIMIT)
def whatsapp_handshake():
    _bot_on()
    q = load(HandshakeSchema(), request.args.to_dict())
    if not signature.handshake_ok(q["mode"], q["verify_token"]):
        raise ForbiddenError("That verify token isn't ours.", code="BAD_VERIFY_TOKEN")
    return Response(q["challenge"], status=200, mimetype="text/plain")


@api_bp.post(WEBHOOK)
@limiter.limit(WEBHOOK_LIMIT)
def whatsapp_messages():
    _bot_on()
    raw = request.get_data(cache=True)
    answered = service.receive(raw, request.headers.get("X-Hub-Signature-256"), request.get_json(silent=True))
    return success_response({"answered": answered})


@api_bp.get(BASE)
@limiter.limit(READ_LIMIT, key_func=per_user)
@auth_required
def my_whatsapp():
    _nothing_sent()
    return success_response(service.status(current_user()))


@api_bp.post(f"{BASE}/code")
@limiter.limit(CODE_LIMIT, key_func=per_user)
@auth_required
def my_whatsapp_code():
    _nothing_sent()
    return success_response(service.new_code(current_user()), status_code=201)


@api_bp.delete(BASE)
@limiter.limit(CHANGE_LIMIT, key_func=per_user)
@auth_required
def unlink_my_whatsapp():
    _nothing_sent()
    return success_response(service.unlink(current_user()))
