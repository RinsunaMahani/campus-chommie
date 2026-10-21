import pytest

from campus_engine.standing import Assessment, standing


def test_needed_average_on_remaining_work():
    module = [
        Assessment("Test 1", 20, 64),
        Assessment("Assignment 1", 10, 71),
        Assessment("Test 2", 20),
        Assessment("Exam", 50),
    ]
    s = standing(module, target=60)
    assert s.current == pytest.approx(1990 / 30)
    assert s.needed == pytest.approx((6000 - 1990) / 70)
    assert s.status == "possible"
    assert "57.3%" in s.message and "70%" in s.message


def test_secured_target_mentions_sub_minimums():
    s = standing([Assessment("Coursework", 90, 100), Assessment("Exam", 10)], target=50)
    assert s.status == "secured"
    assert "sub-minimum" in s.message


def test_out_of_reach():
    s = standing([Assessment("Test", 80, 20), Assessment("Exam", 20)], target=50)
    assert s.status == "out_of_reach"
    assert s.needed == pytest.approx(170)


def test_final_mark():
    s = standing([Assessment("Test", 50, 60), Assessment("Exam", 50, 40)], target=55)
    assert s.status == "final"
    assert s.current == pytest.approx(50)
    assert "5.0 points below" in s.message


def test_weights_must_be_positive():
    with pytest.raises(ValueError):
        standing([Assessment("Nothing", 0)], target=50)
