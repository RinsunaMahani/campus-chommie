"""What saved funding accepts: no query parameters and no body. The funder is in the path."""
from __future__ import annotations

from marshmallow import RAISE, Schema, ValidationError

from src.core.exceptions import ValidationError as ApiValidationError


class _Strict(Schema):
    class Meta:
        unknown = RAISE


class NothingSchema(_Strict):
    """No query parameters, and no body: anything sent is refused."""


def load(schema: Schema, data) -> dict:
    """Validate a query string or JSON body; one 422 with every field's message."""
    if not isinstance(data, dict):
        raise ApiValidationError("Please check the highlighted fields.", errors=[{"_schema": ["Send no body."]}])
    try:
        return schema.load(data)
    except ValidationError as e:
        raise ApiValidationError("Please check the highlighted fields.", errors=[e.messages]) from None
