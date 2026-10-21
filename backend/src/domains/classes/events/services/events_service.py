"""
Announcements in, verified events out. A member pastes an announcement;
the engine reads it into a candidate (a confidence per field, and what to
check); a rep edits and confirms it, and only then is it a verified event. A
student's candidate waits for a rep: only a rep can confirm. A "moved" or
"cancelled" message changes the existing event, records each changed field
as an EventChange and bumps its version.

Classes are reached through the classes service: a candidate or event in a
class the student isn't in is the same 404 as one that doesn't exist, and a
student sees only their own candidates (a rep sees the class's).
"""
from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.exc import IntegrityError

from campus_engine.extraction import Candidate, change_line, extract, find_existing, reading
from campus_engine.text import long_day
from campus_engine.workload import AcademicEvent
from src.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from src.domains.classes.classes.services import class_service as classes
from src.extensions import db

from ..constants import (
    EVENT_DAYS_AHEAD,
    EVENT_DAYS_BACK,
    EVENTS_AHEAD_DAYS,
    EVENTS_BACK_DAYS,
    MATCH_DAYS_BACK,
    MAX_PENDING,
    MODULE_MAX,
    RANGE_MAX_DAYS,
    SENT_DAYS_BACK,
    TIMEZONE,
    TITLE_MAX,
    VENUE_MAX,
)
from ..models import Announcement, ClassEvent, EventCandidate, EventChange, EventFlag
from ..repositories import events_repository as repo

WAITING_FOR_REP = "A class rep checks this before it goes live: until then it's unverified."


def _today() -> date:
    """Today in South Africa: every student's day."""
    return datetime.now(ZoneInfo(TIMEZONE)).date()


def _now() -> datetime:
    return datetime.now(UTC)


def _field_error(field: str, message: str) -> ValidationError:
    return ValidationError("Please check the highlighted fields.", errors=[{field: [message]}])


def _cut(text: str | None, n: int) -> str | None:
    return text[:n] if text else text


def _clean(text: str | None) -> str | None:
    return " ".join(text.split()) if text else None


def _clock(t: time | None) -> str | None:
    return f"{t:%H:%M}" if t else None


def _iso(d: date | None) -> str | None:
    return d.isoformat() if d else None


def _when(on: date, at: time | None) -> str:
    return long_day(on) + (f" at {at:%H:%M}" if at else "")


def academic(row: ClassEvent) -> AcademicEvent:
    """A verified event as the engine sees it. With no time given, it counts from the start of its day."""
    return AcademicEvent(
        title=row.title,
        kind=row.kind,
        starts=datetime.combine(row.on_date, row.at_time or time(0, 0)),
        module=row.module,
        weighting=row.weighting,
        venue=row.venue,
        verified=True,
        cancelled=row.cancelled,
    )


# --------------------------------------------- announcements and candidates


def announce(user, class_id: uuid.UUID, body: dict) -> dict:
    """Read an announcement into a candidate for the class's reps."""
    m = classes.membership(user, class_id)
    today = _today()
    sent = body["sent_on"] or today
    if sent > today:
        raise _field_error("sent_on", "That day is still to come: use the day the message was sent.")
    if sent < today - timedelta(days=SENT_DAYS_BACK):
        raise _field_error("sent_on", f"Use a message from the last {SENT_DAYS_BACK} days.")
    if not m.is_rep and repo.count_pending(class_id, user.id) >= MAX_PENDING:
        raise _field_error("text", f"You have {MAX_PENDING} messages waiting for a rep in this class: give them a moment.")

    c = extract(body["text"], sent, [m.module_code])
    if c.module is None:  # the class says which module it is
        c.module, c.confidence["module"] = m.module_code, 0.95
    target = None
    if c.change:
        live = repo.live_events_since(class_id, sent - timedelta(days=MATCH_DAYS_BACK))
        pairs = [(row, academic(row)) for row in live]
        hit = find_existing(c, [ev for _, ev in pairs])
        target = next((row for row, ev in pairs if ev is hit), None)

    announcement = Announcement(
        class_id=class_id, submitted_by=user.id, raw_text=body["text"], sent_on=sent, status="pending"
    )
    repo.add(announcement)
    db.session.flush()
    candidate = EventCandidate(
        announcement_id=announcement.id,
        class_id=class_id,
        from_rep=m.is_rep,
        kind=c.kind,
        title=_cut(c.title, TITLE_MAX),
        module=_cut(c.module, MODULE_MAX),
        on_date=c.on,
        at_time=c.at,
        venue=_cut(c.venue, VENUE_MAX),
        weighting=c.weighting,
        change=c.change,
        event_id=target.id if target else None,
        confidence=c.confidence,
        notes=c.notes,
    )
    repo.add(candidate)
    db.session.commit()
    return {"candidate": _candidate(candidate, m, user)}


