"""
"How to apply" on today's date: each status on either side of every date, programmes with their own
closing date, dates nobody has published, last year's dates as a guide, the guides, the deadlines and
the pack rules. Fictional packs, so the tests keep their meaning when real dates change.
"""
from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from campus_engine.applications import (
    CHECK,
    CLOSED,
    CLOSING_SOON,
    LATE_AHEAD,
    LATE_OPEN,
    NOT_PUBLISHED,
    OPEN,
    OPENS_LATER,
    apply_guide,
    funder_guide,
    intakes,
    programme_windows,
    university_guide,
    window_status,
)
from campus_engine.bridges import Plan, Slot
from campus_engine.matching import MEETS_MINIMUM, Match
from campus_engine.schemas import FundingPack, University

SOURCES = [{"id": "s", "url": "https://example.org/apply", "publisher": "Example University"}]

#: The usual window: open 1 Apr to 30 Sep 2026, programme b closes on 15 Jun, late applications in January.
WINDOW = {
    "intake": 2027,
    "source": "s",
    "opens": "2026-04-01",
    "closes": "2026-09-30",
    "programme_closes": [{"closes": "2026-06-15", "programmes": ["b"]}],
    "late": {"opens": "2027-01-14", "closes": "2027-01-22", "note": "Online only.", "source": "s"},
}

#: Opens 1 Apr 2027; programmes close on one of three dates, without saying which.
UNSURE = {"intake": 2028, "source": "s", "opens": "2027-04-01", "closes_one_of": ["2027-09-30", "2027-06-15", "2027-07-31"]}


def make(windows: list[dict] | None = None, max_choices: int | None = None, **apps) -> University:
    applications = {"windows": windows if windows is not None else [WINDOW], **apps}
    if any(k in apps for k in ("url", "how", "fee_cents", "fee_note", "contact")):
        applications.setdefault("source", "s")
    return University.model_validate(
        {
            "university": "ex",
            "name": "Example University",
            "city": "Pretoria",
            "academic_year": 2027,
            "max_choices": max_choices,
            "applications": applications,
            "programmes": [{"id": "a", "name": "Programme A"}, {"id": "b", "name": "Programme B"}],
            "sources": SOURCES,
        }
    )


def status(today: date, programme: str = "a", windows: list[dict] | None = None, intake: int = 2027):
    return next(s for s in programme_windows(make(windows), programme, today) if s.intake == intake)


@pytest.mark.parametrize(
    "today, expected",
    [
        (date(2026, 3, 31), OPENS_LATER),
        (date(2026, 4, 1), OPEN),
        (date(2026, 9, 15), OPEN),  # in 15 days; "closing soon" starts at 14
        (date(2026, 9, 16), CLOSING_SOON),
        (date(2026, 9, 30), CLOSING_SOON),
        (date(2026, 10, 1), LATE_AHEAD),
        (date(2027, 1, 13), LATE_AHEAD),
        (date(2027, 1, 14), LATE_OPEN),
        (date(2027, 1, 22), LATE_OPEN),
    ],
)
def test_each_status_on_either_side_of_each_date(today, expected):
    assert status(today).status == expected


def test_open_says_when_it_closes_and_how_long_is_left():
    s = status(date(2026, 9, 16))
    assert s.lines[0] == "Open now. Closes on Wed 30 Sep 2026 (in 14 days)."
    assert (s.next_date, s.days, s.label) == (date(2026, 9, 30), 14, "Closing soon")
    assert s.source_url == "https://example.org/apply"


def test_not_open_yet_gives_both_dates():
    s = status(date(2026, 3, 31))
    assert s.lines[:2] == ["Opens on Wed 1 Apr 2026 (tomorrow).", "Closes on Wed 30 Sep 2026."]
    assert s.days == 1


def test_late_windows_say_their_dates_and_note():
    ahead = status(date(2026, 10, 10))
    assert ahead.lines == [
        "Closed on Wed 30 Sep 2026.",
        "Late applications: Thu 14 to Fri 22 Jan 2027 (in 96 days).",
        "Online only.",
    ]
    open_now = status(date(2027, 1, 22))
    assert open_now.lines[0] == "The closing date has passed, but late applications are open until Fri 22 Jan 2027 (today)."


def test_this_years_intake_drops_out_once_its_late_window_ends():
    uni = make()
    assert intakes(date(2026, 10, 10), uni.applications.windows) == [2027, 2028]
    assert intakes(date(2027, 1, 22), uni.applications.windows) == [2027, 2028, 2029]
    assert intakes(date(2027, 1, 23), uni.applications.windows) == [2028, 2029]


