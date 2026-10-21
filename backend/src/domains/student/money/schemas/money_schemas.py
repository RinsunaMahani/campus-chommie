"""
What the money routes accept. Strict: unknown fields are refused, and an
amount is a whole number of cents, built as shared/finance's Money. A float
(even 1250.0), text, true or false, NaN and infinity are all refused, so a
rounding error can never reach a balance. Dates are YYYY-MM-DD; how far back
or ahead they may be is checked against today by the service.
"""
from __future__ import annotations

from marshmallow import RAISE, Schema, fields, validate, validates, validates_schema
from marshmallow import ValidationError as MarshmallowError

from src.core.exceptions import ValidationError
from src.shared.finance import FinanceError, Money, format_amount, validate_non_negative, validate_positive

from ..constants import GOAL_LABEL_MAX, LABEL_MAX, MAX_CENTS, RELIABILITY


class _Strict(Schema):
    class Meta:
        unknown = RAISE


class Cents(fields.Field):
    """A whole number of cents: never a float, text or a boolean."""

    default_error_messages = {"invalid": "Enter a whole number of cents."}

    def __init__(self, *, positive: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.positive = positive

    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, bool) or not isinstance(value, int):
            raise self.make_error("invalid")
        try:
            money = Money(value)
        except FinanceError:
            raise self.make_error("invalid") from None
        check = validate_positive(money) if self.positive else validate_non_negative(money)
        if not check.is_valid:
            raise MarshmallowError(check.message)
        if value > MAX_CENTS:
            raise MarshmallowError(f"That's more than {format_amount(Money(MAX_CENTS))}: please check the amount.")
        return value


class StrictBoolean(fields.Boolean):
    """true or false only: not 1, "true" or "yes" (1 == True in Python, so a plain set would let it through)."""

    def _deserialize(self, value, attr, data, **kwargs):
        if not isinstance(value, bool):
            raise self.make_error("invalid", input=value)
        return value


class SettingsSchema(_Strict):
    #: What the student had on `balance_on`.
    balance_cents = Cents(required=True)
    balance_on = fields.Date(required=True)
    essentials_per_day_cents = Cents(required=True)
    life_fund_reserve_cents = Cents(load_default=0)


class SourceSchema(_Strict):
    """Monthly on `day_of_month`, or once on `expected_on`: one or the other."""

    label = fields.String(required=True, validate=validate.Length(min=1, max=LABEL_MAX))
    amount_cents = Cents(required=True, positive=True)
    day_of_month = fields.Integer(load_default=None, allow_none=True, strict=True, validate=validate.Range(min=1, max=31))
    expected_on = fields.Date(load_default=None, allow_none=True)
    reliability = fields.String(load_default="not_sure", validate=validate.OneOf(RELIABILITY))

    @validates_schema
    def _one_schedule(self, data, **kwargs):
        if (data.get("day_of_month") is None) == (data.get("expected_on") is None):
            raise MarshmallowError({"day_of_month": ["Choose a day of the month, or one date: not both."]})


class PaymentUpdateSchema(_Strict):
    """Move one payment, change its amount, or tap "received"."""

    expected_on = fields.Date()
    amount_cents = Cents(positive=True)
    received = StrictBoolean()

    @validates_schema
    def _something(self, data, **kwargs):
        if not data:
            raise MarshmallowError({"_schema": ["Send what changed: expected_on, amount_cents or received."]})


class SpendingSchema(_Strict):
    amount_cents = Cents(required=True)


class SpendingQuerySchema(_Strict):
    days = fields.Integer(load_default=30, validate=validate.Range(min=1, max=366, error="1 to 366 days."))


class SummaryQuerySchema(_Strict):
    #: Plan for the next payment arriving two weeks late.
    late = fields.Boolean(load_default=False)


class AffordSchema(_Strict):
    """POST /money/afford: the price of one thing. Nothing is stored."""

    amount_cents = Cents(required=True, positive=True)


class GoalSchema(_Strict):
    """POST /money/goals: what it's for, how much, by when; how much is already aside; whether the date came from
    the university's fee dates."""

    label = fields.String(required=True, validate=validate.Length(min=1, max=GOAL_LABEL_MAX))
    amount_cents = Cents(required=True, positive=True)
    saved_cents = Cents(load_default=0)
    due_on = fields.Date(required=True)
    from_university = StrictBoolean(load_default=False)

    @validates("label")
    def _plain(self, value, **kwargs):
        if not value.strip() or any(ord(c) < 32 or ord(c) == 127 for c in value):
            raise MarshmallowError("Use letters, numbers and punctuation only.")

    @validates_schema
    def _not_more_than(self, data, **kwargs):
        if "saved_cents" in data and "amount_cents" in data and data["saved_cents"] > data["amount_cents"]:
            raise MarshmallowError({"saved_cents": ["That's more than the goal itself."]})


class GoalChangeSchema(GoalSchema):
    """PATCH /money/goals/<id>: any of the same fields, at least one."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, partial=True, **kwargs)

    @validates_schema
    def _something(self, data, **kwargs):
        if not data:
            raise MarshmallowError({"_schema": ["Send what changed."]})


class NoQuerySchema(_Strict):
    """No query parameters."""


def load(schema: Schema, data) -> dict:
    """Validate a JSON body or query string; one 422 with every field's message."""
    try:
        return schema.load(data if isinstance(data, dict) else {})
    except MarshmallowError as e:
        raise ValidationError("Please check the highlighted fields.", errors=[e.messages]) from None