def candidates(user, class_id: uuid.UUID) -> dict:
    """What's waiting for a rep: the whole class's for a rep, a student's own otherwise."""
    m = classes.membership(user, class_id)
    rows = repo.pending_candidates(class_id, None if m.is_rep else user.id)
    return {"candidates": [_candidate(row, m, user) for row in rows]}


def _find_candidate(user, candidate_id: uuid.UUID) -> tuple[EventCandidate, classes.Membership]:
    mine = {m.class_id: m for m in classes.memberships(user)}
    row = repo.candidate(candidate_id, list(mine))
    if row is None or (not mine[row.class_id].is_rep and row.announcement.submitted_by != user.id):
        raise NotFoundError("We couldn't find that announcement.", code="CANDIDATE_NOT_FOUND")
    return row, mine[row.class_id]


def confirm(user, candidate_id: uuid.UUID, body: dict) -> dict:
    """A rep's confirmation: a new verified event, or the change to an existing one."""
    candidate, m = _find_candidate(user, candidate_id)
    if not m.is_rep:
        raise ForbiddenError("Only a class rep can confirm this. Until a rep does, it stays unverified.", code="REP_ONLY")
    if body["on"] is not None:
        _check_event_day(body["on"])
    announcement = candidate.announcement

    if body["change"] is None:
        event = ClassEvent(
            class_id=candidate.class_id,
            kind=body["kind"],
            title=_clean(body["title"]) or body["kind"].capitalize(),
            module=m.module_code,
            on_date=body["on"],
            at_time=body["at"],
            venue=_clean(body["venue"]),
            weighting=body["weighting"],
            verified_by=user.id,
            source_announcement_id=announcement.id,
            cancelled=False,
            version=1,
        )
        repo.add(event)
        lines = [f"{event.title} on {_when(event.on_date, event.at_time)} is now a verified event for {m.module_code}."]
    else:
        event = repo.event(body["event_id"], [candidate.class_id])
        if event is None:
            raise _field_error("event_id", "Choose an event from this class.")
        if event.cancelled:
            raise _field_error("event_id", "That event is already cancelled.")
        diffs = _diffs(event, body)
        if not diffs:
            raise _field_error("on", "Nothing changes: the event already has this date, time and venue.")
        for field, old, new in diffs:
            repo.add(EventChange(
                event_id=event.id, field=field, old=_stored(old), new=_stored(new),
                changed_by=user.id, announcement_id=announcement.id,
            ))
            setattr(event, _COLUMNS[field], new)
        event.version += 1
        event.verified_by = user.id
        lines = [change_line(field, old, new) for field, old, new in diffs]

    announcement.status, announcement.decided_at = "confirmed", _now()
    repo.delete(candidate)
    db.session.commit()
    return {"event": _events([event], m, user)[0], "lines": lines}


def discard(user, candidate_id: uuid.UUID) -> dict:
    """A rep turns a candidate down, or the student who sent it takes it back."""
    candidate, _ = _find_candidate(user, candidate_id)
    announcement = candidate.announcement
    announcement.status, announcement.decided_at = "discarded", _now()
    repo.delete(candidate)
    db.session.commit()
    return {}


_COLUMNS = {"on": "on_date", "at": "at_time", "venue": "venue", "cancelled": "cancelled"}


