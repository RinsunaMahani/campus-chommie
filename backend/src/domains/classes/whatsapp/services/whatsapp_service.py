"""
The WhatsApp bot, and the app's side of linking.

In the app (signed in, owner only):
  status(user)        whether the bot is on, how many numbers are linked, the bot's number
  new_code(user)      a one-time code (replaces any earlier one) and the message to send it in
  unlink(user)        every linked number of this account, removed
  export_for / erase_all_for   POPIA's export, and deleting for real

From Meta (receive(raw, signature)): each message is dropped unless the body is signed with the app secret, it is
from our own business number's webhook, it is a private chat, it is less than 5 minutes old and it hasn't been seen
before. Then, by what it says:
  LINK <code>         links the sender's number to the code's account
  HELP / HI / MENU    what the bot does
  WEEK                verified class events in the next 7 days
  STOP / UNLINK       unlinks the sender's number
  Confirm / Discard   a rep's buttons under an announcement the bot read
  anything else       an announcement for one of the sender's classes, read like the app's rep panel reads it
A number that isn't linked only gets told how to link it. No money, marks or anything private is ever sent.
"""
from __future__ import annotations

import logging
import re
import secrets
import uuid
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

from limits import parse_many
from sqlalchemy.exc import IntegrityError

from src.core.exceptions import AppError, ConflictError, ValidationError
from src.domains.classes.classes.services import class_service as classes
from src.domains.classes.events.services import events_service, week_service
from src.domains.identity.accounts.services import account_service
from src.extensions import db
from src.shared.rate_limit.limiter import limiter

from ..constants import (
    CODE_ALPHABET,
    CODE_LENGTH,
    CODE_MINUTES,
    LINK_ATTEMPT_LIMIT,
    MAX_AGE_SECONDS,
    MAX_AHEAD_SECONDS,
    MAX_LINKS,
    SEEN_HOURS,
    SENDER_LIMIT,
    TIMEZONE,
    WEEK_DAYS,
)
from ..repositories import whatsapp_repository as repo
from . import sender, signature

logger = logging.getLogger("campus_chommie.whatsapp")

HELP = (
    "Hi, I'm Campus Chommie on WhatsApp.\n\n"
    "• Class rep? Forward me an announcement (a test, assignment, venue change) and I'll read it. "
    "Tap Confirm and your class sees it in the app.\n"
    "• WEEK: your class tests and deadlines for the next 7 days.\n"
    "• STOP: unlink this number.\n\n"
    "I never ask for passwords, ID numbers or bank details."
)
NOT_LINKED = (
    "This number isn't linked to Campus Chommie yet. In the app, open Profile, then WhatsApp, and tap "
    "\"Link WhatsApp\". Then send me the message it shows (LINK and your code)."
)
BAD_CODE = "That code didn't work. Codes last 10 minutes and work once: get a new one in the app (Profile, then WhatsApp)."
TOO_MANY_LINKS = f"This account already has {MAX_LINKS} WhatsApp numbers linked. Unlink one in the app first."
LINKED = "Linked. Send WEEK for your next 7 days, or forward me a class announcement. Send HELP any time."
UNLINKED = "Unlinked. I won't answer this number until you link it again in the app."
NO_CLASSES = "You're not in any classes yet. Join your class in the app with the code from your class rep."
ONLY_TEXT = "I can only read text messages for now. Forward the announcement as text."
NOT_WAITING = "That announcement isn't waiting any more: a rep may already have confirmed or discarded it."
FINISH_IN_APP = "Some details are missing, like the date. Open Campus Chommie, go to your class, and finish it there."
DISCARDED = "Discarded. Nothing changes for your class."

_LINK = re.compile(r"^\s*link\s+([A-Za-z0-9][A-Za-z0-9 -]{5,20})\s*$", re.IGNORECASE)
_WORD = re.compile(r"^\s*([A-Za-z]+)\s*[.!?]*\s*$")
# A well-formed id only: anything else is ignored, never parsed (a malformed one used to crash the webhook).
_BUTTON = re.compile(r"^(confirm|discard):([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$")
_PHONE = re.compile(r"^\d{8,15}$")


def _now() -> datetime:
    return datetime.now(UTC)


def _today() -> date:
    return datetime.now(ZoneInfo(TIMEZONE)).date()


# ---------------------------------------------------------------- the app's side


def _bot() -> dict:
    from flask import current_app

    shown = current_app.config.get("WHATSAPP_DISPLAY_NUMBER") or None
    digits = re.sub(r"\D", "", shown or "")
    return {"number": shown, "chat_link": f"https://wa.me/{digits}" if digits else None}


def status(user) -> dict:
    links = repo.links_for(user.id) if signature.available() else []
    return {
        "available": signature.available(),
        "linked": len(links),
        "linked_on": [_local_day(row.created_at) for row in links],
        "bot": _bot() if signature.available() else None,
    }


