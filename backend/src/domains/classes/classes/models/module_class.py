"""
ModuleClass -- one module's class on one campus in one academic year. The
university and campus are data-pack ids. No personal data: who created it
isn't kept (the first rep is a member like any other).
"""
from __future__ import annotations

from src.core.base_model import BaseModel
from src.extensions import db

from ..constants import INVITE_LENGTH, MODULE_CODE_MAX, MODULE_NAME_MAX


class ModuleClass(BaseModel):
    __tablename__ = "classes"
    __table_args__ = (
        db.UniqueConstraint("invite_code", name="uq_classes_invite_code"),
        db.CheckConstraint("year BETWEEN 2000 AND 2100", name="ck_classes_year"),
        {"schema": "classes"},
    )

    university = db.Column(db.String(40), nullable=False)
    campus = db.Column(db.String(40), nullable=True)  # None: the pack lists no campuses
    module_code = db.Column(db.String(MODULE_CODE_MAX), nullable=False)
    module_name = db.Column(db.String(MODULE_NAME_MAX), nullable=True)
    year = db.Column(db.SmallInteger, nullable=False)
    invite_code = db.Column(db.String(INVITE_LENGTH), nullable=False)
