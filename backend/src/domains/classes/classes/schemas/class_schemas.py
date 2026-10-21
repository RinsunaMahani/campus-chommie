"""
What the classes routes accept. Strict: unknown fields are refused. The
university and campus are checked against the data packs by the service,
and the year against today's.
"""
from __future__ import annotations

from marshmallow import RAISE, Schema, fields, validate
from marshmallow import ValidationError as MarshmallowError

from src.core.exceptions import ValidationError

from ..constants import MODULE_CODE_MAX, MODULE_NAME_MAX


class _Strict(Schema):
    class Meta:
        unknown = RAISE


def _not_blank(value: str) -> None:
    if not value.strip():
        raise MarshmallowError("This can't be blank.")


#: Letters and digits, with spaces or dashes inside: ANA201, ANA 201, PHY-121.
MODULE_CODE = validate.Regexp(
    rf"^[A-Za-z0-9][A-Za-z0-9 -]{{0,{MODULE_CODE_MAX - 2}}}[A-Za-z0-9]$", error="Use the module code, like ANA201."
)


class ClassSchema(_Strict):
    university = fields.String(required=True, validate=validate.Length(min=1, max=40))
    campus = fields.String(load_default=None, allow_none=True, validate=validate.Length(min=1, max=40))
    module_code = fields.String(required=True, validate=MODULE_CODE)
    module_name = fields.String(
        load_default=None, allow_none=True, validate=[validate.Length(min=1, max=MODULE_NAME_MAX), _not_blank]
    )
    year = fields.Integer(required=True, strict=True)


class JoinSchema(_Strict):
    #: An invite code or a rep code; spaces and dashes are ignored.
    code = fields.String(required=True, validate=validate.Length(min=1, max=40))


class NoBodySchema(_Strict):
    """Nothing in the body (or no body at all)."""


class NoQuerySchema(_Strict):
    """No query parameters."""


def load(schema: Schema, data) -> dict:
    """Validate a JSON body or query string; one 422 with every field's message."""
    try:
        return schema.load(data if isinstance(data, dict) else {})
    except MarshmallowError as e:
        raise ValidationError("Please check the highlighted fields.", errors=[e.messages]) from None
