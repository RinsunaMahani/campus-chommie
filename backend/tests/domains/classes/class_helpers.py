"""
Shared by the classes tests: signed-in students (the student tests' own
helper, reused rather than copied), a class made by a rep, classmates
joining it, and verified events made the way a rep makes them.
"""
from __future__ import annotations

import sys
from pathlib import Path

# pytest puts each test file's own folder on the path: add the student tests' folder for its helpers.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "student"))

from student_helpers import Student, personas, set_up_persona, student  # noqa: E402,F401

API = "/api/v1"
CLASSES = f"{API}/classes"
UP_CLASS = {"university": "up", "campus": "hatfield", "module_code": "ANA201", "module_name": "Anatomy", "year": 2026}


def make_class(client, rep: Student, **body) -> dict:
    r = client.post(CLASSES, json=UP_CLASS | body, headers=rep.headers)
    assert r.status_code == 201, r.get_json()
    return r.get_json()["data"]["class"]


def join(client, who: Student, code: str) -> dict:
    r = client.post(f"{CLASSES}/join", json={"code": code}, headers=who.headers)
    assert r.status_code == 200, r.get_json()
    return r.get_json()["data"]


def announce(client, who: Student, class_id: str, text: str, **body) -> dict:
    r = client.post(f"{CLASSES}/{class_id}/announcements", json={"text": text} | body, headers=who.headers)
    assert r.status_code == 201, r.get_json()
    return r.get_json()["data"]["candidate"]


def confirm(client, rep: Student, candidate: dict, **edits) -> dict:
    """Confirm what the form starts with, with the rep's edits."""
    body = candidate["proposed"] | edits
    if body["change"] is None:
        body.pop("event_id")
    r = client.post(f"{API}/candidates/{candidate['id']}/confirm", json=body, headers=rep.headers)
    assert r.status_code == 200, r.get_json()
    return r.get_json()["data"]


def verified_event(client, rep: Student, class_id: str, text: str, **edits) -> dict:
    return confirm(client, rep, announce(client, rep, class_id, text), **edits)["event"]
