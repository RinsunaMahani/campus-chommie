"""
Every alert the app can show, in one place. Each template fixes its icon,
a FIXED title and the body's wording. Only the body takes params, and
only ones the server filled: names and numbers it already has. Never an
IP, a place, an email, a phone number, a device name, or anything typed
into a free-text field.

Security alerts are always written. A feature whose alerts a student may
switch off (class updates, reminders) brings its topic and the switch
with it.

Money: a param ending in _cents is shown as rand under the name without
the suffix ({total} from total_cents), so publishers send numbers, not
text.
"""
from __future__ import annotations

import string
from typing import Any, NamedTuple

#: What tapping an alert opens (the app maps each to a screen): "class" opens that class's events,
#: "funding" that funder (link_id is its id in the funding pack), "review" the week in review (link_id is the
#: week's last day).
LINK_TYPES = ("security", "class", "funding", "review")

#: Alerts a student may switch off, by topic, with what the switch covers. Security alerts have no
#: topic: they're always on.
TOPICS = {
    "class_updates": "New, moved and cancelled tests and deadlines from your class reps",
    "funding_reminders": "Funding you saved: when it opens, and before it closes",
    "week_review": "Your week in review, on your check-in day",
}


class Template(NamedTuple):
    icon: str
    title: str
    body: str
    topic: str | None = None  # None: always on


TEMPLATES: dict[str, Template] = {
    # Your account (always on)
    "account.new_phone": Template("smartphone", "New phone signed in", "Your account was opened on a new phone. Not you? Change your password."),
    "account.password_changed": Template("lock", "Password changed", "Your password was changed. Not you? Reset it now."),
    "account.phones_signed_out": Template("log-out", "Other phones signed out", "Every other phone was signed out of your account."),
    # Never says why: only that sign-in is paused, and what to do.
    "account.locked": Template("alert-triangle", "Account locked", "Sign-in is paused for {minutes} minutes to keep your account safe. If that wasn't you, change your password."),
    # Class updates, from a rep's confirmation. Only the module, the kind and the dates: never who, and never
    # what someone typed (a title or a venue). {when} and {was} read "on Tue 20 Oct 2026 at 08:00" or "due ...".
    "class.event_new": Template("calendar", "New date from your class", "{module}: a new {kind} {when}.", "class_updates"),
    "class.event_moved": Template("calendar", "A class date moved", "{module}: the {kind} {was} is now {when}.", "class_updates"),
    "class.event_changed": Template("calendar", "A class date changed", "{module}: the {kind} {when} has a change. Check where and when.", "class_updates"),
    "class.event_cancelled": Template("x-circle", "A class date was cancelled", "{module}: the {kind} {when} is cancelled.", "class_updates"),
    # Funding the student saved: the funder's short name from the funding pack, the year it funds and the
    # closing date. Never anything about the student. {when} reads "in 7 days, on Sat 31 Oct 2026 at 23:59".
    "funding.open": Template(
        "award", "Funding you saved is open", "{funder}: applications for {intake} funding are open now.", "funding_reminders"
    ),
    "funding.closing": Template(
        "clock", "Funding you saved closes soon", "{funder}: applications for {intake} funding close {when}.", "funding_reminders"
    ),
    # The week in review, on the student's check-in day: no params, so nothing about the week is in the alert.
    "review.ready": Template(
        "bar-chart-2", "Your week in review", "See what you got done, what's coming up and how your money went this week.", "week_review"
    ),
}


def rand(cents: int) -> str:
    """R4,500 or R12.50."""
    whole, part = divmod(int(cents), 100)
    text = f"R{whole:,}"
    return f"{text}.{part:02d}" if part else text


def placeholders(template: Template) -> set[str]:
    return {name for _, name, _, _ in string.Formatter().parse(template.body) if name}


def display_params(params: dict[str, Any]) -> dict[str, Any]:
    """Params as the body shows them: *_cents as rand without the suffix."""
    shown: dict[str, Any] = {}
    for key, value in (params or {}).items():
        if key.endswith("_cents") and isinstance(value, int) and not isinstance(value, bool):
            shown[key[: -len("_cents")]] = rand(value)
        else:
            shown[key] = value
    return shown


def missing(kind: str, params: dict[str, Any]) -> set[str]:
    """Placeholders the params don't fill (a publisher's bug)."""
    return placeholders(TEMPLATES[kind]) - set(display_params(params))


class _Blank(dict):
    def __missing__(self, key: str) -> str:
        return ""


def render(kind: str, params: dict[str, Any]) -> tuple[str, str]:
    """(title, body). Never raises: a param that went missing renders empty."""
    t = TEMPLATES[kind]
    return t.title, t.body.format_map(_Blank(display_params(params)))