def _diffs(event: ClassEvent, body: dict) -> list[tuple[str, object, object]]:
    """(field, old, new) for each field a change message changes. What's sent is what the event becomes."""
    if body["change"] == "cancelled":
        return [("cancelled", False, True)]
    wanted = {"on": body["on"], "at": body["at"], "venue": _clean(body["venue"])}
    return [
        (field, getattr(event, _COLUMNS[field]), new)
        for field, new in wanted.items()
        if getattr(event, _COLUMNS[field]) != new
    ]


def _stored(value) -> str | None:
    """A changed value as event_changes keeps it: text."""
    if value is None:
        return None
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, time):
        return f"{value:%H:%M}"
    return str(value)


def _typed(field: str, value: str | None):
    """The other way, for the engine's wording."""
    if field == "cancelled":
        return value == "yes"
    if value is None:
        return None
    if field == "on":
        return date.fromisoformat(value)
    if field == "at":
        return time.fromisoformat(value)
    return value


def _check_event_day(day: date) -> None:
    today = _today()
    if day < today - timedelta(days=EVENT_DAYS_BACK):
        raise _field_error("on", f"That's more than {EVENT_DAYS_BACK} days ago.")
    if day > today + timedelta(days=EVENT_DAYS_AHEAD):
        raise _field_error("on", "That's more than a year away: please check the date.")


# ------------------------------------------------------------------ events


def events(user, class_id: uuid.UUID, query: dict) -> dict:
    """The class's verified events: by default a week back and four months ahead."""
    m = classes.membership(user, class_id)
    start = query["start"] or _today() - timedelta(days=EVENTS_BACK_DAYS)
    end = query["end"] or start + timedelta(days=EVENTS_BACK_DAYS + EVENTS_AHEAD_DAYS)
    if end < start:
        raise _field_error("to", "This comes before the start date.")
    if (end - start).days > RANGE_MAX_DAYS:
        raise _field_error("to", f"Ask for {RANGE_MAX_DAYS} days or fewer at a time.")
    rows = repo.events_between([class_id], start, end)
    return {"class_id": str(class_id), "from": start.isoformat(), "to": end.isoformat(), "events": _events(rows, m, user)}


def _my_event(user, event_id: uuid.UUID) -> tuple[ClassEvent, classes.Membership]:
    mine = {m.class_id: m for m in classes.memberships(user)}
    row = repo.event(event_id, list(mine))
    if row is None:
        raise NotFoundError("We couldn't find that event.", code="EVENT_NOT_FOUND")
    return row, mine[row.class_id]


def flag(user, event_id: uuid.UUID, reason: str) -> dict:
    """Say an event looks wrong. One flag per student per event: flagging again changes the reason."""
    event, m = _my_event(user, event_id)
    row = repo.flag(event.id, user.id)
    if row is None:
        repo.add(EventFlag(event_id=event.id, user_id=user.id, reason=reason))
    else:
        row.reason = reason
    try:
        db.session.commit()
    except IntegrityError:  # the same tap twice at once
        db.session.rollback()
        repo.flag(event.id, user.id).reason = reason
        db.session.commit()
    return {"event": _events([event], m, user)[0]}


def unflag(user, event_id: uuid.UUID) -> dict:
    event, m = _my_event(user, event_id)
    row = repo.flag(event.id, user.id)
    if row is None:
        raise NotFoundError("You haven't flagged this event.", code="FLAG_NOT_FOUND")
    repo.delete(row)
    db.session.commit()
    return {"event": _events([event], m, user)[0]}


def my_flags(user, event_ids: list[uuid.UUID]) -> dict[uuid.UUID, str]:
    return repo.my_flags(user.id, event_ids)


def export_for(user) -> dict:
    """POPIA export: the announcements the student sent (their text while it's kept) and the flags they
    raised. Events a rep confirmed belong to the class, not to one student."""
    return {
        "announcements": [
            {
                "module": module,
                "sent_on": a.sent_on.isoformat(),
                "status": a.status,
                "text": a.raw_text,
                "decided_at": a.decided_at.isoformat() if a.decided_at else None,
            }
            for a, module in repo.announcements_by(user.id)
        ],
        "flags": [
            {"event": e.title, "module": e.module, "on": e.on_date.isoformat(), "reason": f.reason,
             "flagged_at": f.updated_at.isoformat()}
            for f, e in repo.flags_by(user.id)
        ],
    }


