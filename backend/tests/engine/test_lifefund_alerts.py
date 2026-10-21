from datetime import date, datetime

from campus_engine.alerts import TARGETS, alerts_for, module_alert
from campus_engine.lifefund import life_fund_signal
from campus_engine.runway import ExpectedPayment, project_runway
from campus_engine.workload import AcademicEvent, weekly_load

TODAY = date(2026, 10, 12)
ALLOWANCE = ExpectedPayment("Allowance", date(2026, 10, 30), 150_000)


def red_week(with_exam=False):
    kind = "exam" if with_exam else "test"
    events = [
        AcademicEvent("A", kind, datetime(2026, 10, 13, 9), weighting=40),
        AcademicEvent("B", "assignment", datetime(2026, 10, 14, 9), weighting=30),
        AcademicEvent("C", "test", datetime(2026, 10, 15, 9), weighting=30),
    ]
    return weekly_load(events, TODAY, weeks=1)


def green_week():
    return weekly_load([], TODAY, weeks=1)


def test_short_money_pauses_the_life_fund():
    runway = project_runway(61_000, TODAY, [ALLOWANCE], 4_500)
    signal = life_fund_signal(runway, green_week()[0], TODAY)
    assert signal.state == "paused"
    assert "before the next payment" in signal.reason
    assert signal.resume_hint == "Resumes when your next payment lands."


def test_comfortable_money_and_light_week_is_green():
    runway = project_runway(300_000, TODAY, [ALLOWANCE], 5_000)
    assert life_fund_signal(runway, green_week()[0], TODAY).state == "green"


def test_heavy_week_without_exam_is_amber():
    runway = project_runway(300_000, TODAY, [ALLOWANCE], 5_000)
    signal = life_fund_signal(runway, red_week()[0], TODAY)
    assert signal.state == "amber"
    assert "heavy week" in signal.reason


def test_heavy_exam_week_pauses():
    runway = project_runway(300_000, TODAY, [ALLOWANCE], 5_000)
    signal = life_fund_signal(runway, red_week(with_exam=True)[0], TODAY)
    assert signal.state == "paused"
    assert signal.resume_hint == "Resumes after the exam week."


def test_tight_money_is_amber():
    # Enough to reach the payment, but less than 3 days of spending to spare.
    runway = project_runway(18 * 5_000 + 8_000, TODAY, [ALLOWANCE], 5_000)
    signal = life_fund_signal(runway, green_week()[0], TODAY)
    assert signal.state == "amber"
    assert "tight" in signal.reason


def test_combined_alert_when_heavy_week_meets_short_money():
    runway = project_runway(61_000, TODAY, [ALLOWANCE], 4_500)
    alerts = alerts_for(red_week(), runway)
    assert [a.kind for a in alerts] == ["combined"]
    assert len(alerts[0].actions) >= 3


def test_separate_alerts():
    short = project_runway(61_000, TODAY, [ALLOWANCE], 4_500)
    fine = project_runway(300_000, TODAY, [ALLOWANCE], 5_000)
    assert [a.kind for a in alerts_for(red_week(), fine)] == ["heavy_week"]
    assert [a.kind for a in alerts_for(green_week(), short)] == ["money"]
    assert alerts_for(green_week(), fine) == []


def test_alerts_without_money_entered_yet():
    assert [a.kind for a in alerts_for(red_week(), None)] == ["heavy_week"]
    assert alerts_for(green_week(), None) == []


def test_every_action_says_where_it_leads():
    short = project_runway(61_000, TODAY, [ALLOWANCE], 4_500)
    fine = project_runway(300_000, TODAY, [ALLOWANCE], 5_000)
    alerts = alerts_for(red_week(), short) + alerts_for(red_week(), fine) + alerts_for(green_week(), short)
    alerts.append(module_alert("ANA201", 75, "Even 100% on the rest wouldn't reach 75%."))
    for alert in alerts:
        for action in alert.actions:
            assert action.target in TARGETS
            assert (action.target == "support") == (action.support_kind is not None)


def test_heavier_alerts_point_to_counselling_and_never_label_the_student():
    short = project_runway(61_000, TODAY, [ALLOWANCE], 4_500)
    fine = project_runway(300_000, TODAY, [ALLOWANCE], 5_000)
    for alert in alerts_for(red_week(), short) + alerts_for(red_week(), fine) + [module_alert("ANA201", 75, "x")]:
        assert "counselling" in {a.support_kind for a in alert.actions}
        words = " ".join([alert.title, alert.message] + [a.text for a in alert.actions]).lower()
        assert "at risk" not in words and "failing" not in words


def test_a_module_out_of_reach():
    alert = module_alert("ANA201", 75, "Even 100% on the rest wouldn't reach 75%.")
    assert (alert.kind, alert.title) == ("module", "ANA201: your 75% target is out of reach")
    assert alert.message == "Even 100% on the rest wouldn't reach 75%."