def _local_day(at: datetime) -> str:
    return at.astimezone(ZoneInfo(TIMEZONE)).date().isoformat()


def _require_bot() -> None:
    if not signature.available():
        raise AppError("WhatsApp isn't switched on yet.", status_code=409, code="WHATSAPP_OFF")


def new_code(user) -> dict:
    """A new one-time code; any earlier code of this account stops working."""
    _require_bot()
    if repo.count_links(user.id) >= MAX_LINKS:
        raise ConflictError(TOO_MANY_LINKS, code="WHATSAPP_TOO_MANY")
    code = "".join(secrets.choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))
    expires = _now() + timedelta(minutes=CODE_MINUTES)
    repo.delete_codes(user.id)
    repo.forget_codes_before(_now())
    repo.add_code(user.id, signature.code_hash(code), expires)
    db.session.commit()
    shown = f"{code[:4]}-{code[4:]}"
    bot = _bot()
    message = f"LINK {shown}"
    return {
        "code": shown,
        "message": message,
        "expires_at": expires.isoformat(),
        "minutes": CODE_MINUTES,
        "bot": bot,
        "send_link": f"{bot['chat_link']}?text=LINK%20{shown}" if bot["chat_link"] else None,
    }


def unlink(user) -> dict:
    repo.delete_links(user.id)
    repo.delete_codes(user.id)
    db.session.commit()
    return {}


def export_for(user) -> dict:
    """POPIA export: how many numbers are linked and since when. We hold no number to export, only its hash."""
    return {"linked_numbers": [{"linked_on": _local_day(row.created_at)} for row in repo.links_for(user.id)]}


def erase_all_for(user) -> None:
    unlink(user)


# ------------------------------------------------------------------ from Meta


class BadSignature(AppError):
    status_code = 401
    code = "INVALID_SIGNATURE"


def receive(raw: bytes, signature_header: str | None, body) -> int:
    """Meta's webhook POST. Returns how many messages were answered."""
    if not signature.signed(raw, signature_header):
        raise BadSignature("This request isn't signed by WhatsApp.")
    if not isinstance(body, dict) or body.get("object") != "whatsapp_business_account":
        return 0
    from flask import current_app

    ours = current_app.config["WHATSAPP_PHONE_NUMBER_ID"]
    answered = 0
    for value in _values(body):
        if str((value.get("metadata") or {}).get("phone_number_id")) != ours:
            continue
        for message in value.get("messages") or []:
            if isinstance(message, dict) and _handle(message):
                answered += 1
    repo.forget_seen_before(_now() - timedelta(hours=SEEN_HOURS))
    db.session.commit()
    return answered


def _values(body: dict) -> list[dict]:
    out = []
    for entry in body.get("entry") or []:
        if not isinstance(entry, dict):
            continue
        for change in entry.get("changes") or []:
            if isinstance(change, dict) and change.get("field") == "messages" and isinstance(change.get("value"), dict):
                out.append(change["value"])
    return out


def _fresh(message: dict) -> bool:
    try:
        sent = int(str(message.get("timestamp")))
    except ValueError:
        return False
    age = _now().timestamp() - sent
    return -MAX_AHEAD_SECONDS <= age <= MAX_AGE_SECONDS


def _first_time(message_id: str) -> bool:
    """Marks the message seen; False when it already was (Meta retries until it hears 200)."""
    try:
        repo.add_seen(signature.message_hash(message_id))
        db.session.commit()  # now, so a reply that fails later can't make a retry answer twice
    except IntegrityError:
        db.session.rollback()
        return False
    return True


def _allowed(limit: str, *key: str) -> bool:
    if not limiter.enabled:
        return True
    return all(limiter.limiter.hit(item, "whatsapp", *key) for item in parse_many(limit))


def _handle(message: dict) -> bool:
    phone, message_id = str(message.get("from") or ""), message.get("id")
    if not _PHONE.match(phone) or not isinstance(message_id, str) or not 0 < len(message_id) <= 256:
        return False
    if "group_id" in message or "group_id" in (message.get("context") or {}):
        return False  # private chats only, never groups
    if not _fresh(message) or not _first_time(message_id):
        return False
    who = signature.phone_hash(phone)
    if not _allowed(SENDER_LIMIT, who):
        return False

    kind = message.get("type")
    if kind == "text":
        text = str((message.get("text") or {}).get("body") or "")
        _text(phone, who, text)
    elif kind == "interactive":
        reply = (message.get("interactive") or {}).get("button_reply") or {}
        _button(phone, who, str(reply.get("id") or ""))
    else:
        if repo.link_for_phone(who):
            sender.text(phone, ONLY_TEXT)
        else:
            sender.text(phone, NOT_LINKED)
    return True


def _linked_user(who: str):
    link = repo.link_for_phone(who)
    if link is None:
        return None
    user = account_service.get(link.user_id)
    return user if user is not None and user.is_active else None