def test_a_programme_with_its_own_closing_date():
    today = date(2026, 6, 16)
    assert status(today, "a").status == OPEN
    b = status(today, "b")
    assert b.status == LATE_AHEAD and b.closes == date(2026, 6, 15)
    assert b.lines[0] == "Closed on Mon 15 Jun 2026."


def test_no_late_applications_is_said_only_when_the_university_says_it():
    no_late = dict(WINDOW, late=None, no_late_applications=True)
    s = status(date(2026, 10, 10), windows=[no_late])
    assert s.status == CLOSED and s.lines == ["Closed on Wed 30 Sep 2026.", "No late applications."]
    silent = dict(WINDOW, late=None)
    assert status(date(2026, 10, 10), windows=[silent]).lines == ["Closed on Wed 30 Sep 2026."]


def test_a_closing_time_is_shown():
    timed = dict(WINDOW, closing_time="23:59")
    assert status(date(2026, 9, 1), windows=[timed]).lines[0] == "Open now. Closes on Wed 30 Sep 2026 at 23:59 (in 29 days)."


def test_an_unknown_opening_date_means_check_rather_than_open():
    s = status(date(2026, 5, 1), windows=[dict(WINDOW, opens=None)])
    assert s.status == CHECK and s.label == "Check the dates"
    assert "We haven't verified when applications open" in s.lines[0]


@pytest.mark.parametrize(
    "today, expected, line",
    [
        (date(2027, 3, 1), OPENS_LATER, "apply by Tue 15 Jun 2027 to be safe."),
        (date(2027, 5, 1), OPEN, "apply by Tue 15 Jun 2027 to be safe (in 45 days)."),
        (date(2027, 6, 20), CHECK, "This programme may already have closed on Tue 15 Jun 2027."),
        (date(2027, 10, 1), CLOSED, "Closed: the last of its possible closing dates was Thu 30 Sep 2027."),
    ],
)
def test_dates_named_without_saying_which_programme_closes_when(today, expected, line):
    s = status(today, windows=[WINDOW, UNSURE], intake=2028)
    assert s.status == expected
    assert any(line in text for text in s.lines)
    assert s.closes is None and s.closes_one_of == [date(2027, 6, 15), date(2027, 7, 31), date(2027, 9, 30)]


def test_unpublished_dates_are_never_guessed_but_last_years_are_given_as_last_years():
    s = status(date(2026, 10, 10), intake=2028)
    assert s.status == NOT_PUBLISHED and s.label == "Dates not published yet"
    assert s.lines == [
        "Example University hasn't published these dates yet.",
        "To start in 2027, applications ran from Wed 1 Apr to Wed 30 Sep 2026.",
    ]
    assert s.opens is None and s.closes is None and s.next_date is None
    own = status(date(2026, 10, 10), "b", intake=2028)
    assert own.lines[1] == "To start in 2027, applications for this programme closed on Mon 15 Jun 2026."


def test_last_years_dates_wait_until_they_have_passed():
    s = status(date(2026, 5, 1), intake=2028)
    assert s.lines == ["Example University hasn't published these dates yet."]


def test_after_its_late_window_an_intake_is_closed():
    window = make().applications.windows[0]
    s = window_status(window, 2027, date(2027, 1, 23), who="Example University", heading="To start in 2027", url_for=lambda _: None)
    assert s.status == CLOSED and s.lines == ["Closed. Late applications closed on Fri 22 Jan 2027."]


def test_an_opening_date_without_a_closing_date():
    window = {"intake": 2027, "source": "s", "opens": "2026-11-01", "note": "A programme may close once it's full."}
    before = status(date(2026, 10, 10), windows=[window])
    assert before.status == OPENS_LATER
    assert before.lines == [
        "Opens on Sun 1 Nov 2026 (in 22 days).",
        "The closing date isn't published yet.",
        "A programme may close once it's full.",
    ]
    after = status(date(2026, 11, 2), windows=[window])
    assert after.status == OPEN and after.lines[0] == "Open now. The closing date isn't published yet, so apply early."
    assert after.next_date is None


def test_only_a_late_window_published():
    window = {"intake": 2027, "source": "s", "late": {"opens": "2026-12-14", "closes": "2027-01-22", "source": "s"}}
    s = status(date(2026, 10, 10), windows=[window])
    assert s.status == NOT_PUBLISHED
    assert s.lines == [
        "Example University hasn't published these dates yet.",
        "Late applications: Mon 14 Dec 2026 to Fri 22 Jan 2027 (in 65 days).",
    ]


