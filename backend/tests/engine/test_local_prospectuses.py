"""Boundary examples transcribed from the supplied official 2027 tables."""
from campus_engine.matching import assess
from campus_engine.points import compute_points


def test_every_public_university_has_programmes(catalogue):
    assert len(catalogue) == 26
    assert all(u.programmes for u in catalogue.values())
    assert {c.id for c in catalogue["ufh"].campuses} == {"alice", "bisho", "east_london"}


def test_uj_chiropractic_accepts_either_science_not_both(catalogue):
    uni = catalogue["uj"]
    programme = uni.programme("uj_b9c01q")
    marks = dict(english=60, mathematics=50, life_sciences=60, geography=70, history=70, other_language=60)
    assert assess(uni, programme, marks).tier == "reach"
    marks["life_sciences"] = 49
    assert assess(uni, programme, marks).tier == "not_yet"


def test_uwc_accounting_waives_accounting_subject_at_maths_level_five(catalogue):
    uni = catalogue["uwc"]
    programme = uni.programme("uwc_accounting")
    marks = dict(english=60, other_language=50, mathematics=60, life_sciences=70, geography=70, history=70, life_orientation=60)
    assert assess(uni, programme, marks).tier == "reach"
    marks["mathematics"] = 59
    assert assess(uni, programme, marks).tier == "not_yet"
    marks["accounting"] = 60
    assert assess(uni, programme, marks).tier == "reach"


def test_cput_construction_uses_nsc_levels_not_tenths_of_percentages(catalogue):
    uni = catalogue["cput"]
    programme = uni.programme("dip_construction")
    marks = dict(english=59, mathematics=59, physical_sciences=59, life_sciences=59, geography=59, other_language=59, life_orientation=99)
    assert compute_points(marks, programme.points_rules).total == 24
    assert assess(uni, programme, marks).tier == "not_yet"
    marks["mathematics"] = 60
    assert assess(uni, programme, marks).tier != "not_yet"


def test_unknown_points_methods_and_missing_thresholds_do_not_claim_eligibility(catalogue):
    strong = dict(english=90, mathematics=90, physical_sciences=90, life_sciences=90, geography=90, other_language=90, life_orientation=90)
    ufh = catalogue["ufh"]
    assert assess(ufh, ufh.programme("ufh_84040"), strong).tier == "subjects_met"
    assert assess(ufh, ufh.programme("ufh_21526"), strong).tier == "unverified"
    uj = catalogue["uj"]
    assert assess(uj, uj.programme("uj_b34imq"), strong).tier == "subjects_met"


def test_imports_stay_drafts_and_do_not_change_existing_human_signoff(catalogue):
    assert catalogue["smu"].release
    for key in ("uj", "uwc", "ufh", "cput", "wits"):
        uni = catalogue[key]
        assert not uni.release
        fresh = [s for s in uni.sources if s.retrieved and s.retrieved.isoformat() == "2026-10-24"]
        assert fresh
        assert all(s.last_verified is None and not s.human_verified for s in fresh)
