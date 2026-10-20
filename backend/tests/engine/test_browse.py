"""Browsing without marks: programmes by university and faculty, and what closes soonest."""
from __future__ import annotations

from datetime import date

from campus_engine import browse
from campus_engine.catalogue import load_catalogue, load_funding
from campus_engine.config import load_config
from campus_engine.funding import cards


def test_programmes_come_by_university_then_faculty_with_unnamed_faculties_last():
    rows = browse.programmes(load_catalogue(), university="up")
    assert rows and all(r.university == "up" for r in rows)
    named = [r.faculty for r in rows if r.faculty]
    assert named == sorted(named, key=str.lower)
    first_unnamed = next((i for i, r in enumerate(rows) if r.faculty is None), len(rows))
    assert all(r.faculty is None for r in rows[first_unnamed:])


def test_a_search_matches_a_programme_or_its_faculty_word_by_word():
    packs = load_catalogue()
    nursing = browse.programmes(packs, query="nursing")
    assert nursing and all("nursing" in (r.name + " " + (r.faculty or "")).lower() for r in nursing)
    assert browse.programmes(packs, query="zzzz no such thing") == []
    assert browse.summary([]) == "No programmes match."


def test_minimum_points_are_shown_only_where_the_pack_has_checked_requirements():
    for r in browse.programmes(load_catalogue()):
        if not r.verified:
            assert r.min_points is None


def test_deadlines_list_whats_open_nearest_first():
    today = date(2026, 10, 20)
    found = browse.deadlines(load_catalogue(), cards(load_funding(), today), today)
    assert found and [d.closes for d in found] == sorted(d.closes for d in found)
    assert all(d.closes >= today and d.days == (d.closes - today).days for d in found)
    assert {d.kind for d in found} == {"university", "funding"}
    uj = next(d for d in found if d.id == "uj")
    assert uj.line == "Applications for 2027 close in 11 days."


def test_deadlines_respect_the_configured_number():
    today = date(2026, 10, 20)
    found = browse.deadlines(load_catalogue(), cards(load_funding(), today), today, cfg={**load_config(), "browse": {"deadlines": 2}})
    assert len(found) == 2


def test_a_universitys_headline_is_where_its_applications_stand_today():
    w = browse.application_headline(load_catalogue()["uj"], date(2026, 10, 20))
    assert w is not None and w.status in {"open", "closing_soon"} and w.closes == date(2026, 10, 31)
