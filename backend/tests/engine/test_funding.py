"""
Funding on today's date: each funder's status, the list's order and counts, the filters, and
the funding a course-finder choice is shown. Made-up funders, so the rules are tested apart
from the shipped pack (test_packs.py checks that against its sources).
"""
from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from campus_engine.applications import CHECK, CLOSED, CLOSING_SOON, NOT_PUBLISHED, OPEN, OPENS_LATER, apply_guide
from campus_engine.bridges import Plan, Slot
from campus_engine.funding import (
    AUTOMATIC,
    VIA_UNIVERSITY,
    card,
    cards,
    counts,
    detail,
    field_counts,
    group,
    matches,
)
from campus_engine.matching import MEETS_MINIMUM, Match
from campus_engine.schemas import FIELDS, FundingPack, Programme, University, Window

TODAY = date(2026, 10, 11)
SOURCES = [{"id": "f", "url": "https://example.org/fund", "publisher": "Example Fund"}]


def funder(fid: str, **extra) -> dict:
    base = {
        "id": fid,
        "name": f"{fid.title()} Bursary",
        "short_name": fid.title(),
        "sector": "company",
        "fields": "any",
        "stages": ["first_year"],
        "who_can_apply": {"items": ["South African citizens"], "source": "f"},
        "applications": {"source": "f", "url": f"https://example.org/{fid}", "windows": []},
    }
    return base | extra


def windows(*items: dict) -> dict:
    return {"source": "f", "url": "https://example.org/apply", "windows": [{"source": "f", **w} for w in items]}


def pack(*funders: dict) -> FundingPack:
    return FundingPack.model_validate({"funders": list(funders), "sources": SOURCES})


NSFAS = funder(
    "nsfas", short_name="NSFAS", sector="government", every_plan=True,
    applications=windows({"intake": 2027, "opens": "2026-09-18", "closes": "2026-10-31"}),
)

#: Eight funders, one of each kind of status.
LIST = [
    funder("later", applications=windows({"intake": 2027, "opens": "2026-11-01", "closes": "2027-01-31"})),
    funder("soon", fields=["engineering"], applications=windows({"intake": 2027, "opens": "2026-09-01", "closes": "2026-10-20"})),
    funder("open", fields=["accounting"], stages=["senior"],
           applications=windows({"intake": 2027, "opens": "2026-09-01", "closes": "2026-12-01"})),
    funder("closed", fields=["engineering", "computing"], applications=windows({"intake": 2027, "closes": "2026-09-30"})),
    funder("quiet", sector="government"),
    funder("auto", kind="merit_award", sector="university", applying="automatic", study_at=["up"]),
    funder("campus", sector="university", applying="via_university", study_at=["tut"]),
    funder("loan", kind="loan", sector="government", fields=["engineering"], not_fields=["medicine"]),
]


# ------------------------------------------------------------------ the pack's rules


def test_field_tags_must_be_known():
    with pytest.raises(ValidationError, match="unknown field 'enginering'"):
        pack(funder("a", fields=["enginering"]))
    with pytest.raises(ValidationError, match="unknown field 'medcine'"):
        pack(funder("a", not_fields=["medcine"]))
    with pytest.raises(ValidationError, match='name at least one, or "any"'):
        pack(funder("a", fields=[]))
    with pytest.raises(ValidationError, match="unknown field 'example_field'"):
        Programme.model_validate({"id": "p", "name": "P", "fields": ["example_field"]})


def test_a_funder_says_what_it_is_for_and_who_it_is_for():
    with pytest.raises(ValidationError):
        pack(funder("a", stages=[]))
    with pytest.raises(ValidationError, match="stages: each once"):
        pack(funder("a", stages=["senior", "senior"]))
    with pytest.raises(ValidationError):
        pack(funder("a", sector="bank"))
    with pytest.raises(ValidationError):
        pack(funder("a", fields="all"))


def test_funding_in_every_plan_takes_applications_and_an_automatic_award_has_no_dates():
    with pytest.raises(ValidationError, match="a funder in every plan takes applications directly"):
        pack(funder("a", every_plan=True, applying="via_university"))
    with pytest.raises(ValidationError, match="an automatic award has no application windows"):
        pack(funder("a", applying="automatic", applications=windows({"intake": 2027, "closes": "2026-10-31"})))


def test_covers_and_obligations_cite_known_sources():
    with pytest.raises(ValidationError, match="a: covers cites unknown source 'missing'"):
        pack(funder("a", covers={"items": ["Tuition"], "source": "missing"}))
    with pytest.raises(ValidationError, match="a: obligations cites unknown source 'missing'"):
        pack(funder("a", obligations={"items": ["Work a year for every year funded."], "source": "missing"}))