def _text(phone: str, who: str, text: str) -> None:
    m = _LINK.match(text)
    if m:
        _link(phone, who, m.group(1))
        return
    user = _linked_user(who)
    if user is None:
        sender.text(phone, NOT_LINKED)
        return
    word = (_WORD.match(text).group(1).upper() if _WORD.match(text) else "")
    if word in ("HELP", "HI", "HELLO", "MENU", "START"):
        sender.text(phone, HELP)
    elif word == "WEEK":
        sender.text(phone, _week(user))
    elif word in ("STOP", "UNLINK"):
        link = repo.link_for_phone(who)
        repo.delete(link)
        db.session.commit()
        sender.text(phone, UNLINKED)
    else:
        _announcement(phone, user, text)


def _link(phone: str, who: str, typed: str) -> None:
    if not _allowed(LINK_ATTEMPT_LIMIT, "link", who):
        sender.text(phone, "Too many tries. Wait an hour, then get a new code in the app.")
        return
    code = re.sub(r"[\s-]", "", typed).upper()
    row = repo.code_by_hash(signature.code_hash(code)) if len(code) == 8 else None
    if row is None or row.expires_at <= _now():
        sender.text(phone, BAD_CODE)
        return
    user_id = row.user_id
    repo.delete(row)  # one use
    existing = repo.link_for_phone(who)
    if existing is not None and existing.user_id != user_id:
        repo.delete(existing)  # a number links to one account: the newest code wins
        db.session.flush()
    if existing is None or existing.user_id != user_id:
        if repo.count_links(user_id) >= MAX_LINKS:
            db.session.commit()
            sender.text(phone, TOO_MANY_LINKS)
            return
        repo.add_link(user_id, who)
    db.session.commit()
    sender.text(phone, LINKED)


def _week(user) -> str:
    today = _today()
    last = today + timedelta(days=WEEK_DAYS)
    weeks = week_service.week(user, 2, today)
    events = [
        e for w in weeks["weeks"] for e in w["events"]
        if today.isoformat() <= e["on"] <= last.isoformat() and not e["cancelled"]
    ]
    if not weeks["classes"]:
        return NO_CLASSES
    if not events:
        return f"Nothing from your classes in the next {WEEK_DAYS} days. Only events a class rep confirmed show here."
    lines = [f"Your next {WEEK_DAYS} days:"]
    for e in sorted(events, key=lambda e: (e["on"], e["at"] or "")):
        venue = f", {e['venue']}" if e["venue"] else ""
        lines.append(f"• {e['when']}: {e['module']} {e['title']}{venue}")
    return "\n".join(lines)


def _class_for(user, text: str):
    """The class an announcement is for: the only one, or the one whose module code the message names."""
    mine = classes.memberships(user)
    if len(mine) == 1:
        return mine[0], mine
    upper = text.upper()
    named = [m for m in mine if re.search(rf"\b{re.escape(m.module_code.upper())}\b", upper)]
    return (named[0] if len(named) == 1 else None), mine


def _announcement(phone: str, user, text: str) -> None:
    m, mine = _class_for(user, text)
    if not mine:
        sender.text(phone, NO_CLASSES)
        return
    if m is None:
        codes = ", ".join(sorted(x.module_code for x in mine))
        sender.text(phone, f"Which class is this for? Send it again with the module code in it ({codes}).")
        return
    try:
        candidate = events_service.announce_text(user, m.class_id, text)["candidate"]
    except ValidationError as e:
        sender.text(phone, _first_message(e) or "I couldn't read that. Try forwarding the announcement as text.")
        return
    body = "\n".join([f"{m.module_code}: here's what I read."] + candidate["lines"])
    if candidate["confirmable"]:
        sender.buttons(phone, body, [(f"confirm:{candidate['id']}", "Confirm"), (f"discard:{candidate['id']}", "Discard")])
    else:
        sender.text(phone, body)


def _first_message(error: ValidationError) -> str | None:
    for item in error.errors or []:
        for messages in (item or {}).values():
            if isinstance(messages, list) and messages and isinstance(messages[0], str):
                return messages[0]
    return None


def _button(phone: str, who: str, button_id: str) -> None:
    user = _linked_user(who)
    if user is None:
        sender.text(phone, NOT_LINKED)
        return
    m = _BUTTON.match(button_id)
    if m is None:
        return
    action, candidate_id = m.group(1), uuid.UUID(m.group(2))
    try:
        if action == "confirm":
            done = events_service.confirm_as_read(user, candidate_id)
            sender.text(phone, "\n".join(done["lines"] + ["Your class can see it in the app now."]))
        else:
            events_service.discard(user, candidate_id)
            sender.text(phone, DISCARDED)
    except ValidationError:
        db.session.rollback()
        sender.text(phone, FINISH_IN_APP)
    except AppError as e:  # not found (someone else's, or already decided) or not a rep
        db.session.rollback()
        sender.text(phone, NOT_WAITING if e.status_code == 404 else e.message)

