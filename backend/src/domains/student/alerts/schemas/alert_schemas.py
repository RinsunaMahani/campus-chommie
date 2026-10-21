"""What the alerts and support routes accept: nothing. Any query parameter is refused."""
from __future__ import annotations

from marshmallow import RAISE, Schema
from marshmallow import ValidationError as MarshmallowError

from src.core.exceptions import ValidationError


class NoQuerySchema(Schema):
    """No query parameters."""

    class Meta:
        unknown = RAISE


def load(schema: Schema, data) -> dict:
    """Validate a query string; one 422 with every field's message."""
    try:
        return schema.load(data if isinstance(data, dict) else {})
    except MarshmallowError as e:
        raise ValidationError("Please check the highlighted fields.", errors=[e.messages]) from None
