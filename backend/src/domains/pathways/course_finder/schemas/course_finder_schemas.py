"""
What the course finder accepts. Strict: unknown fields, unknown or repeated
subjects, more than nine subjects, and marks outside 0 to 100 (NaN and
infinity included) are refused with one 422 that never echoes a mark back.
"""
from __future__ import annotations

from marshmallow import RAISE, Schema, fields, validate, validates_schema
from marshmallow import ValidationError as MarshmallowError

from src.core.exceptions import ValidationError

from ..constants import MAX_SUBJECTS, SUBJECT_KEYS


class _Strict(Schema):
    class Meta:
        unknown = RAISE


class MarkSchema(_Strict):
    language_level = fields.String(validate=validate.OneOf(["home", "first_additional"]))
    subject = fields.String(required=True, validate=validate.OneOf(sorted(SUBJECT_KEYS), error="We don't know that subject."))
    percent = fields.Float(
        required=True, allow_nan=False, validate=validate.Range(min=0, max=100, error="A mark is from 0 to 100.")
    )

    @validates_schema
    def _language_only_for_english(self, data, **kwargs):
        if "language_level" in data and data.get("subject") != "english":
            raise MarshmallowError({"language_level": ["Language level applies to English only."]})


class PointsSchema(_Strict):
    """Marks only: the learner's points at every university."""

    marks = fields.List(
        fields.Nested(MarkSchema),
        required=True,
        validate=validate.Length(min=1, max=MAX_SUBJECTS, error=f"Enter 1 to {MAX_SUBJECTS} subjects."),
    )

    @validates_schema
    def _each_subject_once(self, data, **kwargs):
        subjects = [mark["subject"] for mark in data.get("marks", [])]
        repeated = sorted({s for s in subjects if subjects.count(s) > 1})
        if repeated:
            raise MarshmallowError({"marks": [f"Enter each subject once: {', '.join(repeated)} is repeated."]})


class AssessSchema(PointsSchema):
    university = fields.String(required=True, validate=validate.Length(min=1, max=40))


class PlanSchema(AssessSchema):
    goal = fields.String(required=True, validate=validate.Length(min=1, max=60))


def load(schema: Schema, data) -> dict:
    """Validate a JSON body; one 422 with every field's message."""
    try:
        return schema.load(data if isinstance(data, dict) else {})
    except MarshmallowError as e:
        raise ValidationError("Please check the highlighted fields.", errors=[e.messages]) from None
