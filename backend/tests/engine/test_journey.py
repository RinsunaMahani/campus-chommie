"""
First steps after acceptance, on today's date: each step's status either side of its dates, which
intakes show, first-years' own dates, campuses, dates not published or not verified, last year's
dates as a guide, and NSFAS at registration. Fictional packs, so the tests keep their meaning when
real dates change.
"""
from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from campus_engine.journey import (
    AHEAD,
    DONE,
    NOT_PUBLISHED,
    NOT_VERIFIED,
    NOW,
    WHEN_OFFERED,
    first_steps,
    intakes,
)
from campus_engine.schemas import FundingPack, University

SOURCES = [
    {"id": "s", "url": "https://example.org/calendar", "publisher": "Example University"},
    {"id": "a", "url": "https://example.org/apply", "publisher": "Example University"},
]

CALENDAR_2027 = [
    {"period": "registration", "name": "Returning students register", "start": "2027-01-10", "end": "2027-01-15",
     "who": "returning", "step": "register", "source": "s"},
    {"period": "registration", "name": "Online registration", "start": "2027-01-14", "end": "2027-01-31",
     "step": "register", "source": "s"},
    {"period": "registration", "name": "First-year registration", "start": "2027-01-20", "end": "2027-01-29",
     "who": "first_years", "step": "register", "source": "s"},
    {"period": "orientation", "name": "Orientation", "start": "2027-02-01", "end": "2027-02-05", "campuses": ["north"],
     "who": "first_years", "step": "orientation", "source": "s"},
    {"period": "term", "name": "Semester 1", "start": "2027-02-08", "end": "2027-06-30", "step": "first_lecture",
     "note": "Some programmes start a week later.", "source": "s"},
    {"period": "deadline", "name": "Last day to change modules", "start": "2027-02-26", "source": "s"},
]


def make(calendar: list[dict] | None = None, accepting: dict | None = None) -> University:
    return University.model_validate(
        {
            "university": "ex",
            "name": "Example University",
            "city": "Pretoria",
            "academic_year": 2027,
            "applications": {"accepting": accepting} if accepting else None,
            "campuses": [{"id": "north", "name": "North", "source": "s"}, {"id": "south", "name": "South", "source": "s"}],
            "calendar": CALENDAR_2027 if calendar is None else calendar,
            "sources": SOURCES,
        }
    )


FUNDING = FundingPack.model_validate(
    {
        "funders": [
            {
                "id": "fund", "name": "Example Fund", "short_name": "Fund", "sector": "government",
                "every_plan": True, "fields": "any", "stages": ["first_year"],
                "at_registration": {"text": "If Fund finds you eligible, it confirms your funding once you register.", "source": "f"},
                "applications": {"windows": []},
            }
        ],
        "sources": [{"id": "f", "url": "https://example.org/fund", "publisher": "Example Fund"}],
    }
)


def steps(today: date, intake: int = 2027, **kwargs):
    found = next(fs for fs in first_steps(make(**kwargs), today, FUNDING) if fs.intake == intake)
    return {s.key: s for s in found.steps}, found


def test_four_steps_in_order_with_their_dates():
    by_key, found = steps(date(2026, 10, 10))
    assert list(by_key) == ["accept", "register", "orientation", "first_lecture"]
    assert found.notes == []
    register = by_key["register"]
    assert (register.status, register.starts, register.ends, register.days) == (AHEAD, date(2027, 1, 20), date(2027, 1, 29), 102)
    assert register.lines[0] == "First-year registration: Wed 20 to Fri 29 Jan 2027 (in 102 days)."
    assert register.source_urls == ["https://example.org/calendar", "https://example.org/fund"]


def test_first_years_own_dates_win_and_returning_students_dates_never_show():
    register = steps(date(2026, 10, 10))[0]["register"]
    assert all("Online registration" not in line and "Returning" not in line for line in register.lines)
    without_own = [e for e in CALENDAR_2027 if e["name"] != "First-year registration"]
    register = steps(date(2026, 10, 10), calendar=without_own)[0]["register"]
    assert register.lines[0].startswith("Online registration: Thu 14 to Sun 31 Jan 2027")


def test_campuses_are_named():
    orientation = steps(date(2026, 10, 10))[0]["orientation"]
    assert orientation.lines == ["Orientation (North): Mon 1 to Fri 5 Feb 2027 (in 114 days)."]


def test_the_first_lecture_is_one_day_with_its_note():
    first = steps(date(2026, 10, 10))[0]["first_lecture"]
    assert (first.starts, first.ends) == (date(2027, 2, 8), date(2027, 2, 8))
    assert first.lines == ["Lectures start on Mon 8 Feb 2027 (in 121 days).", "Some programmes start a week later."]


@pytest.mark.parametrize(
    "today, expected",
    [
        (date(2027, 1, 19), AHEAD),
        (date(2027, 1, 20), NOW),
        (date(2027, 1, 29), NOW),
        (date(2027, 1, 30), DONE),
    ],
)
def test_a_steps_status_either_side_of_its_dates(today, expected):
    assert steps(today)[0]["register"].status == expected


