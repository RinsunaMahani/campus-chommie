"""Colleges: search, one college's status in words, and "is this college registered?", on a small pack
whose answers don't change as DHET's registers do; then the real pack's shape."""
from __future__ import annotations

import pytest

from campus_engine import colleges as e
from campus_engine.catalogue import load_colleges
from campus_engine.schemas import CollegesPack

SRC = [{"id": "s-reg", "url": "https://www.dhet.gov.za/r.pdf", "publisher": "DHET"}]


def _pack(**extra) -> CollegesPack:
    data = {
        "colleges": [
            {"id": "tshwane-north", "name": "Tshwane North TVET College", "kind": "tvet", "status": "public",
             "provinces": ["Gauteng"], "website": "www.tnc.edu.za", "source": "s-reg"},
            {"id": "acme-college", "name": "Acme College (Pty) Ltd", "kind": "private_college", "status": "registered",
             "registration_number": "2010/FE07/001", "provinces": ["Gauteng"],
             "qualifications": ["National Certificate (Vocational) L2-L4 Office Administration"], "source": "s-reg"},
            {"id": "tshwane-commerce", "name": "Tshwane College of Commerce (Pty) Ltd", "kind": "private_college",
             "status": "cancelled", "registration_number": "2010/FE07/039", "source": "s-reg"},
            {"id": "beta-institute", "name": "Beta Institute NPC", "kind": "private_higher_education",
             "status": "provisionally_registered", "registration_number": "2026/HE08/001", "source": "s-reg"},
            {"id": "gamma-school", "name": "Gamma School", "kind": "private_higher_education",
             "status": "registered", "source": "s-reg"},
        ],
        "occupational": [{"saqa_id": "91761", "name": "Occupational Certificate: Electrician",
                          "nsfas_allowances": False, "colleges": ["tshwane-north"], "source": "s-reg"}],
        "unregistered": [{"id": "barkley-university", "name": "Barkley University", "source": "s-reg"}],
        "sources": SRC,
        **extra,
    }
    return CollegesPack.model_validate(data)


def test_a_search_matches_names_word_by_word_and_says_what_it_found():
    found = e.search(_pack(), query="tshwane")
    assert [c.college.id for c in found.cards] == ["tshwane-north", "tshwane-commerce"]  # public before cancelled
    assert found.lines == ["2 colleges: 1 public, 1 cancelled."]
    assert e.search(_pack(), query="tsh coll comm").cards[0].college.id == "tshwane-commerce"


def test_a_search_finds_a_registration_number_and_a_qualification():
    assert [c.college.id for c in e.search(_pack(), query="2010 / fe07 / 001").cards] == ["acme-college"]
    assert [c.college.id for c in e.search(_pack(), query="electrician").cards] == ["tshwane-north"]
    assert [c.college.id for c in e.search(_pack(), query="office admin").cards] == ["acme-college"]


def test_filters_narrow_the_list():
    assert [c.college.id for c in e.search(_pack(), kind="tvet").cards] == ["tshwane-north"]
    assert {c.college.id for c in e.search(_pack(), status="registered").cards} == {"acme-college", "gamma-school"}
    assert e.search(_pack(), province="Limpopo").lines == ["No colleges to show."]
    assert e.search(_pack(), query="hogwarts").lines == ["No college in DHET's lists matches “hogwarts”."]


def test_each_status_reads_in_plain_words():
    p = _pack()
    lines = {c.college.id: c.lines for c in e.search(p).cards}
    assert lines["tshwane-north"] == [
        "Tshwane North TVET College is a public TVET college, under the Department of Higher Education and Training."]
    assert lines["acme-college"] == [
        "Acme College (Pty) Ltd is registered with the Department of Higher Education and Training "
        "(registration number 2010/FE07/001).",
        "It is registered for 1 qualification: it may offer only those, at the sites listed.",
    ]
    assert lines["tshwane-commerce"][0].endswith("will not sit for examinations nor be certificated.")
    assert "provisionally registered (registration number 2026/HE08/001)" in lines["beta-institute"][0]
    assert lines["gamma-school"][1] == "The register shows no registration number for it."


@pytest.mark.parametrize("query, verdict", [
    ("Acme College", "registered"),
    ("2010/FE07/001", "registered"),
    ("tshwane north", "public"),
    ("beta institute", "provisionally_registered"),
    ("tshwane college of commerce", "cancelled"),
    ("barkley", "bogus"),
    ("hogwarts", "not_found"),
    ("tshwane", "several"),  # a public college and a cancelled one: neither borrows the other's status
])
def test_the_registration_check(query, verdict):
    assert e.check(_pack(), query).verdict == verdict


def test_a_bogus_college_is_named_as_dhet_names_it():
    found = e.check(_pack(), "Barkley University")
    assert found.label == "Illegal (bogus) college"
    assert found.lines == ["DHET lists “Barkley University” as an illegal (bogus) college: it is not registered, "
                           "so its qualifications are not recognised."]


def test_not_found_never_means_bogus():
    found = e.check(_pack(), "Hogwarts")
    assert found.lines[1].startswith("Not being in these lists doesn't make a college bogus")
    assert (found.colleges, found.unregistered) == ([], [])


def test_several_matches_list_the_most_serious_first_and_say_so():
    found = e.check(_pack(), "tshwane")
    assert [c.id for c in found.colleges] == ["tshwane-commerce", "tshwane-north"]
    assert found.lines[-1] == "2 names matched: check which one you mean."


def test_a_check_shows_at_most_the_configured_number_of_matches():
    found = e.check(_pack(), "tshwane", cfg={"colleges": {"max_matches": 1}})
    assert len(found.colleges) == 1


def test_only_a_public_tvet_college_is_public():
    with pytest.raises(ValueError, match="only a public TVET college"):
        CollegesPack.model_validate({"colleges": [{"id": "x", "name": "X College", "kind": "private_college",
                                                   "status": "public", "source": "s-reg"}], "sources": SRC})


def test_the_pack_refuses_unknown_sources_and_unknown_tvet_colleges():
    with pytest.raises(ValueError, match="unknown source"):
        _pack(sources=[{"id": "other", "url": "https://x.example", "publisher": "X"}])
    with pytest.raises(ValueError, match="unknown TVET colleges"):
        _pack(occupational=[{"saqa_id": "91761", "name": "Electrician", "nsfas_allowances": False,
                             "colleges": ["acme-college"], "source": "s-reg"}])


def test_the_real_pack_loads_and_counts_dhets_lists():
    pack = load_colleges()
    kinds = {(c.kind, c.status) for c in pack.colleges}
    assert {("tvet", "public"), ("private_higher_education", "registered"), ("private_college", "cancelled")} <= kinds
    assert sum(c.kind == "tvet" for c in pack.colleges) == 50
    assert pack.release is False  # an agent draft until a person checks it
    assert all(s.verified_by == "agent draft, needs human check" for s in pack.sources)
    assert len(pack.warning_signs.items) == 11
    # Contact persons' names never become part of a college's name.
    assert not any(" Mr " in c.name or " Mrs " in c.name or " Ms " in c.name for c in pack.colleges)
