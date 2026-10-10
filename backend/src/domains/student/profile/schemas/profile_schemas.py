"""
What the profile routes accept. Strict: unknown fields are refused, so
nothing beyond university and campus can be stored here.
"""
from __future__ import annotations

from marshmallow import RAISE, Schema, fields, validate
from marshmallow import ValidationError as MarshmallowError

from src.core.exceptions import ValidationError


class _Strict(Schema):
    class Meta:
        unknown = RAISE


class ProfileSchema(_Strict):
    university = fields.String(required=True, validate=validate.Length(min=1, max=40))
    campus = fields.String(load_default=None, allow_none=True, validate=validate.Length(min=1, max=40))


def load(schema: Schema, data) -> dict:
    """Validate a JSON body; one 422 with every field's message."""
    try:
        return schema.load(data if isinstance(data, dict) else {})
    except MarshmallowError as e:
        raise ValidationError("Please check the highlighted fields.", errors=[e.messages]) from None
