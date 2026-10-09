from datetime import date, datetime

from campus_engine.alerts import alerts_for
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