def test_seen_is_only_for_a_page_without_an_opening_date():
    seen = {"status": "open", "checked": "2026-10-11"}
    with pytest.raises(ValidationError, match="'seen' is only for a page that gives no opening date"):
        Window.model_validate({"intake": 2027, "source": "f", "opens": "2026-09-01", "seen": seen})
    with pytest.raises(ValidationError, match="seen open after its closing date"):
        Window.model_validate({"intake": 2027, "source": "f", "closes": "2026-09-30", "seen": seen})


def test_every_field_has_words_to_show():
    assert all(label and label[0].isupper() for label in FIELDS.values())
    assert FIELDS["disaster_and_fire"] == "Disaster management and fire"  # a funder's field no programme has yet


# ------------------------------------------------- a page that says open or closed


def _one(*items: dict) -> FundingPack:
    return pack(funder("a", applications=windows(*items)))


def test_a_page_that_says_closed_without_dates_is_closed():
    funding = _one({"intake": 2027, "seen": {"status": "closed", "checked": "2026-10-11"}})
    c = card(funding, funding.funders[0], TODAY)
    assert c.status == CLOSED
    assert c.lines == ["Closed: A's own page said so on Sun 11 Oct 2026.", "Funding for 2028: A hasn't published these dates yet."]


def test_open_without_dates_is_believed_for_a_while_then_checked():
    funding = _one({"intake": 2027, "seen": {"status": "open", "checked": "2026-10-11"}})
    fresh = card(funding, funding.funders[0], date(2026, 10, 25))
    assert (fresh.status, fresh.lines) == (
        OPEN, ["Open: A's own page said so on Sun 11 Oct 2026. The closing date isn't published, so apply soon."]
    )
    stale = card(funding, funding.funders[0], date(2026, 10, 26))  # 15 days on (config: 14)
    assert (stale.status, stale.lines) == (
        CHECK, ["A's own page said applications were open on Sun 11 Oct 2026. Check that they still are."]
    )


def test_seen_open_with_a_closing_date_is_open_not_a_date_to_check():
    funding = _one({"intake": 2027, "closes": "2026-10-20", "seen": {"status": "open", "checked": "2026-10-11"}})
    c = card(funding, funding.funders[0], TODAY)
    assert (c.status, c.days, c.lines[0]) == (CLOSING_SOON, 9, "Open now. Closes on Tue 20 Oct 2026 (in 9 days).")
    unseen = _one({"intake": 2027, "closes": "2026-10-20"})
    assert card(unseen, unseen.funders[0], TODAY).status == CHECK  # nobody saw it open


def test_what_a_page_said_counts_only_from_the_day_we_read_it():
    funding = _one({"intake": 2027, "seen": {"status": "closed", "checked": "2026-10-11"}})
    c = card(funding, funding.funders[0], date(2026, 10, 10))
    assert (c.status, c.lines) == (NOT_PUBLISHED, ["A hasn't published these dates yet."])


def test_a_funder_that_closed_before_its_closing_date_is_closed():
    funding = _one({"intake": 2027, "closes": "2026-10-31", "seen": {"status": "closed", "checked": "2026-10-11"}})
    c = card(funding, funding.funders[0], TODAY)
    assert (c.status, c.lines[0]) == (CLOSED, "Closed: A's own page said so on Sun 11 Oct 2026.")


def test_a_closed_card_says_what_is_known_about_the_next_round():
    funding = _one(
        {"intake": 2027, "seen": {"status": "closed", "checked": "2026-10-11"}},
        {"intake": 2028, "note": "A says applications for 2028 open in October 2027."},
    )
    assert card(funding, funding.funders[0], TODAY).lines == [
        "Closed: A's own page said so on Sun 11 Oct 2026.",
        "Funding for 2028: A hasn't published these dates yet.",
        "A says applications for 2028 open in October 2027.",
    ]


# ----------------------------------------------------------- the list and its order


def test_open_first_soonest_closing_first_then_upcoming_then_no_dates_then_closed():
    found = cards(pack(*LIST), TODAY)
    assert [(c.funder.id, c.status) for c in found] == [
        ("soon", CLOSING_SOON),
        ("open", OPEN),
        ("later", OPENS_LATER),
        ("auto", AUTOMATIC),
        ("campus", VIA_UNIVERSITY),
        ("loan", NOT_PUBLISHED),
        ("quiet", NOT_PUBLISHED),
        ("closed", CLOSED),
    ]
    auto, campus = found[3], found[4]
    assert (auto.label, auto.window) == ("No application needed", None)
    assert auto.lines == ["There's no application: it's paid to students who qualify."]
    assert campus.label == "Apply through the university"
    assert campus.lines == ["You apply through the university, not to the funder directly."]
    assert (found[0].url, found[0].source_url, found[0].days) == ("https://example.org/apply", "https://example.org/fund", 9)


def test_the_counts_a_list_starts_with():
    c = counts(cards(pack(*LIST), TODAY))
    assert (c.total, c.open_now, c.closing_soon) == (8, 2, 1)
    assert c.line == "8 funding options: 2 open now, 1 closing soon."
    assert counts([]).line == "0 funding options: 0 open now."


