"""
What the My marks routes accept. Strict: unknown fields are refused. A
percentage is a number from 0 to 100: text, true or false, NaN and infinity
are refused. Names can't be blank.
"""
from __future__ import annotations

import math

from marshmallow import RAISE, Schema, fields, validate
from marshmallow import ValidationError as MarshmallowError

from src.core.exceptions import ValidationError

from ..constants import CODE_MAX, DEFAULT_TARGET, NAME_MAX


class _Strict(Schema):
    class Meta:
        unknown = RAISE


class Percent(fields.Field):
    """A number from 0 to 100 (or above 0, for a weight)."""

    default_error_messages = {"invalid": "Enter a number from 0 to 100."}

    def __init__(self, *, above_zero: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.above_zero = above_zero

    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise self.make_error("invalid")
        if isinstance(value, float) and not math.isfinite(value):
            raise self.make_error("invalid")
        # Compared before float(): a 400-digit integer is refused, not overflowed.
        low_ok = value > 0 if self.above_zero else value >= 0
        if not low_ok or value > 100:
            raise MarshmallowError("Enter a number above 0, up to 100." if self.above_zero else "Enter a number from 0 to 100.")
        return float(value)


def _not_blank(value: str) -> None:
    if not value.strip():
        raise MarshmallowError("This can't be blank.")


_NAME = [validate.Length(min=1, max=NAME_MAX), _not_blank]
#: Letters and digits, with spaces or dashes inside: ANA201, ANA 201, PHY-121.
_CODE = validate.Regexp(
    rf"^[A-Za-z0-9][A-Za-z0-9 -]{{0,{CODE_MAX - 2}}}[A-Za-z0-9]$", error="Use the module code, like ANA201."
)


class ModuleSchema(_Strict):
    code = fields.String(required=True, validate=_CODE)
    name = fields.String(load_default=None, allow_none=True, validate=_NAME)
    #: The final mark the student is aiming for, in %.
    target = Percent(load_default=float(DEFAULT_TARGET))


class AssessmentSchema(_Strict):
    name = fields.String(required=True, validate=_NAME)
    #: Its share of the final mark, in %.
    weight = Percent(required=True, above_zero=True)
    #: The student's mark, in %; null until it's written.
    mark = Percent(load_default=None, allow_none=True)


class NoQuerySchema(_Strict):
    """No query parameters."""


def load(schema: Schema, data) -> dict:
    """Validate a JSON body or query string; one 422 with every field's message."""
    try:
        return schema.load(data if isinstance(data, dict) else {})
    except MarshmallowError as e:
        raise ValidationError("Please check the highlighted fields.", errors=[e.messages]) from None
