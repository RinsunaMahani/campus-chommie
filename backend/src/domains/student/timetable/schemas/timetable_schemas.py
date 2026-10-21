"""What adding or changing a class accepts: a module code, what kind of class, a weekday (0 = Monday), a
start and end time as "HH:MM" between 06:00 and 22:00 in 5-minute steps, and optionally a title and a
venue. An exam: a module code, a date, a start time, and optionally its length, name, paper and venue. Several
of either can be saved at once (after an import), and an import names its layout. Anything else is refused;
nothing asked is about the student."""
from __future__ import annotations

import re
from datetime import time

from marshmallow import RAISE, Schema, ValidationError, fields, validate, validates, validates_schema

from src.core.exceptions import ValidationError as ApiValidationError

from ..constants import ACTIVITY_KINDS, EARLIEST, KINDS, LATEST, MAX_ENTRIES, MAX_EXAMS

_TIME = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


class _Strict(Schema):
    class Meta:
        unknown = RAISE


def _plain_text(value: str) -> None:
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
        raise ValidationError("Use letters, numbers and punctuation only.")
    if not value.strip():
        raise ValidationError("Type something, or leave it out.")


def parse_time(value: str) -> time:
    m = _TIME.match(value)
    if not m:
        raise ValidationError('Use 24-hour time, like "08:30".')
    t = time(int(m.group(1)), int(m.group(2)))
    if t.minute % 5:
        raise ValidationError("Use 5-minute steps, like 08:30 or 08:35.")
    if not (parse_hm(EARLIEST) <= t <= parse_hm(LATEST)):
        raise ValidationError(f"Classes run between {EARLIEST} and {LATEST}.")
    return t


def parse_hm(value: str) -> time:
    h, m = value.split(":")
    return time(int(h), int(m))


class TimeField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        if not isinstance(value, str):
            raise ValidationError('Use 24-hour time, like "08:30".')
        return parse_time(value)


class EntrySchema(_Strict):
    """POST /me/timetable"""

    module = fields.String(required=True, validate=[validate.Length(min=2, max=20), validate.Regexp(r"^[A-Za-z0-9 ]+$")])
    title = fields.String(allow_none=True, validate=validate.Length(max=80))
    kind = fields.String(required=True, validate=validate.OneOf(KINDS))
    weekday = fields.Integer(required=True, strict=True, validate=validate.Range(min=0, max=6))
    starts = TimeField(required=True)
    ends = TimeField(required=True)
    venue = fields.String(allow_none=True, validate=validate.Length(max=80))

    @validates("title")
    def _title(self, value, **_kwargs):
        if value is not None:
            _plain_text(value)

    @validates("venue")
    def _venue(self, value, **_kwargs):
        if value is not None:
            _plain_text(value)

    @validates_schema
    def _order(self, data, **_kwargs):
        if "starts" in data and "ends" in data and data["ends"] <= data["starts"]:
            raise ValidationError({"ends": ["The class must end after it starts."]})


class EntryChangeSchema(EntrySchema):
    """PATCH /me/timetable/<id>: any of the same fields, at least one."""

    class Meta:
        unknown = RAISE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, partial=True, **kwargs)

    @validates_schema
    def _something(self, data, **_kwargs):
        if not data:
            raise ValidationError({"_schema": ["Send at least one change."]})


_MODULE = [validate.Length(min=2, max=20), validate.Regexp(r"^[A-Za-z0-9 ]+$")]


class ExamSchema(_Strict):
    """POST /me/exams"""

    module = fields.String(required=True, validate=_MODULE)
    on = fields.Date(required=True)
    starts = TimeField(required=True)
    minutes = fields.Integer(allow_none=True, strict=True, validate=validate.Range(min=1, max=480))
    title = fields.String(allow_none=True, validate=validate.Length(max=80))
    paper = fields.String(allow_none=True, validate=validate.Length(max=80))
    venue = fields.String(allow_none=True, validate=validate.Length(max=80))

    @validates("title", "paper", "venue")
    def _text(self, value, **_kwargs):
        if value is not None:
            _plain_text(value)


