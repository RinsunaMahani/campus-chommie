"""
What the notification routes accept. Unknown fields are rejected, a page
is 1..50, and "read all" takes no fields at all.
"""
from __future__ import annotations

from marshmallow import RAISE, Schema, fields, validate, validates_schema
from marshmallow import ValidationError as MarshmallowError

from src.core.exceptions import ValidationError

from ..constants import PAGE_DEFAULT, PAGE_MAX


class _Strict(Schema):
    class Meta:
        unknown = RAISE


class ListQuerySchema(_Strict):
    #: The last alert of the previous page.
    before = fields.UUID(load_default=None)
    limit = fields.Integer(load_default=PAGE_DEFAULT, validate=validate.Range(min=1, max=PAGE_MAX, error=f"1 to {PAGE_MAX} at a time."))


class ReadAllSchema(_Strict):
    """No fields: every unread alert of the signed-in user."""


class StrictBoolean(fields.Boolean):
    """true or false only: not 1, "true" or "yes"."""

    def _deserialize(self, value, attr, data, **kwargs):
        if not isinstance(value, bool):
            raise self.make_error("invalid", input=value)
        return value


class SwitchesSchema(_Strict):
    """The topics to change, each true (on) or false (off). Security alerts have no switch."""

    class_updates = StrictBoolean()
    funding_reminders = StrictBoolean()

    @validates_schema
    def _something(self, data, **kwargs):
        if not data:
            raise MarshmallowError({"_schema": ["Send at least one switch, for example {\"class_updates\": false}."]})


class NoQuerySchema(_Strict):
    """No query parameters."""


def load(schema: Schema, data) -> dict:
    """Validate a JSON body or query string; one 422 with every field's message."""
    try:
        return schema.load(data if isinstance(data, dict) else {})
    except MarshmallowError as e:
        raise ValidationError("Please check the highlighted fields.", errors=[e.messages]) from None
