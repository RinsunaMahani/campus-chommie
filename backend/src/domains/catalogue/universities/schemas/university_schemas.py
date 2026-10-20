"""What the catalogue routes accept: nothing on a university; a search and a university on the programme list."""
from __future__ import annotations

from marshmallow import RAISE, Schema, fields, validate, validates
from marshmallow import ValidationError as MarshmallowError

from src.core.exceptions import ValidationError


class _Strict(Schema):
    class Meta:
        unknown = RAISE


class NoQuerySchema(_Strict):
    """The catalogue takes no query parameters; any is refused."""


class ProgrammeListSchema(_Strict):
    """GET /programmes?q=nursing&university=up&page=2 (all optional)"""

    q = fields.String(validate=validate.Length(min=1, max=120))
    university = fields.String(validate=validate.Regexp(r"^[a-z]{2,12}$"))
    page = fields.Integer(validate=validate.Range(min=1, max=200), strict=False)

    @validates("q")
    def _clean(self, value: str, **_kwargs) -> None:
        if any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
            raise MarshmallowError("Use letters, numbers and punctuation only.")


def query(args) -> dict:
    """The query string as a dict, refusing a parameter given twice."""
    repeated = sorted(key for key, values in args.to_dict(flat=False).items() if len(values) > 1)
    if repeated:
        raise ValidationError("Please check the highlighted fields.", errors=[{key: ["Give it once."] for key in repeated}])
    return args.to_dict()


def load(schema: Schema, data) -> dict:
    """Validate a JSON body or query string; one 422 with every field's message."""
    try:
        return schema.load(data if isinstance(data, dict) else {})
    except MarshmallowError as e:
        raise ValidationError("Please check the highlighted fields.", errors=[e.messages]) from None
