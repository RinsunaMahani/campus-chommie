"""What the funding routes accept: a few known filters on the list, nothing on one funder. Anything
else is refused, and no filter is ever about the learner (income, race or any other personal detail)."""
from __future__ import annotations

from marshmallow import RAISE, Schema, ValidationError, fields, validate, validates

from campus_engine.funding import FILTERS
from campus_engine.schemas import FIELDS
from src.core.exceptions import ValidationError as ApiValidationError

from ..constants import MAX_FIELDS


class _Strict(Schema):
    class Meta:
        unknown = RAISE


class NoQuerySchema(_Strict):
    """One funder takes no query parameters; any is refused."""


class FundingListSchema(_Strict):
    """GET /funding?field=engineering,computing&status=open&kind=bursary&stage=first_year"""

    field = fields.String(validate=validate.Length(min=1, max=400))
    status = fields.String(validate=validate.OneOf(sorted(FILTERS)))
    kind = fields.String(validate=validate.OneOf(["bursary", "merit_award", "loan"]))
    stage = fields.String(validate=validate.OneOf(["first_year", "senior", "postgraduate"]))

    @validates("field")
    def _known_fields(self, value: str, **_kwargs) -> None:
        tags = value.split(",")
        if len(tags) > MAX_FIELDS:
            raise ValidationError(f"Name at most {MAX_FIELDS} fields.")
        unknown = [t for t in tags if t not in FIELDS]
        if unknown or len(set(tags)) != len(tags):
            raise ValidationError("Use field ids from the list, each once, separated by commas.")


def query(args) -> dict:
    """The query string as a dict, refusing a parameter given twice (?status=open&status=closed)."""
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