def erase_all_for(user) -> None:
    """The announcements this student sent and the flags they raised, deleted for real: the demo's daily
    reset (and DELETE /me's later). Verified events stay with their class."""
    repo.erase_all(user.id)
    db.session.commit()


# ------------------------------------------------------------- what's sent


def brief(row: ClassEvent, your_flag: str | None = None) -> dict:
    """An event as the week strip and a candidate show it."""
    return {
        "id": str(row.id),
        "class_id": str(row.class_id),
        "kind": row.kind,
        "title": row.title,
        "module": row.module,
        "on": row.on_date.isoformat(),
        "at": _clock(row.at_time),
        "when": _when(row.on_date, row.at_time),
        "venue": row.venue,
        "weighting": row.weighting,
        "cancelled": row.cancelled,
        "version": row.version,
        "verified": True,
        "your_flag": your_flag,
    }


def _events(rows: list[ClassEvent], m: classes.Membership, user) -> list[dict]:
    ids = [row.id for row in rows]
    changes = repo.changes_for(ids)
    flags = repo.my_flags(user.id, ids)
    counts = repo.flag_counts(ids) if m.is_rep else {}
    out = []
    for row in rows:
        view = brief(row, flags.get(row.id))
        view["changes"] = [
            {
                "field": ch.field,
                "old": ch.old,
                "new": ch.new,
                "changed_on": ch.created_at.astimezone(ZoneInfo(TIMEZONE)).date().isoformat(),
                "line": change_line(ch.field, _typed(ch.field, ch.old), _typed(ch.field, ch.new)),
            }
            for ch in changes.get(row.id, [])
        ]
        if m.is_rep:  # how many and why, never who
            reasons = counts.get(row.id, {})
            view["flags"] = {"count": sum(reasons.values()), "reasons": reasons}
        out.append(view)
    return out


def _candidate(row: EventCandidate, m: classes.Membership, user) -> dict:
    c = Candidate(
        raw="",
        kind=row.kind,
        title=row.title,
        module=row.module,
        on=row.on_date,
        at=row.at_time,
        venue=row.venue,
        weighting=row.weighting,
        change=row.change,
        confidence=dict(row.confidence or {}),
        notes=list(row.notes or []),
    )
    target = row.event if row.event is not None and not row.event.cancelled else None
    lines = reading(c, target.title if target else None, target.on_date if target else None)
    if not m.is_rep:
        lines.append(WAITING_FOR_REP)
    return {
        "id": str(row.id),
        "class_id": str(row.class_id),
        "sent_on": row.announcement.sent_on.isoformat(),
        "text": row.announcement.raw_text,
        "from_rep": row.from_rep,
        "yours": row.announcement.submitted_by == user.id,
        "confirmable": m.is_rep,
        "read_as": {
            "kind": row.kind,
            "title": row.title,
            "module": row.module,
            "on": _iso(row.on_date),
            "at": _clock(row.at_time),
            "venue": row.venue,
            "weighting": row.weighting,
            "change": row.change,
        },
        "confidence": c.confidence,
        "needs_check": c.needs_check(),
        "changes_event": brief(target) if target else None,
        "proposed": _proposed(row, target),
        "lines": lines,
    }


def _proposed(row: EventCandidate, target: ClassEvent | None) -> dict:
    """What the rep's confirm form starts with."""
    if row.change and target is not None:
        moved = row.change == "moved"
        return {
            "change": row.change,
            "event_id": str(target.id),
            "kind": target.kind,
            "title": target.title,
            "on": _iso((row.on_date if moved else None) or target.on_date),
            "at": _clock((row.at_time if moved else None) or target.at_time),
            "venue": (row.venue if moved else None) or target.venue,
            "weighting": target.weighting,
        }
    return {
        "change": row.change,
        "event_id": None,
        "kind": row.kind,
        "title": row.title or (row.kind.capitalize() if row.kind else None),
        "on": _iso(row.on_date),
        "at": _clock(row.at_time),
        "venue": row.venue,
        "weighting": row.weighting,
    }
