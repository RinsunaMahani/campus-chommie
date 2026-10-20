"""What the colleges routes accept: a search and a few known filters on the list, a name on the check,
nothing on one college. Anything else is refused, and nothing asked is about the learner."""
from __future__ import annotations

from typing import get_args

from marshmallow import RAISE, Schema, ValidationError, fields, validate, validates

from campus_engine.schemas import CollegeKind, CollegeStatus, Province
from src.core.exceptions import ValidationError as ApiValidationError

from ..constants import MAX_QUERY


class _Strict(Schema):
    class Meta:
        unknown = RAISE


def _no_control_characters(value: str) -> None:
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
        raise ValidationError("Use letters, numbers and punctuation only.")


class NoQuerySchema(_Strict):
    """One college takes no query parameters; any is refused."""


class CollegeListSchema(_Strict):
    """GET /colleges?q=damelin&kind=private_college&province=Gauteng&status=registered&page=2"""

    q = fields.String(validate=validate.Length(min=1, max=MAX_QUERY))
    kind = fields.String(validate=validate.OneOf(get_args(CollegeKind)))
    province = fields.String(validate=validate.OneOf(get_args(Province)))
    status = fields.String(validate=validate.OneOf(get_args(CollegeStatus)))
    page = fields.Integer(validate=validate.Range(min=1, max=100), strict=False)

    @validates("q")
    def _clean(self, value: str, **_kwargs) -> None:
        _no_control_characters(value)


class CheckSchema(_Strict):
    """GET /colleges/check?name=Damelin  (a name or a registration number)"""

    name = fields.String(required=True, validate=validate.Length(min=1, max=MAX_QUERY))

    @validates("name")
    def _clean(self, value: str, **_kwargs) -> None:
        _no_control_characters(value)


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
