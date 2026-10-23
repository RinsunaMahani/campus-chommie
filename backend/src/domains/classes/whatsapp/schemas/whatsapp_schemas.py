"""
What the WhatsApp routes accept. The app's routes take no query and no body. The webhook's handshake takes
exactly Meta's three hub.* parameters; its POST body is Meta's own JSON, checked by signature first and then
read defensively by the service (anything not in the shape we expect is ignored, never trusted).
"""
from __future__ import annotations

from marshmallow import RAISE, Schema, fields, validate
from marshmallow import ValidationError as MarshmallowError

from src.core.exceptions import ValidationError


class _Strict(Schema):
    class Meta:
        unknown = RAISE


class NothingSchema(_Strict):
    """No query parameters, and no body: anything sent is refused."""


class HandshakeSchema(_Strict):
    mode = fields.String(required=True, data_key="hub.mode", validate=validate.Length(max=32))
    verify_token = fields.String(required=True, data_key="hub.verify_token", validate=validate.Length(max=256))
    #: Echoed back as text: digits and letters only, so nothing else can be reflected.
    challenge = fields.String(required=True, data_key="hub.challenge", validate=validate.Regexp(r"^[A-Za-z0-9_-]{1,128}$"))


def load(schema: Schema, data) -> dict:
    if not isinstance(data, dict):
        raise ValidationError("Please check the highlighted fields.", errors=[{"_schema": ["Send no body."]}])
    try:
        return schema.load(data)
    except MarshmallowError as e:
        raise ValidationError("Please check the highlighted fields.", errors=[e.messages]) from None