def test_a_university_without_an_applications_section_publishes_nothing():
    uni = make()
    uni = uni.model_copy(update={"applications": None})
    statuses = programme_windows(uni, "a", date(2026, 10, 10))
    assert [s.status for s in statuses] == [NOT_PUBLISHED, NOT_PUBLISHED]


def test_the_guide_says_what_is_not_verified_yet():
    guide = university_guide(make())
    assert guide.lines == [
        "Where to apply: not verified yet.",
        "Application fee: not verified yet.",
        "Documents: not verified yet.",
        "How many programmes you can list on one application: not verified yet.",
    ]


def test_the_guide_with_every_fact():
    uni = make(
        max_choices=2,
        url="https://example.org/apply",
        how="Apply online.",
        fee_cents=24000,
        fee_note="Not refundable.",
        contact="012 000 0000",
        documents={"items": ["A certified copy of your ID"], "source": "s"},
        after=[{"text": "Check your status online.", "source": "s"}],
    )
    guide = university_guide(uni)
    assert guide.lines == [
        "Where to apply: https://example.org/apply",
        "Apply online.",
        "Application fee: R240.",
        "Not refundable.",
        "You can list 2 programmes on one application.",
        "Questions: 012 000 0000",
    ]
    assert guide.documents.items == ["A certified copy of your ID"]
    assert guide.documents.source_url == "https://example.org/apply"
    assert [(a.text, a.source_url) for a in guide.after] == [("Check your status online.", "https://example.org/apply")]


FUNDING = {
    "funders": [
        {
            "id": "fund",
            "name": "Example Fund",
            "short_name": "Fund",
            "who_can_apply": {"items": ["South African citizens"], "source": "f"},
            "warnings": {"items": ["Never pay anyone to apply."], "source": "f"},
            "applications": {
                "source": "f",
                "url": "https://example.org/fund",
                "fee_cents": 0,
                "windows": [
                    {
                        "intake": 2027, "source": "f", "opens": "2026-09-18", "closes": "2026-10-31",
                        "closing_time": "23:59", "no_late_applications": True,
                    }
                ],
            },
        }
    ],
    "sources": [{"id": "f", "url": "https://example.org/fund", "publisher": "Example Fund"}],
}


def test_a_funders_guide_counts_down_to_its_closing_date():
    pack = FundingPack.model_validate(FUNDING)
    guide = funder_guide(pack, pack.funders[0], date(2026, 10, 10))
    assert "Applying is free." in guide.lines
    first, second = guide.windows
    assert (first.heading, first.status, first.days) == ("Funding for 2027", OPEN, 21)
    assert first.lines == ["Open now. Closes on Sat 31 Oct 2026 at 23:59 (in 21 days).", "No late applications."]
    assert second.lines == ["Fund hasn't published these dates yet."]  # 2027's dates aren't over yet
    later = funder_guide(pack, pack.funders[0], date(2026, 11, 1)).windows[1]
    assert later.lines == [
        "Fund hasn't published these dates yet.",
        "For 2027 funding, applications ran from Fri 18 Sep to Sat 31 Oct 2026.",
    ]
    assert guide.who_can_apply.items == ["South African citizens"]
    assert guide.warnings.source_url == "https://example.org/fund"


def _plan(uni: University, *programmes: str) -> Plan:
    def slot(n: int, pid: str) -> Slot:
        p = uni.programme(pid)
        return Slot(n, "goal" if n == 1 else "safe", Match(uni.university, uni.name, p.id, p.name, MEETS_MINIMUM))

    goal, *rest = programmes
    return Plan(goal=slot(1, goal), bridge=None, safe=slot(3, rest[0]) if rest else None)


def test_a_plans_deadlines_come_soonest_first_without_repeats_or_past_dates():
    uni = make(windows=[WINDOW, UNSURE])
    pack = FundingPack.model_validate(FUNDING)
    guide = apply_guide({"ex": uni}, pack, _plan(uni, "a", "b"), date(2026, 10, 10))
    maybe = "applications to start in 2028 may close on this date, so apply by then to be safe."
    assert [(d.on.isoformat(), d.text) for d in guide.deadlines] == [
        ("2026-10-31", "Fund: applications for 2027 funding close at 23:59."),
        ("2027-01-14", "Example University: late applications to start in 2027 open."),
        ("2027-01-22", "Example University: late applications to start in 2027 close."),
        ("2027-04-01", "Example University: applications to start in 2028 open."),
        ("2027-06-15", f"Example University, Programme A: {maybe}"),
        ("2027-06-15", f"Example University, Programme B: {maybe}"),
    ]
    assert guide.deadlines[0].days == 21 and guide.deadlines[0].who == "fund"
    assert [g.id for g in guide.universities] == ["ex"]
    assert set(guide.windows) == {("ex", "a"), ("ex", "b")}
    assert guide.notes[-1] == "Funding is a separate application: if you might qualify for Fund, apply there as well."


