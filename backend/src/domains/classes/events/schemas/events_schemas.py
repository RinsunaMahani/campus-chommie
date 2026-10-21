"""
What the class events and week routes accept. Strict: unknown fields are
refused. Dates are YYYY-MM-DD and times HH:MM (24-hour); how far back or
ahead a date may be is checked against today by the service.
"""
from __future__ import annotations

import math
import re
from datetime import time

from marshmallow import RAISE, Schema, fields, validate, validates_schema
from marshmallow import ValidationError as MarshmallowError

from src.core.exceptions import ValidationError

from ..constants import CHANGES, DEFAULT_WEEKS, FLAG_REASONS, KINDS, MAX_WEEKS, TEXT_MAX, TITLE_MAX, VENUE_MAX

CLOCK = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


class _Strict(Schema):
    class Meta:
        unknown = RAISE


def _not_blank(value: str) -> None:
    if not value.strip():
        raise MarshmallowError("This can't be blank.")


class Clock(fields.Field):
    """A time of day as HH:MM, 24-hour."""

    default_error_messages = {"invalid": "Enter a time as HH:MM, like 14:00."}

    def _deserialize(self, value, attr, data, **kwargs):
        m = CLOCK.match(value) if isinstance(value, str) else None
        if m is None:
            raise self.make_error("invalid")
        return time(int(m.group(1)), int(m.group(2)))


class Weighting(fields.Field):
    """A share of the module mark: a number above 0, up to 100."""

    default_error_messages = {"invalid": "Enter a number above 0, up to 100."}

    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise self.make_error("invalid")
        if isinstance(value, float) and not math.isfinite(value):
            raise self.make_error("invalid")
        if not 0 < value <= 100:  # compared before float(): a 400-digit integer is refused, not overflowed
            raise self.make_error("invalid")
        return float(value)


class AnnouncementSchema(_Strict):
    text = fields.String(required=True, validate=[validate.Length(min=1, max=TEXT_MAX), _not_blank])
    #: When the message was sent: "Friday" means the Friday after this. Today if left out.
    sent_on = fields.Date(load_default=None, allow_none=True)


class ConfirmSchema(_Strict):
    """The event as the rep confirms it. A new event needs a type and a date; a change names the
    event it changes, and a "moved" one gives the new date, time and venue (all three: what's sent is
    what the event becomes)."""

    change = fields.String(load_default=None, allow_none=True, validate=validate.OneOf(CHANGES))
    event_id = fields.UUID(load_default=None, allow_none=True)
    kind = fields.String(load_default=None, allow_none=True, validate=validate.OneOf(KINDS))
    title = fields.String(load_default=None, allow_none=True, validate=[validate.Length(min=1, max=TITLE_MAX), _not_blank])
    on = fields.Date(load_default=None, allow_none=True)
    at = Clock(load_default=None, allow_none=True)
    venue = fields.String(load_default=None, allow_none=True, validate=[validate.Length(min=1, max=VENUE_MAX), _not_blank])
    weighting = Weighting(load_default=None, allow_none=True)

    @validates_schema
    def _complete(self, data, **kwargs):
        errors = {}
        if data.get("change") is None:
            if data.get("kind") is None:
                errors["kind"] = ["Choose the type: test, quiz, practical, assignment or exam."]
            if data.get("on") is None:
                errors["on"] = ["Enter the date."]
            if data.get("event_id") is not None:
                errors["event_id"] = ["A new event doesn't change another one: leave this out."]
        else:
            if data.get("event_id") is None:
                errors["event_id"] = ["Choose the event this message changes."]
            if data["change"] == "moved" and data.get("on") is None:
                errors["on"] = ["Enter the new date (the same one, if only the time or venue changed)."]
        if errors:
            raise MarshmallowError(errors)


class FlagSchema(_Strict):
    reason = fields.String(required=True, validate=validate.OneOf(FLAG_REASONS))


class EventsQuerySchema(_Strict):
    start = fields.Date(data_key="from", load_default=None)
    end = fields.Date(data_key="to", load_default=None)


class WeekQuerySchema(_Strict):
    weeks = fields.Integer(
        load_default=DEFAULT_WEEKS, validate=validate.Range(min=1, max=MAX_WEEKS, error=f"1 to {MAX_WEEKS} weeks.")
    )
    start = fields.Date(data_key="from", load_default=None)


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
