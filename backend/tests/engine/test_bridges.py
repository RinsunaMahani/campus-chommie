from campus_engine.bridges import build_plan
from campus_engine.matching import NOT_YET, REACH


def test_strong_learner_plan(catalogue, strong_marks):
    plan = build_plan(catalogue, "smu", "mbchb", strong_marks)
    assert plan.goal.match.tier == REACH
    # The unrestricted BSc route comes before the restricted foundation programme.
    assert plan.bridge.match.programme_id == "bsc_y1"
    assert plan.bridge.bridge.guarantee == "considered"
    assert any("Places on this route: 5." in n for n in plan.bridge.notes)
    assert [r.match.programme_id for r in plan.other_routes] == ["mbchb_ecp"]
    assert any(n.startswith("Eligibility:") for n in plan.other_routes[0].notes)
    # Every SMU programme is selective, so slot 3 is honestly labelled as not safe yet.
    assert plan.safe.match.programme_id == "brad"
    assert any("not a safe choice yet" in n for n in plan.safe.notes)
    assert any("Check how many programmes" in n for n in plan.notes)


def test_routes_the_learner_cannot_enter_go_last(catalogue, strong_marks):
    marks = dict(strong_marks, mathematics=55)  # level 4: below the foundation year's 5
    plan = build_plan(catalogue, "smu", "mbchb", marks)
    assert plan.goal.match.tier == NOT_YET
    assert plan.bridge.match.programme_id == "bsc_y1"
    assert plan.other_routes[0].match.tier == NOT_YET


def test_no_safe_choice_when_nothing_fits(catalogue):
    weak = {"english": 35, "mathematics": 35, "physical_sciences": 35, "life_sciences": 35, "life_orientation": 35}
    plan = build_plan(catalogue, "smu", "mbchb", weak)
    assert plan.safe is None
    assert any("No related programme" in n for n in plan.notes)


def test_choice_limit_warning(catalogue, strong_marks):
    limited = dict(catalogue)
    limited["smu"] = catalogue["smu"].model_copy(update={"max_choices": 2})
    plan = build_plan(limited, "smu", "mbchb", strong_marks)
    assert any("allows 2 choice(s)" in n for n in plan.notes)
