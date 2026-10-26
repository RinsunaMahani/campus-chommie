"""What the alerts and support routes accept: nothing, except which week a review is for. Any other query is refused."""
from __future__ import annotations

from marshmallow import RAISE, Schema, fields, validate
from marshmallow import ValidationError as MarshmallowError

from src.core.exceptions import ValidationError


class NoQuerySchema(Schema):
    """No query parameters."""

    class Meta:
        unknown = RAISE


class WeekReviewQuerySchema(NoQuerySchema):
    """GET /me/week-review: which week, by name only (never a date a client picks)."""

    week = fields.String(load_default="auto", validate=validate.OneOf(("auto", "this", "last")))


def load(schema: Schema, data) -> dict:
    """Validate a query string; one 422 with every field's message."""
    try:
        return schema.load(data if isinstance(data, dict) else {})
    except MarshmallowError as e:
        raise ValidationError("Please check the highlighted fields.", errors=[e.messages]) from None


def load_query(schema: Schema, args) -> dict:
    """A query string where each parameter is given once (a repeated one is refused, never guessed between)."""
    repeated = sorted(key for key, values in args.to_dict(flat=False).items() if len(values) > 1)
    if repeated:
        raise ValidationError("Please check the highlighted fields.", errors=[{key: ["Give it once."] for key in repeated}])
    return load(schema, args.to_dict())
