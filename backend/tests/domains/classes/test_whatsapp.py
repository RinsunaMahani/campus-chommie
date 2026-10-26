"""
The WhatsApp bot (M6), end to end against a faked Meta, on Mon 12 Oct 2026. A student links their number with a
one-time code from the app; a rep forwards an announcement and confirms what the bot read, and it goes live for the
class exactly as from the app's rep panel. Every hostile case the brief names: unsigned or wrongly signed bodies,
stale and repeated messages, groups, someone else's announcement, guessed codes. Numbers are kept only as hashes.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import time
import uuid
from datetime import date

import pytest
from class_helpers import API, CLASSES, join, make_class, student
from sqlalchemy import text

from src.domains.classes.classes.services import class_service
from src.domains.classes.events.services import events_service, week_service
from src.domains.classes.whatsapp.services import sender, whatsapp_service
from src.extensions import db
from src.shared.rate_limit.limiter import limiter

TODAY = date(2026, 10, 12)  # a Monday
SECRET = "test-app-secret"
PHONE_ID = "1000001"
REP_PHONE, CLASSMATE_PHONE, STRANGER_PHONE = "27820000001", "27820000002", "27820000003"
WEBHOOK = f"{API}/webhooks/whatsapp"
ME = f"{API}/me/whatsapp"
TEST_2 = "ANA201 Test 2 on 20 Oct at 08:00, LT 3, worth 20%"


@pytest.fixture(autouse=True)
def on_12_october(monkeypatch):
    for module in (class_service, events_service, week_service, whatsapp_service):
        monkeypatch.setattr(module, "_today", lambda: TODAY)


@pytest.fixture
def bot(app, monkeypatch):
    for key, value in {
        "WHATSAPP_VERIFY_TOKEN": "verify-me", "WHATSAPP_APP_SECRET": SECRET, "WHATSAPP_ACCESS_TOKEN": "token",
        "WHATSAPP_PHONE_NUMBER_ID": PHONE_ID, "WHATSAPP_PHONE_KEY": "phone-key", "WHATSAPP_DISPLAY_NUMBER": "+1 555 010 0000",
    }.items():
        monkeypatch.setitem(app.config, key, value)
    sender.OUTBOX.clear()
    yield sender.OUTBOX
    sender.OUTBOX.clear()


@pytest.fixture
def rep(client, outbox):
    return student(client, outbox, "thabo@example.com")


@pytest.fixture
def classmate(client, outbox):
    return student(client, outbox, "naledi@example.com")


@pytest.fixture
def anatomy(client, rep, classmate):
    made = make_class(client, rep)
    join(client, classmate, made["invite_code"])
    return made


# ------------------------------------------------------------------ helpers


def _message(phone: str, *, body: str | None = None, button: str | None = None, at: float | None = None,
             message_id: str | None = None, **extra) -> dict:
    m = {"from": phone, "id": message_id or f"wamid.{uuid.uuid4().hex}", "timestamp": str(int(at or time.time()))}
    if button is not None:
        m |= {"type": "interactive", "interactive": {"type": "button_reply", "button_reply": {"id": button, "title": "x"}}}
    else:
        m |= {"type": "text", "text": {"body": body}}
    return m | extra


def _envelope(*messages: dict, phone_number_id: str = PHONE_ID) -> dict:
    return {"object": "whatsapp_business_account", "entry": [{"id": "1", "changes": [{"field": "messages", "value": {
        "messaging_product": "whatsapp", "metadata": {"phone_number_id": phone_number_id}, "messages": list(messages)}}]}]}


def _post(client, payload, secret: str = SECRET, signature: str | None = None):
    raw = json.dumps(payload).encode() if not isinstance(payload, bytes) else payload
    sig = signature or "sha256=" + hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest()
    return client.post(WEBHOOK, data=raw, content_type="application/json", headers={"X-Hub-Signature-256": sig})


def say(client, phone: str, **message) -> dict:
    r = _post(client, _envelope(_message(phone, **message)))
    assert r.status_code == 200, r.get_json()
    return r.get_json()["data"]


def replies(outbox, phone: str) -> list[dict]:
    return [p for to, p in outbox if to == phone]


def last_words(outbox, phone: str) -> str:
    p = replies(outbox, phone)[-1]
    return p["text"]["body"] if p["type"] == "text" else p["interactive"]["body"]["text"]


def link(client, outbox, who, phone: str) -> None:
    code = client.post(f"{ME}/code", headers=who.headers).get_json()["data"]["code"]
    say(client, phone, body=f"LINK {code}")
    assert last_words(outbox, phone).startswith("Linked."), last_words(outbox, phone)


def events_of(client, who, class_id) -> list[dict]:
    return client.get(f"{CLASSES}/{class_id}/events", headers=who.headers).get_json()["data"]["events"]


# ------------------------------------------------------------- switched off


def test_with_no_secrets_the_bot_does_not_exist(client, rep):
    assert client.get(WEBHOOK, query_string={"hub.mode": "subscribe"}).status_code == 404
    assert _post(client, _envelope(_message(REP_PHONE, body="HELP"))).status_code == 404
    assert client.get(ME, headers=rep.headers).get_json()["data"] == {"available": False, "linked": 0, "linked_on": [], "bot": None}
    r = client.post(f"{ME}/code", headers=rep.headers)
    assert r.status_code == 409 and r.get_json()["code"] == "WHATSAPP_OFF"


@pytest.mark.parametrize("method, path", [("get", ME), ("post", f"{ME}/code"), ("delete", ME)])
def test_the_apps_routes_need_a_token(client, bot, method, path):
    assert getattr(client, method)(path).status_code == 401


# ---------------------------------------------------------------- handshake


def test_metas_handshake_echoes_the_challenge_only_for_our_token(client, bot):
    ok = client.get(WEBHOOK, query_string={"hub.mode": "subscribe", "hub.verify_token": "verify-me", "hub.challenge": "1158201444"})
    assert ok.status_code == 200 and ok.data == b"1158201444" and ok.mimetype == "text/plain"
    wrong = client.get(WEBHOOK, query_string={"hub.mode": "subscribe", "hub.verify_token": "guess", "hub.challenge": "1"})
    assert wrong.status_code == 403
    mode = client.get(WEBHOOK, query_string={"hub.mode": "unsubscribe", "hub.verify_token": "verify-me", "hub.challenge": "1"})
    assert mode.status_code == 403


@pytest.mark.parametrize("query", [
    {"hub.mode": "subscribe", "hub.verify_token": "verify-me", "hub.challenge": "<script>alert(1)</script>"},
    {"hub.mode": "subscribe", "hub.verify_token": "verify-me"},
    {"hub.mode": "subscribe", "hub.verify_token": "verify-me", "hub.challenge": "1", "extra": "x"},
])
def test_a_handshake_that_isnt_metas_shape_is_refused(client, bot, query):
    assert client.get(WEBHOOK, query_string=query).status_code == 422


# ---------------------------------------------------------------- signatures


@pytest.mark.parametrize("signature", [None, "", "sha256=", "sha1=abc", "sha256=" + "0" * 64, "sha256=" + "G" * 64])
def test_unsigned_or_wrongly_signed_bodies_are_refused(client, bot, signature):
    raw = json.dumps(_envelope(_message(STRANGER_PHONE, body="HELP"))).encode()
    headers = {} if signature is None else {"X-Hub-Signature-256": signature}
    r = client.post(WEBHOOK, data=raw, content_type="application/json", headers=headers)
    assert r.status_code == 401 and r.get_json()["code"] == "INVALID_SIGNATURE"
    assert bot == []


def test_a_body_signed_with_another_secret_or_changed_after_signing_is_refused(client, bot):
    assert _post(client, _envelope(_message(STRANGER_PHONE, body="HELP")), secret="not-ours").status_code == 401
    raw = json.dumps(_envelope(_message(STRANGER_PHONE, body="HELP"))).encode()
    sig = "sha256=" + hmac.new(SECRET.encode(), raw, hashlib.sha256).hexdigest()
    tampered = raw.replace(b"HELP", b"WEEK")
    r = client.post(WEBHOOK, data=tampered, content_type="application/json", headers={"X-Hub-Signature-256": sig})
    assert r.status_code == 401 and bot == []


@pytest.mark.parametrize("payload", [b"not json", b"[]", {"object": "page"}, {"object": "whatsapp_business_account", "entry": "x"},
                                     {"object": "whatsapp_business_account", "entry": [{"changes": [{"field": "messages", "value": []}]}]},
                                     {"object": "whatsapp_business_account", "entry": [{"changes": [{"field": "messages", "value": {
                                         "metadata": {"phone_number_id": PHONE_ID}, "messages": ["x", 1, None, {"from": 5}]}}]}]}])
def test_signed_bodies_in_any_other_shape_are_answered_200_and_ignored(client, bot, payload):
    r = _post(client, payload)
    assert r.status_code == 200 and r.get_json()["data"] == {"answered": 0} and bot == []


# ------------------------------------------------------------------- linking


def test_a_student_links_their_number_and_only_its_hash_is_kept(client, bot, rep):
    r = client.post(f"{ME}/code", headers=rep.headers)
    assert r.status_code == 201
    data = r.get_json()["data"]
    assert len(data["code"]) == 9 and data["message"] == f"LINK {data['code']}" and data["minutes"] == 10
    assert data["send_link"] == f"https://wa.me/15550100000?text=LINK%20{data['code']}"
    say(client, REP_PHONE, body=f"link {data['code'].lower()}")
    assert last_words(bot, REP_PHONE).startswith("Linked.")
    assert client.get(ME, headers=rep.headers).get_json()["data"]["linked"] == 1

    with client.application.app_context():
        rows = db.session.execute(text("SELECT phone_hash FROM classes.whatsapp_links")).all()
        codes = db.session.execute(text("SELECT count(*) FROM classes.whatsapp_link_codes")).scalar()
    assert len(rows) == 1 and REP_PHONE not in rows[0][0] and len(rows[0][0]) == 64
    assert codes == 0  # used once, gone
    export = client.get(f"{API}/me/export", headers=rep.headers).get_json()["data"]
    assert REP_PHONE not in json.dumps(export) and rows[0][0] not in json.dumps(export)


def test_a_code_works_once_and_a_wrong_or_expired_one_never(client, bot, rep, classmate):
    code = client.post(f"{ME}/code", headers=rep.headers).get_json()["data"]["code"]
    say(client, STRANGER_PHONE, body="LINK ABCD-EFGH")
    assert "didn't work" in last_words(bot, STRANGER_PHONE)
    say(client, REP_PHONE, body=f"LINK {code}")
    say(client, CLASSMATE_PHONE, body=f"LINK {code}")
    assert "didn't work" in last_words(bot, CLASSMATE_PHONE)

    old = client.post(f"{ME}/code", headers=classmate.headers).get_json()["data"]["code"]
    with client.application.app_context():
        db.session.execute(text("UPDATE classes.whatsapp_link_codes SET expires_at = now() - interval '1 second'"))
        db.session.commit()
    say(client, CLASSMATE_PHONE, body=f"LINK {old}")
    assert "didn't work" in last_words(bot, CLASSMATE_PHONE)


def test_a_new_code_replaces_the_last_one(client, bot, rep):
    first = client.post(f"{ME}/code", headers=rep.headers).get_json()["data"]["code"]
    client.post(f"{ME}/code", headers=rep.headers)
    say(client, REP_PHONE, body=f"LINK {first}")
    assert "didn't work" in last_words(bot, REP_PHONE)


def test_guessing_codes_stops_after_five_tries_an_hour(client, bot, rep):
    limiter.enabled = True
    try:
        for _ in range(5):
            say(client, STRANGER_PHONE, body="LINK ZZZZ-ZZZZ")
        code = client.post(f"{ME}/code", headers=rep.headers).get_json()["data"]["code"]
        say(client, STRANGER_PHONE, body=f"LINK {code}")
        assert last_words(bot, STRANGER_PHONE).startswith("Too many tries")
        assert client.get(ME, headers=rep.headers).get_json()["data"]["linked"] == 0
    finally:
        limiter.enabled = False


def test_a_number_that_isnt_linked_is_only_told_how_to_link(client, bot, rep, anatomy):
    say(client, STRANGER_PHONE, body=TEST_2)
    say(client, STRANGER_PHONE, body="WEEK")
    assert all("isn't linked" in p["text"]["body"] for p in replies(bot, STRANGER_PHONE))
    assert events_of(client, rep, anatomy["id"]) == []


def test_stop_and_the_apps_unlink_both_unlink(client, bot, rep, classmate):
    link(client, bot, rep, REP_PHONE)
    say(client, REP_PHONE, body="stop")
    assert last_words(bot, REP_PHONE).startswith("Unlinked.")
    say(client, REP_PHONE, body="WEEK")
    assert "isn't linked" in last_words(bot, REP_PHONE)

    link(client, bot, classmate, CLASSMATE_PHONE)
    assert client.delete(ME, headers=classmate.headers).status_code == 200
    assert client.get(ME, headers=classmate.headers).get_json()["data"]["linked"] == 0


@pytest.mark.parametrize("method, path, kwargs", [
    ("get", ME, {"query_string": {"x": "1"}}), ("post", f"{ME}/code", {"json": {"phone": "27820000001"}}),
    ("delete", ME, {"json": {"user_id": str(uuid.uuid4())}}), ("post", f"{ME}/code", {"data": "nope", "content_type": "text/plain"}),
])
def test_the_apps_routes_take_nothing(client, bot, rep, method, path, kwargs):
    assert getattr(client, method)(path, headers=rep.headers, **kwargs).status_code == 422


# ------------------------------------------------------- stale, repeated, groups


def test_stale_future_repeated_and_group_messages_are_dropped(client, bot, rep):
    link(client, bot, rep, REP_PHONE)
    sent = len(bot)
    assert say(client, REP_PHONE, body="HELP", at=time.time() - 600)["answered"] == 0
    assert say(client, REP_PHONE, body="HELP", at=time.time() + 600)["answered"] == 0
    assert say(client, REP_PHONE, body="HELP", group_id="120363000000000000")["answered"] == 0
    assert say(client, REP_PHONE, body="HELP", timestamp="soon")["answered"] == 0
    once = _message(REP_PHONE, body="HELP")
    assert _post(client, _envelope(once)).get_json()["data"]["answered"] == 1
    assert _post(client, _envelope(once)).get_json()["data"]["answered"] == 0  # Meta's retry
    assert len(bot) == sent + 1


def test_messages_to_another_business_number_are_ignored(client, bot, rep):
    link(client, bot, rep, REP_PHONE)
    r = _post(client, _envelope(_message(REP_PHONE, body="HELP"), phone_number_id="999"))
    assert r.get_json()["data"]["answered"] == 0


# -------------------------------------------------------------- the rep flow


def test_a_rep_forwards_an_announcement_and_confirms_it_from_whatsapp(client, bot, rep, classmate, anatomy):
    link(client, bot, rep, REP_PHONE)
    say(client, REP_PHONE, body=TEST_2)
    p = replies(bot, REP_PHONE)[-1]
    assert p["type"] == "interactive"
    assert p["interactive"]["body"]["text"].startswith("ANA201: here's what I read.")
    confirm_id, discard_id = [b["reply"]["id"] for b in p["interactive"]["action"]["buttons"]]
    assert confirm_id.startswith("confirm:") and discard_id.startswith("discard:")
    assert events_of(client, classmate, anatomy["id"]) == []

    say(client, REP_PHONE, button=confirm_id)
    assert last_words(bot, REP_PHONE).endswith("Your class can see it in the app now.")
    live = events_of(client, classmate, anatomy["id"])
    assert [(e["kind"], e["on"], e["at"]) for e in live] == [("test", "2026-10-20", "08:00")]

    say(client, REP_PHONE, button=confirm_id)  # pressed again
    assert "isn't waiting" in last_words(bot, REP_PHONE)
    assert len(events_of(client, classmate, anatomy["id"])) == 1


def test_a_rep_discards_from_whatsapp(client, bot, rep, anatomy):
    link(client, bot, rep, REP_PHONE)
    say(client, REP_PHONE, body=TEST_2)
    discard_id = replies(bot, REP_PHONE)[-1]["interactive"]["action"]["buttons"][1]["reply"]["id"]
    say(client, REP_PHONE, button=discard_id)
    assert last_words(bot, REP_PHONE).startswith("Discarded.")
    assert events_of(client, rep, anatomy["id"]) == []


def test_a_classmates_forward_waits_for_a_rep_and_they_cant_confirm_it(client, bot, rep, classmate, anatomy):
    link(client, bot, classmate, CLASSMATE_PHONE)
    say(client, CLASSMATE_PHONE, body="Guys the ANA201 quiz is on Friday 16 Oct")
    p = replies(bot, CLASSMATE_PHONE)[-1]
    assert p["type"] == "text" and "class rep checks this" in p["text"]["body"]
    cid = client.get(f"{CLASSES}/{anatomy['id']}/candidates", headers=rep.headers).get_json()["data"]["candidates"][0]["id"]
    say(client, CLASSMATE_PHONE, button=f"confirm:{cid}")
    assert "Only a class rep" in last_words(bot, CLASSMATE_PHONE)
    assert events_of(client, rep, anatomy["id"]) == []


def test_a_button_for_someone_elses_class_is_not_found(client, bot, outbox, rep, anatomy):
    other_rep = student(client, outbox, "lerato@example.com")
    link(client, bot, other_rep, STRANGER_PHONE)
    make_class(client, other_rep, module_code="PHY101", module_name="Physics")
    link(client, bot, rep, REP_PHONE)
    say(client, REP_PHONE, body=TEST_2)
    confirm_id = replies(bot, REP_PHONE)[-1]["interactive"]["action"]["buttons"][0]["reply"]["id"]
    say(client, STRANGER_PHONE, button=confirm_id)
    assert "isn't waiting" in last_words(bot, STRANGER_PHONE)
    assert events_of(client, rep, anatomy["id"]) == []


@pytest.mark.parametrize("button", [
    "confirm:not-a-uuid", "delete:" + str(uuid.uuid4()), "", "x" * 300,
    # 36 characters a uuid is made of, in shapes that aren't one: these used to crash the webhook (a 500).
    "confirm:" + "-" * 36, "discard:" + "a" * 36, "confirm:" + str(uuid.uuid4()).replace("-", "a", 1),
])
def test_made_up_buttons_do_nothing(client, bot, rep, anatomy, button):
    link(client, bot, rep, REP_PHONE)
    sent = len(bot)
    say(client, REP_PHONE, button=button)
    assert len(bot) == sent


def test_a_message_without_a_date_is_finished_in_the_app(client, bot, rep, anatomy):
    link(client, bot, rep, REP_PHONE)
    say(client, REP_PHONE, body="ANA201 assignment 3 is out, check the portal")
    p = replies(bot, REP_PHONE)[-1]
    confirm_id = p["interactive"]["action"]["buttons"][0]["reply"]["id"]
    say(client, REP_PHONE, button=confirm_id)
    assert "finish it there" in last_words(bot, REP_PHONE)
    assert events_of(client, rep, anatomy["id"]) == []


def test_with_two_classes_the_module_code_picks_one(client, bot, rep, anatomy):
    make_class(client, rep, module_code="PHY101", module_name="Physics")
    link(client, bot, rep, REP_PHONE)
    say(client, REP_PHONE, body="Test on 20 Oct at 08:00")
    assert "Which class is this for?" in last_words(bot, REP_PHONE) and "ANA201, PHY101" in last_words(bot, REP_PHONE)
    say(client, REP_PHONE, body="PHY101 test on 21 Oct at 09:00")
    assert last_words(bot, REP_PHONE).startswith("PHY101: here's what I read.")


def test_too_long_or_classless_messages_say_why(client, bot, rep):
    link(client, bot, rep, REP_PHONE)
    say(client, REP_PHONE, body=TEST_2)
    assert last_words(bot, REP_PHONE).startswith("You're not in any classes yet")


def test_an_announcement_too_long_for_the_app_is_too_long_here(client, bot, rep, anatomy):
    link(client, bot, rep, REP_PHONE)
    say(client, REP_PHONE, body="ANA201 " + "x" * 2100)
    assert "2000" in last_words(bot, REP_PHONE)


def test_pictures_and_voice_notes_get_a_text_only_reply(client, bot, rep):
    link(client, bot, rep, REP_PHONE)
    m = _message(REP_PHONE, body="x") | {"type": "image", "image": {"id": "1"}}
    m.pop("text")
    _post(client, _envelope(m))
    assert last_words(bot, REP_PHONE).startswith("I can only read text")


# ---------------------------------------------------------------- WEEK, HELP


def test_week_lists_the_next_seven_days_of_verified_events(client, bot, rep, classmate, anatomy):
    link(client, bot, classmate, CLASSMATE_PHONE)
    say(client, CLASSMATE_PHONE, body="week")
    assert last_words(bot, CLASSMATE_PHONE).startswith("Nothing from your classes in the next 7 days")
    link(client, bot, rep, REP_PHONE)
    say(client, REP_PHONE, body="ANA201 quiz on 15 Oct at 10:00 in LT 2")
    say(client, REP_PHONE, button=replies(bot, REP_PHONE)[-1]["interactive"]["action"]["buttons"][0]["reply"]["id"])
    say(client, REP_PHONE, body=TEST_2)  # 20 Oct: 8 days away, not listed
    say(client, CLASSMATE_PHONE, body="WEEK")
    words = last_words(bot, CLASSMATE_PHONE)
    assert words.startswith("Your next 7 days:") and "ANA201" in words and "LT 2" in words and "08:00" not in words


def test_help_says_what_the_bot_does_and_what_it_never_asks(client, bot, rep):
    link(client, bot, rep, REP_PHONE)
    say(client, REP_PHONE, body="Hi!")
    assert "never ask for passwords" in last_words(bot, REP_PHONE)


def test_a_deleted_account_is_unlinked_with_it(client, bot, rep, app):
    link(client, bot, rep, REP_PHONE)
    with app.app_context():
        db.session.execute(text("DELETE FROM identity.users WHERE id = :id"), {"id": rep.id})
        db.session.commit()
        assert db.session.execute(text("SELECT count(*) FROM classes.whatsapp_links")).scalar() == 0
    say(client, REP_PHONE, body="WEEK")
    assert "isn't linked" in last_words(bot, REP_PHONE)