def test_a_programmes_own_closing_date_is_its_own_deadline():
    uni = make()
    guide = apply_guide({"ex": uni}, None, _plan(uni, "b", "a"), date(2026, 5, 1))
    texts = [d.text for d in guide.deadlines]
    assert "Example University, Programme B: applications to start in 2027 close." in texts
    assert "Example University: applications to start in 2027 close." in texts
    own = next(d for d in guide.deadlines if d.programme_id == "b")
    assert own.on == date(2026, 6, 15)
    assert guide.funding == []


@pytest.mark.parametrize(
    "window, problem",
    [
        (dict(WINDOW, closes="2026-03-01"), "a closing date is before the opening date"),
        (dict(WINDOW, programme_closes=[{"closes": "2026-06-15", "programmes": ["b", "b"]}]), "'b' has more than one closing date"),
        (dict(WINDOW, late=dict(WINDOW["late"], opens="2026-09-01")), "late applications open before the last closing date"),
        (dict(WINDOW, no_late_applications=True), "late applications are both published and ruled out"),
        (dict(WINDOW, late=dict(WINDOW["late"], closes="2027-01-01")), "the late window closes before it opens"),
        (dict(WINDOW, closing_time="24:00"), "closing_time"),
        (dict(WINDOW, closing_time=1439), "closing_time"),  # YAML reads an unquoted 23:59 as 1439
        (dict(WINDOW, intake=1999), "intake"),
    ],
)
def test_impossible_windows_fail_validation(window, problem):
    with pytest.raises(ValidationError, match=problem):
        make(windows=[window])


@pytest.mark.parametrize(
    "change, problem",
    [
        (
            {"windows": [dict(WINDOW, programme_closes=[{"closes": "2026-06-15", "programmes": ["zz"]}])]},
            "closing date for unknown programme 'zz'",
        ),
        ({"windows": [dict(WINDOW, source="missing")]}, "window 2027 cites unknown source 'missing'"),
        ({"windows": [WINDOW, WINDOW]}, "one window per intake"),
        ({"url": "http://example.org/apply"}, "url must start with https://"),
        ({"fee_cents": -1}, "fee_cents"),
        ({"documents": {"items": [], "source": "s"}}, "items"),
        ({"after": [{"text": "x", "source": "missing"}]}, "applications after cites unknown source 'missing'"),
    ],
)
def test_broken_applications_fail_validation(change, problem):
    with pytest.raises(ValidationError, match=problem):
        make(**change)


def test_facts_without_a_source_fail_validation():
    with pytest.raises(ValidationError, match="url, how, fee and contact need a source"):
        University.model_validate(
            {
                "university": "ex", "name": "Example University", "city": "Pretoria", "academic_year": 2027,
                "applications": {"fee_cents": 30000}, "sources": SOURCES,
            }
        )


def test_a_funder_has_no_programme_closing_dates():
    funder = FUNDING["funders"][0]
    applications = dict(funder["applications"], windows=[UNSURE | {"source": "f"}])
    broken = {**FUNDING, "funders": [dict(funder, applications=applications)]}
    with pytest.raises(ValidationError, match="no programmes to close separately"):
        FundingPack.model_validate(broken)


def test_a_funder_citing_a_missing_source_fails():
    broken = {**FUNDING, "funders": [dict(FUNDING["funders"][0], tips={"items": ["x"], "source": "missing"})]}
    with pytest.raises(ValidationError, match="fund: tips cites unknown source 'missing'"):
        FundingPack.model_validate(broken)

def test_a_funding_pack_needs_unique_ids():
    twice = {**FUNDING, "funders": FUNDING["funders"] * 2, "sources": FUNDING["sources"] * 2}
    with pytest.raises(ValidationError) as exc:
        FundingPack.model_validate(twice)
    assert "funder ids must be unique" in str(exc.value) and "source ids must be unique" in str(exc.value)


def test_asking_for_an_unknown_funder_is_a_key_error():
    pack = FundingPack.model_validate(FUNDING)
    assert pack.funder("fund").short_name == "Fund"
    with pytest.raises(KeyError):
        pack.funder("nope")
