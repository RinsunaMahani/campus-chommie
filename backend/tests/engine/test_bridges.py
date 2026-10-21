from campus_engine.bridges import build_plan
from campus_engine.matching import MEETS_MINIMUM, NOT_YET, REACH
from campus_engine.schemas import University


def test_strong_learner_plan(smu_catalogue, strong_marks):
    plan = build_plan(smu_catalogue, "smu", "mbchb", strong_marks)
    assert plan.goal.match.tier == REACH
    # The unrestricted BSc route comes before the restricted foundation programme.
    assert plan.bridge.match.programme_id == "bsc_y1"
    assert plan.bridge.bridge.guarantee == "considered"
    assert any("Places on this route: 5." in n for n in plan.bridge.notes)
    assert [r.match.programme_id for r in plan.other_routes] == ["mbchb_ecp"]
    assert any(n.startswith("Eligibility:") for n in plan.other_routes[0].notes)
    # Every SMU programme is selective, so slot 3 is honestly labelled as not safe yet, and it
    # is never a programme already shown as a route.
    safe = plan.safe
    assert safe.match.university == "smu" and safe.match.selective
    assert safe.match.programme_id not in {"mbchb", "bsc_y1", "mbchb_ecp"}
    assert safe.notes[0].startswith("Related to MBChB")
    assert any("not a safe choice yet" in n for n in safe.notes)
    assert any("allows 2 choice(s)" in n for n in plan.notes)  # SMU's pack now says two choices


def test_routes_the_learner_cannot_enter_go_last(smu_catalogue, strong_marks):
    marks = dict(strong_marks, mathematics=55)  # level 4: below the foundation year's 5
    plan = build_plan(smu_catalogue, "smu", "mbchb", marks)
    assert plan.goal.match.tier == NOT_YET
    assert plan.bridge.match.programme_id == "bsc_y1"
    assert plan.other_routes[0].match.tier == NOT_YET


def test_no_safe_choice_when_nothing_fits(smu_catalogue):
    weak = {"english": 35, "mathematics": 35, "physical_sciences": 35, "life_sciences": 35, "life_orientation": 35}
    plan = build_plan(smu_catalogue, "smu", "mbchb", weak)
    assert plan.safe is None
    assert any("No related programme" in n for n in plan.notes)


def test_choice_limit_warning(smu_catalogue, strong_marks):
    unknown = {"smu": smu_catalogue["smu"].model_copy(update={"max_choices": None})}
    plan = build_plan(unknown, "smu", "mbchb", strong_marks)
    assert any("Check how many programmes" in n for n in plan.notes)
    plan = build_plan(smu_catalogue, "smu", "mbchb", strong_marks)  # two choices: goal + bridge + slot 3 at SMU
    assert any("allows 2 choice(s)" in n for n in plan.notes)


def test_safe_choice_can_come_from_another_university(smu_catalogue, strong_marks):
    """A related programme without competitive selection elsewhere beats SMU's selective B Rad."""
    other = University.model_validate(
        {
            "university": "example",
            "name": "Example University (fictional, for tests)",
            "city": "Pretoria",
            "academic_year": 2027,
            "points_rules": {
                "source": "s",
                "subjects_counted": 6,
                "life_orientation": "exclude",
                "scale": [{"min_percent": 50, "level": 4}, {"min_percent": 0, "level": 1}],
            },
            "programmes": [
                {
                    "id": "bsc_health",
                    "name": "BSc in Health Sciences",
                    "fields": ["health_sciences"],
                    "requirements": {"source": "s", "min_points": 20, "subject_minimums": {"life_sciences": 4}},
                }
            ],
            "sources": [{"id": "s", "url": "https://example.org", "publisher": "Example"}],
        }
    )
    plan = build_plan(dict(smu_catalogue, example=other), "smu", "mbchb", strong_marks)
    assert plan.bridge.match.programme_id == "bsc_y1"  # bridges stay at the goal's university
    assert (plan.safe.match.university, plan.safe.match.programme_id) == ("example", "bsc_health")
    assert plan.safe.match.tier == MEETS_MINIMUM
    assert not any("not a safe choice yet" in n for n in plan.safe.notes)


def _university(pid, programmes):
    return University.model_validate(
        {
            "university": pid,
            "name": f"{pid.title()} University (fictional, for tests)",
            "city": "Pretoria",
            "academic_year": 2027,
            "points_rules": {"source": "s", "subjects_counted": 6, "life_orientation": "exclude",
                             "scale": [{"min_percent": 50, "level": 4}, {"min_percent": 0, "level": 1}]},
            "programmes": programmes,
            "sources": [{"id": "s", "url": "https://example.org", "publisher": "Example"}],
        }
    )


def _open(pid, fields, **extra):
    return {"id": pid, "name": pid, "fields": fields, "requirements": {"source": "s", "min_points": 20}, **extra}


def test_the_closest_safe_programme_wins_whatever_its_name(strong_marks):
    goal = _open("goal", ["health_sciences", "medicine", "medical_sciences"], selective=True)
    near = _open("zz_medical_science", ["natural_sciences", "health_sciences", "medical_sciences"])
    far = _open("aa_nursing", ["health_sciences", "nursing"], requirements={"source": "s", "min_points": 20,
                                                                             "competitive_points": 21})
    catalogue = {"a": _university("a", [goal]), "b": _university("b", [far]), "c": _university("c", [near])}
    plan = build_plan(catalogue, "a", "goal", strong_marks)
    # Closer to the goal (two of four fields shared) beats a better tier with one of four, and the name.
    assert plan.safe.match.programme_id == "zz_medical_science"
    assert plan.safe.notes[0] == "Related to goal through health sciences and medical sciences."


def test_routes_are_never_offered_again_as_the_safe_choice(strong_marks):
    route = {"to": "goal", "guarantee": "considered", "conditions": "Pass year one.", "source": "s"}
    goal = _open("goal", ["health_sciences"], selective=True)
    via = _open("bsc", ["health_sciences"], bridges_to=[dict(route)])
    other = _open("ecp", ["health_sciences"], bridges_to=[dict(route, eligibility_note="Some learners only.")])
    plan = build_plan({"a": _university("a", [goal, via, other])}, "a", "goal", strong_marks)
    assert plan.bridge.match.programme_id == "bsc"
    assert [r.match.programme_id for r in plan.other_routes] == ["ecp"]
    assert plan.safe is None  # both related programmes are already routes
