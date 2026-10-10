"""
My marks: the student's modules and assessments, and what the engine makes
of them (where they stand, the average needed for their target, a projected
final mark with a likely range). Services call the engine; routes never do.
Every function touches only the signed-in student's rows: another student's
is the same 404 as one that doesn't exist.

A module's mark is out of 100%. When the weights entered add up to less, the
rest counts as still to come, so "what you need" never forgets it.
"""
from __future__ import annotations

import uuid

from sqlalchemy.exc import IntegrityError

from campus_engine.forecast import project_module_mark
from campus_engine.standing import Assessment as Mark
from campus_engine.standing import standing
from campus_engine.text import num
from src.core.exceptions import NotFoundError, ValidationError
from src.extensions import db

from ..constants import MAX_ASSESSMENTS, MAX_MODULES
from ..models import Assessment, Module
from ..repositories import academics_repository as repo

NO_ASSESSMENTS = "Add this module's assessments and their weights to see where you stand."
NOT_ENTERED = "Not entered yet"


def _field_error(field: str, message: str) -> ValidationError:
    return ValidationError("Please check the highlighted fields.", errors=[{field: [message]}])


def _clean_code(code: str) -> str:
    return " ".join(code.split()).upper()


def _clean_name(name: str | None) -> str | None:
    return " ".join(name.split()) if name is not None else None


def _my_module(user, module_id: uuid.UUID) -> Module:
    row = repo.module(user.id, module_id)
    if row is None:
        raise NotFoundError("We couldn't find that module.", code="MODULE_NOT_FOUND")
    return row


def _my_assessment(user, module: Module, assessment_id: uuid.UUID) -> Assessment:
    row = repo.assessment(user.id, module.id, assessment_id)
    if row is None:
        raise NotFoundError("We couldn't find that assessment.", code="ASSESSMENT_NOT_FOUND")
    return row


def _commit_module(code: str) -> None:
    """Commit; two requests adding the same code at once get the same answer as one after the other."""
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise _field_error("code", f"You already have {code}.") from None


# ------------------------------------------------------------------ modules


def list_modules(user) -> dict:
    return {"modules": [_module(m) for m in repo.modules_for(user.id)]}


def add_module(user, body: dict) -> dict:
    if repo.count_modules(user.id) >= MAX_MODULES:
        raise _field_error("modules", f"You can keep up to {MAX_MODULES} modules.")
    code = _clean_code(body["code"])
    if repo.module_by_code(user.id, code) is not None:
        raise _field_error("code", f"You already have {code}.")
    row = Module(user_id=user.id, code=code, name=_clean_name(body["name"]), target=body["target"])
    repo.add(row)
    _commit_module(code)
    return {"module": _module(row)}


def replace_module(user, module_id: uuid.UUID, body: dict) -> dict:
    row = _my_module(user, module_id)
    code = _clean_code(body["code"])
    clash = repo.module_by_code(user.id, code)
    if clash is not None and clash.id != row.id:
        raise _field_error("code", f"You already have {code}.")
    row.code, row.name, row.target = code, _clean_name(body["name"]), body["target"]
    _commit_module(code)
    return {"module": _module(row)}


def delete_module(user, module_id: uuid.UUID) -> dict:
    """The module goes, with its assessments."""
    repo.delete(_my_module(user, module_id))
    db.session.commit()
    return {}


# -------------------------------------------------------------- assessments


def _check_weights(module: Module, weight: float, replacing: Assessment | None = None) -> None:
    others = sum(a.weight for a in module.assessments if replacing is None or a.id != replacing.id)
    if others + weight > 100 + 1e-9:
        raise _field_error("weight", f"The weights would add up to {num(others + weight)}%: they can't pass 100%.")


def add_assessment(user, module_id: uuid.UUID, body: dict) -> dict:
    module = _my_module(user, module_id)
    if len(module.assessments) >= MAX_ASSESSMENTS:
        raise _field_error("assessments", f"A module can have up to {MAX_ASSESSMENTS} assessments.")
    _check_weights(module, body["weight"])
    repo.add(Assessment(user_id=user.id, module_id=module.id, name=_clean_name(body["name"]),
                        weight=body["weight"], mark=body["mark"]))
    db.session.commit()
    db.session.refresh(module)
    return {"module": _module(module)}


def replace_assessment(user, module_id: uuid.UUID, assessment_id: uuid.UUID, body: dict) -> dict:
    module = _my_module(user, module_id)
    row = _my_assessment(user, module, assessment_id)
    _check_weights(module, body["weight"], replacing=row)
    row.name, row.weight, row.mark = _clean_name(body["name"]), body["weight"], body["mark"]
    db.session.commit()
    db.session.refresh(module)
    return {"module": _module(module)}


def delete_assessment(user, module_id: uuid.UUID, assessment_id: uuid.UUID) -> dict:
    module = _my_module(user, module_id)
    repo.delete(_my_assessment(user, module, assessment_id))
    db.session.commit()
    db.session.refresh(module)
    return {"module": _module(module)}


def erase_all_for(user) -> None:
    """Every module and assessment of this student, deleted for real: the demo's daily reset (and DELETE /me's later)."""
    repo.erase_all(user.id)
    db.session.commit()


# ------------------------------------------------------------- what's sent


def _round(x: float | None) -> float | None:
    return round(x, 1) if x is not None else None


def _module(m: Module) -> dict:
    entered = sum(a.weight for a in m.assessments)
    out = {
        "id": str(m.id),
        "code": m.code,
        "name": m.name,
        "target": m.target,
        "assessments": [{"id": str(a.id), "name": a.name, "weight": a.weight, "mark": a.mark} for a in m.assessments],
        "total_weight": _round(entered),
        "standing": None,
        "projection": None,
        "lines": [],
    }
    if not m.assessments:
        out["lines"].append(NO_ASSESSMENTS)
        return out

    marks = [Mark(a.name, a.weight, a.mark) for a in m.assessments]
    if entered < 100 - 1e-9:
        marks.append(Mark(NOT_ENTERED, 100 - entered, None))
        out["lines"].append(
            f"The weights you've entered add up to {num(entered)}%. "
            f"The other {num(100 - entered)}% counts as still to come until you add it."
        )
    s = standing(marks, m.target)
    out["standing"] = {
        "status": s.status,
        "current": _round(s.current),
        "needed": _round(s.needed),
        "completed_weight": _round(s.completed_weight),
        "remaining_weight": _round(s.remaining_weight),
        "message": s.message,
    }
    out["lines"].append(s.message)
    p = project_module_mark(marks, m.target)
    if p is not None:
        out["projection"] = {
            "projected": _round(p.projected),
            "low": _round(p.low),
            "high": _round(p.high),
            "based_on": p.based_on,
            "below_target": p.below_target,
            "message": p.explanation,
        }
        out["lines"].append(p.explanation)
    return out