def test_filters_by_field_status_kind_stage_and_university():
    p = pack(*LIST)

    def ids(**filters):
        return [c.funder.id for c in cards(p, TODAY, **filters)]

    # A field's own funders come before those open to any field, within each status.
    assert ids(fields=["engineering"]) == ["soon", "later", "auto", "campus", "loan", "quiet", "closed"]
    assert ids(fields=["engineering", "accounting"])[:2] == ["soon", "open"]
    assert ids(status="open") == ["soon", "open"]
    assert ids(status="closing_soon") == ["soon"]
    assert ids(status="upcoming") == ["later"]
    assert ids(status="automatic") == ["auto"] and ids(status="via_university") == ["campus"]
    assert ids(status="not_published") == ["loan", "quiet"] and ids(status="closed") == ["closed"]
    assert ids(kind="loan") == ["loan"] and ids(kind="merit_award") == ["auto"]
    assert ids(stage="senior") == ["open"]
    assert "auto" not in ids(university="tut") and "auto" in ids(university="up")


def test_a_search_by_field_says_why_each_funder_is_there():
    found = {c.funder.id: c.why for c in cards(pack(*LIST), TODAY, fields=["engineering", "computing"])}
    assert found["closed"] == "Funds engineering and computing and IT."
    assert found["soon"] == "Funds engineering."
    assert found["quiet"] == "Open to any field."
    assert all(c.why is None for c in cards(pack(*LIST), TODAY))


def test_a_ruled_out_field_wins():
    assert "loan" not in [c.funder.id for c in cards(pack(*LIST), TODAY, fields=["engineering", "medicine"])]


def test_field_counts_name_only_funders_of_named_fields():
    assert field_counts(pack(*LIST)) == [
        ("accounting", "Accounting", 1),
        ("computing", "Computing and IT", 1),
        ("engineering", "Engineering", 3),
    ]


# ------------------------------------------------------- one funder, and a plan's choices


def test_an_automatic_award_shows_no_dates_fee_or_documents():
    funding = pack(funder("auto", kind="merit_award", applying="automatic", covers={"items": ["R18 000"], "source": "f"},
                          applications={"source": "f", "how": "There's no application."}))
    c, guide = detail(funding, funding.funders[0], TODAY)
    assert c.status == AUTOMATIC and guide.windows == [] and guide.lines == ["There's no application."]
    covers = group(funding, funding.funders[0].covers)
    assert (covers.items, covers.source_url) == (["R18 000"], "https://example.org/fund")
    assert group(funding, None) is None


def test_a_bursary_in_detail_has_every_intake():
    p = pack(*LIST)
    c, guide = detail(p, p.funder("soon"), TODAY)
    assert c.status == CLOSING_SOON and [w.intake for w in guide.windows] == [2027, 2028]
    assert guide.who_can_apply.items == ["South African citizens"]


def test_a_choice_is_shown_first_year_funding_for_its_fields_at_its_university():
    p = pack(NSFAS, *LIST)
    m = matches(p, ["engineering"], "up", TODAY)
    # NSFAS shows with every plan; "open" is for students already studying; "campus" is TUT's only.
    assert [c.funder.id for c in m.cards] == ["soon", "later", "auto", "loan", "quiet"]
    assert (m.count, m.open_now) == (6, 1)  # five shown (config: per_choice), six in all
    assert m.lines == ["6 funding options for engineering, besides NSFAS: 1 open now."]
    assert matches(p, ["engineering", "medicine"], "up", TODAY).count == 5  # the loan rules medicine out
    only_later = matches(pack(*LIST[:2]), ["health_sciences"], "smu", TODAY)  # no NSFAS in this pack
    assert only_later.lines == ["1 funding option for health sciences: none open right now."]


def test_a_choice_with_nothing_to_show_says_where_to_ask():
    m = matches(pack(NSFAS, funder("acc", fields=["accounting"])), ["music"], "up", TODAY)
    assert (m.cards, m.count) == ([], 0)
    assert m.lines == ["We haven't found other funding for music yet, besides NSFAS. Ask the university's funding office."]


def test_a_plan_shows_only_the_funders_meant_for_every_plan():
    uni = University.model_validate({
        "university": "ex", "name": "Example University", "city": "Pretoria", "academic_year": 2027,
        "programmes": [{"id": "a", "name": "A", "fields": ["engineering"]}],
    })
    plan = Plan(goal=Slot(1, "goal", Match("ex", uni.name, "a", "A", MEETS_MINIMUM)), bridge=None, safe=None)
    guide = apply_guide({"ex": uni}, pack(NSFAS, *LIST), plan, TODAY)
    assert [g.id for g in guide.funding] == ["nsfas"]
    assert {d.who for d in guide.deadlines} == {"nsfas"}  # no bursary dates in the plan's own list
    assert guide.notes[-1] == "Funding is a separate application: if you might qualify for NSFAS, apply there as well."
