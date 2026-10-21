"""What the catalogue routes accept: no query parameters at all."""
from __future__ import annotations

from marshmallow import RAISE, Schema
from marshmallow import ValidationError as MarshmallowError

from src.core.exceptions import ValidationError


class _Strict(Schema):
    class Meta:
        unknown = RAISE


class NoQuerySchema(_Strict):
    """The catalogue takes no query parameters; any is refused."""


def load(schema: Schema, data) -> dict:
    """Validate a JSON body or query string; one 422 with every field's message."""
    try:
        return schema.load(data if isinstance(data, dict) else {})
    except MarshmallowError as e:
        raise ValidationError("Please check the highlighted fields.", errors=[e.messages]) from None
