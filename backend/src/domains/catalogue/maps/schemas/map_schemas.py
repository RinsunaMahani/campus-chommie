"""What the map route accepts: one optional campus id, given once. Anything else is refused."""
from __future__ import annotations

from marshmallow import RAISE, Schema, ValidationError, fields, validate

from src.core.exceptions import ValidationError as ApiValidationError


class _Strict(Schema):
    class Meta:
        unknown = RAISE


class MapQuerySchema(_Strict):
    """GET /universities/<id>/map?campus=hatfield"""

    campus = fields.String(validate=[validate.Length(min=1, max=40), validate.Regexp(r"^[a-z0-9_]+$")])


def query(args) -> dict:
    """The query string as a dict, refusing a parameter given twice."""
    repeated = sorted(key for key, values in args.to_dict(flat=False).items() if len(values) > 1)
    if repeated:
        raise ApiValidationError("Please check the highlighted fields.", errors=[{key: ["Give it once."] for key in repeated}])
    return args.to_dict()


def load(schema: Schema, data) -> dict:
    """Validate a query string; one 422 with every field's message."""
    try:
        return schema.load(data if isinstance(data, dict) else {})
    except ValidationError as e:
        raise ApiValidationError("Please check the highlighted fields.", errors=[e.messages]) from None
