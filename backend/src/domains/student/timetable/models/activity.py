"""
Activity -- something in a student's own week that isn't a class: groceries, the gym, a shift, seeing friends,
church or anything else they type. Either every week on a weekday, or once on a date; from a start to an end time;
optionally where. Only what the student typed. The kinds are broad on purpose (personal, social, errands,
exercise, work, other): we never ask about religion or anything sensitive, and only the student sees the name.
"""
from __future__ import annotations

from sqlalchemy.dialects.postgresql import UUID

from src.core.base_model import BaseModel
from src.extensions import db

from ..constants import ACTIVITY_KINDS


class Activity(BaseModel):
    __tablename__ = "activities"
    __table_args__ = (
        db.CheckConstraint("(weekday IS NULL) <> (on_date IS NULL)", name="ck_activities_one_schedule"),
        db.CheckConstraint("weekday IS NULL OR weekday BETWEEN 0 AND 6", name="ck_activities_weekday"),
        db.CheckConstraint("ends_at > starts_at", name="ck_activities_order"),
        db.CheckConstraint("kind IN (" + ", ".join(f"'{k}'" for k in ACTIVITY_KINDS) + ")", name="ck_activities_kind"),
        db.Index("ix_activities_user", "user_id", "weekday", "on_date"),
        {"schema": "student"},
    )

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("identity.users.id", ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(60), nullable=False)
    kind = db.Column(db.String(12), nullable=False)
    weekday = db.Column(db.SmallInteger, nullable=True)  # every week: 0 = Monday
    on_date = db.Column(db.Date, nullable=True)  # once
    starts_at = db.Column(db.Time, nullable=False)
    ends_at = db.Column(db.Time, nullable=False)
    place = db.Column(db.String(80), nullable=True)