def test_registering_says_what_national_funders_do_then():
    register = steps(date(2026, 10, 10))[0]["register"]
    assert register.lines[-1] == "If Fund finds you eligible, it confirms your funding once you register."


def test_only_funding_shown_with_every_plan_speaks_at_registration():
    bursary = {
        "id": "bursary", "name": "A bursary", "short_name": "Bursary", "sector": "company", "fields": ["law"],
        "stages": ["first_year"], "applications": {"windows": []},
        "at_registration": {"text": "Bursary pays once you register.", "source": "f"},
    }
    data = FUNDING.model_dump(mode="json")
    funding = FundingPack.model_validate(dict(data, funders=[*data["funders"], bursary]))
    found = next(fs for fs in first_steps(make(), date(2026, 10, 10), funding) if fs.intake == 2027)
    register = {s.key: s for s in found.steps}["register"]
    assert "Bursary pays once you register." not in register.lines


def test_accepting_an_offer():
    accept = steps(date(2026, 10, 10))[0]["accept"]
    assert (accept.status, accept.lines) == (NOT_VERIFIED, ["How to accept an offer: not verified yet."])
    accepting = {"text": "Pay the confirmation fee within three days.", "source": "a"}
    accept = steps(date(2026, 10, 10), accepting=accepting)[0]["accept"]
    assert (accept.status, accept.label) == (WHEN_OFFERED, "When your offer comes")
    assert accept.lines == ["Pay the confirmation fee within three days."]
    assert accept.source_urls == ["https://example.org/apply"]


def test_this_years_intake_stays_until_its_last_step_is_over():
    uni = make()
    assert intakes(uni, date(2026, 10, 10)) == [2027]
    assert intakes(uni, date(2027, 2, 8)) == [2027, 2028]  # the first lecture is today
    assert intakes(uni, date(2027, 2, 9)) == [2028]  # the term runs on, but every first step is over


def test_a_year_nobody_has_published_offers_last_years_dates_as_last_years():
    by_key, found = steps(date(2027, 3, 1), intake=2028)
    assert found.notes == ["Example University hasn't published its 2028 dates yet."]
    register = by_key["register"]
    assert register.status == NOT_PUBLISHED and register.label == "Not published yet"
    assert register.lines[:2] == ["Not published yet.", "For 2027: First-year registration: Wed 20 to Fri 29 Jan 2027."]
    assert by_key["first_lecture"].lines[1] == "For 2027: Lectures start on Mon 8 Feb 2027."


def test_a_step_missing_from_a_published_year_is_not_verified():
    without_orientation = [e for e in CALENDAR_2027 if e["period"] != "orientation"]
    by_key, found = steps(date(2026, 10, 10), calendar=without_orientation)
    assert found.notes == []
    assert (by_key["orientation"].status, by_key["orientation"].lines) == (NOT_VERIFIED, ["Not verified yet."])


@pytest.mark.parametrize(
    "change, problem",
    [
        ({"calendar": [dict(CALENDAR_2027[1], end="2027-01-01")]}, "ends before it starts"),
        ({"calendar": [dict(CALENDAR_2027[3], campuses=["east"])]}, "names unknown campus 'east'"),
        ({"calendar": [dict(CALENDAR_2027[1], source="missing")]}, "calendar 'Online registration' cites unknown source"),
        ({"calendar": [dict(CALENDAR_2027[1], period="holiday")]}, "period"),
        ({"campuses": [{"id": "north", "name": "North", "source": "s"}] * 2}, "campus ids must be unique"),
        ({"support_services": [{"kind": "crisis", "name": "Line", "contact": "0800", "campuses": ["east"], "source": "s"}]},
         "names unknown campus 'east'"),
        ({"support_services": [{"kind": "astrology", "name": "Line", "contact": "0800", "source": "s"}]}, "kind"),
        ({"funding_cycles": [{"funder": "university", "kind": "fee_due", "name": "Fees", "when": "2027-03-31",
                              "source": "missing"}]}, "funding date 'Fees' cites unknown source"),
        ({"funding_cycles": [{"funder": "university", "kind": "fee_due", "name": "Fees", "on": "2027-03-31",
                              "source": "s"}]}, "when"),
        ({"cheap_things": [{"name": "Park", "category": "outdoors", "cost_note": "Free", "campuses": ["east"],
                            "source": "s"}]}, "names unknown campus 'east'"),
    ],
)
def test_broken_sections_fail_validation(change, problem):
    pack = {
        "university": "ex", "name": "Example University", "city": "Pretoria", "academic_year": 2027,
        "campuses": [{"id": "north", "name": "North", "source": "s"}], "sources": SOURCES, **change,
    }
    with pytest.raises(ValidationError, match=problem):
        University.model_validate(pack)