class EntryBatchSchema(_Strict):
    """POST /me/timetable/batch: classes checked after an import; replace=true clears the timetable first."""

    entries = fields.List(fields.Nested(EntrySchema), required=True, validate=validate.Length(min=1, max=MAX_ENTRIES))
    replace = fields.Boolean(load_default=False, truthy={True}, falsy={False})


class ExamBatchSchema(_Strict):
    """POST /me/exams/batch: exams checked after an import; replace=true clears the student's exams first."""

    exams = fields.List(fields.Nested(ExamSchema), required=True, validate=validate.Length(min=1, max=MAX_EXAMS))
    replace = fields.Boolean(load_default=False, truthy={True}, falsy={False})


class ImportFormSchema(_Strict):
    """POST /me/timetable/import's form fields besides the file: which layout the PDF is."""

    layout = fields.String(required=True, validate=validate.OneOf(("classes", "exams")))


class DayTimeField(fields.Field):
    """Any time of day in 5-minute steps: a plan can be early or late ("22:30")."""

    def _deserialize(self, value, attr, data, **kwargs):
        if not isinstance(value, str) or not _TIME.match(value):
            raise ValidationError('Use 24-hour time, like "18:30".')
        t = time(int(value[:2]), int(value[3:]))
        if t.minute % 5:
            raise ValidationError("Use 5-minute steps, like 18:30 or 18:35.")
        return t


class ActivitySchema(_Strict):
    """POST /me/activities: every week on `weekday`, or once `on`: one or the other."""

    title = fields.String(required=True, validate=validate.Length(min=1, max=60))
    kind = fields.String(required=True, validate=validate.OneOf(ACTIVITY_KINDS))
    weekday = fields.Integer(load_default=None, allow_none=True, strict=True, validate=validate.Range(min=0, max=6))
    on = fields.Date(load_default=None, allow_none=True)
    starts = DayTimeField(required=True)
    ends = DayTimeField(required=True)
    place = fields.String(allow_none=True, validate=validate.Length(max=80))

    @validates("title")
    def _title(self, value, **_kwargs):
        _plain_text(value)

    @validates("place")
    def _place(self, value, **_kwargs):
        if value is not None:
            _plain_text(value)

    @validates_schema
    def _shape(self, data, **_kwargs):
        if "weekday" in data or "on" in data:
            if (data.get("weekday") is None) == (data.get("on") is None):
                raise ValidationError({"weekday": ["Choose a day of the week, or one date: not both."]})
        if "starts" in data and "ends" in data and data["ends"] <= data["starts"]:
            raise ValidationError({"ends": ["It must end after it starts."]})


class ActivityChangeSchema(ActivitySchema):
    """PATCH /me/activities/<id>: any of the same fields, at least one. Moving between weekly and once sends both
    weekday and on (one of them null)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, partial=True, **kwargs)

    @validates_schema
    def _something(self, data, **_kwargs):
        if not data:
            raise ValidationError({"_schema": ["Send at least one change."]})


class FindTimeSchema(_Strict):
    """POST /me/activities/find-time: how long, from which day, over how many days."""

    minutes = fields.Integer(required=True, strict=True, validate=[validate.Range(min=15, max=480)])
    start = fields.Date(load_default=None, allow_none=True)
    days = fields.Integer(load_default=7, strict=True, validate=validate.Range(min=1, max=14))

    @validates("minutes")
    def _steps(self, value, **_kwargs):
        if value % 5:
            raise ValidationError("Use 5-minute steps.")


class NothingSchema(_Strict):
    """No query parameters: anything sent is refused."""


def load(schema: Schema, data) -> dict:
    """Validate a JSON body or query string; one 422 with every field's message."""
    if not isinstance(data, dict):
        raise ApiValidationError("Please check the highlighted fields.", errors=[{"_schema": ["Send a JSON object."]}])
    try:
        return schema.load(data)
    except ValidationError as e:
        raise ApiValidationError("Please check the highlighted fields.", errors=[e.messages]) from None
