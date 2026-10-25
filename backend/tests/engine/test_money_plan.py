"""
Looking ahead with money: "can I afford this?" (yes, tight, not now and when instead), the payday plan's pots,
and a goal's weekly pace. Fictional amounts: R1 000 now, R40 a day, R1 500 landing in 20 days.
"""
from __future__ import annotations

from datetime import date, timedelta

from campus_engine.money_plan import Goal, afford, goal_pace, payday_plan, pot_pace
from campus_engine.runway import ExpectedPayment

TODAY = date(2026, 10, 12)
PAYDAY = TODAY + timedelta(days=20)  # Sun 1 Nov 2026
PAY = [ExpectedPayment("Allowance", PAYDAY, 150_000)]


def check(amount: int, payments=PAY):
    return afford(amount, 100_000, TODAY, payments, 4_000, 4_000, 10_000)


def test_a_small_buy_is_a_yes_with_what_is_left_a_day():
    a = check(5_000)
    assert a.verdict == "yes"
    assert a.lines == ["After it you'd still have about R2.50 a day for extras until your next payment on "
                       "Sun 1 Nov 2026, with essentials and your life fund covered."]


def test_a_buy_that_eats_the_buffer_is_tight_but_lasts():
    a = check(20_000)
    assert a.verdict == "tight"
    assert "your money still lasts past your next payment on Sun 1 Nov 2026" in a.lines[0]


def test_a_buy_that_runs_the_money_out_before_payday_is_not_now_with_when_instead():
    a = check(50_000)
    assert a.verdict == "not_now"
    assert (a.days_before, a.days_after) == (62, 12)  # the R1 500 lands in between
    assert a.wait_until == PAYDAY
    assert a.lines == [
        "Buying it today, your money would last 12 days instead of 62 days: it would run out around "
        "Sat 24 Oct 2026, before your next payment on Sun 1 Nov 2026.",
        "If you wait until your payment lands on Sun 1 Nov 2026, you can buy it then and your money still lasts.",
    ]


def test_more_than_the_balance_is_not_now():
    a = check(200_000)
    assert a.verdict == "not_now" and a.wait_until is None
    assert a.lines == ["R2 000 is more than your balance of about R1 000."]


def test_when_money_already_runs_short_it_only_says_keep_to_essentials():
    a = afford(5_000, 10_000, TODAY, PAY, 4_000, 4_000, 0)
    assert a.verdict == "not_now" and a.wait_until is None
    assert a.lines == ["Your money already runs out before your next payment on Sun 1 Nov 2026; this would make it "
                       "1 day sooner. Keep to essentials until then."]


def test_when_even_the_next_payment_cannot_cover_it_it_says_so():
    a = check(90_000, [ExpectedPayment("Allowance", PAYDAY, 10_000)])
    assert a.verdict == "not_now" and a.wait_until is None
    assert a.lines[-1].startswith("Even out of your next payment it would leave you short.")


def test_the_payday_plan_covers_essentials_to_the_next_payday_then_shares_goals():
    payments = PAY + [ExpectedPayment("Allowance", PAYDAY + timedelta(days=30), 150_000)]
    plan = payday_plan(payments, TODAY, 4_000, [Goal("Registration fee", 90_000, TODAY + timedelta(days=80))])
    assert plan.lands_on == PAYDAY
    assert [(p.label, p.cents) for p in plan.pots] == [("Essentials", 120_000), ("Registration fee", 30_000)]
    assert plan.pots[1].why == "R900 still to put aside by Thu 31 Dec 2026, over 3 paydays"
    assert plan.free_cents == 0
    assert plan.lines == ["When R1 500 lands on Sun 1 Nov 2026: R1 500 is spoken for, and R0 is yours to spend freely."]


def test_a_payday_short_of_essentials_says_essentials_come_first():
    plan = payday_plan([ExpectedPayment("Wage", PAYDAY, 50_000)], TODAY, 4_000, [])
    assert plan.free_cents == 0
    assert plan.lines[0].endswith("it's R700 short of covering these. Essentials come first: the goals can wait for "
                                  "a later payday.")


def test_no_payment_expected_means_no_plan():
    assert payday_plan([], TODAY, 4_000, []) is None


def test_a_goals_weekly_pace():
    assert goal_pace(70_000, TODAY + timedelta(days=14), TODAY) == (
        35_000, "About R350 a week for 2 weeks gets you there by Mon 26 Oct 2026.")
    assert goal_pace(0, TODAY, TODAY) == (0, "Done: you've put it all aside.")
    assert goal_pace(5_000, TODAY, TODAY) == (5_000, "Due now: R50 still to find.")


def test_payday_plan_prioritizes_family_stokvel_buffer_then_goals():
    payments = [ExpectedPayment("Allowance", PAYDAY, 350_000)]
    goals = [
        Goal("Laptop", 60_000, PAYDAY + timedelta(days=60), kind="big_purchase", stokvel_funded=True, amount_cents=60_000),
        Goal("Fees", 30_000, PAYDAY + timedelta(days=30), kind="goal", amount_cents=30_000),
        Goal("Emergency buffer", 40_000, None, kind="buffer", amount_cents=40_000),
        Goal("Stokvel contribution", 30_000, None, kind="stokvel", amount_cents=30_000),
        Goal("Family support", 50_000, None, kind="family", amount_cents=50_000),
    ]
    plan = payday_plan(payments, TODAY, 4_000, goals)
    assert plan is not None
    labels = [p.label for p in plan.pots]
    # Priority order: Essentials -> Family & Stokvel -> Buffer -> Date goals
    assert labels == ["Essentials", "Family support", "Stokvel contribution", "Emergency buffer", "Fees", "Laptop"]
    # Check amounts and explanations
    assert [(p.label, p.cents) for p in plan.pots] == [
        ("Essentials", 120_000),
        ("Family support", 50_000),
        ("Stokvel contribution", 30_000),
        ("Emergency buffer", 40_000),
        ("Fees", 15_000),  # 30_000 over 2 paydays = 15_000
        ("Laptop", 20_000),  # 60_000 over 3 paydays = 20_000
    ]
    assert plan.pots[1].why == "R500 monthly support for family"
    assert plan.pots[2].why == "R300 monthly stokvel contribution"
    assert plan.pots[3].why == "R400 to reach your R400 buffer"
    assert "(paying through stokvel)" in plan.pots[5].why
    assert plan.free_cents == 75_000  # 350k - 275k = 75k


def test_buffer_paydays_spreads_buffer():
    payments = [ExpectedPayment("Allowance", PAYDAY, 200_000)]
    goals = [Goal("Emergency buffer", 40_000, None, kind="buffer", amount_cents=40_000)]
    plan = payday_plan(payments, TODAY, 4_000, goals, buffer_paydays=2)
    assert plan is not None
    assert [(p.label, p.cents) for p in plan.pots] == [("Essentials", 120_000), ("Emergency buffer", 20_000)]
    assert plan.pots[1].why == "R400 still to put aside for your R400 buffer, over 2 paydays"


def test_pot_pace_for_all_kinds():
    # Family
    assert pot_pace("family", 50_000, 0, None, TODAY) == (12_500, "R500 a month to support family.")
    assert pot_pace("family", 50_000, 20_000, None, TODAY) == (
        7_500, "R500 monthly support for family: R200 aside so far, R300 still to find.")
    assert pot_pace("family", 50_000, 50_000, None, TODAY) == (
        0, "Done: you've set aside your family support for this month.")

    # Stokvel
    assert pot_pace("stokvel", 30_000, 0, None, TODAY) == (7_500, "R300 a month for your stokvel contribution.")
    assert pot_pace("stokvel", 30_000, 10_000, None, TODAY) == (
        5_000, "R300 monthly stokvel contribution: R100 aside so far, R200 still to find.")
    assert pot_pace("stokvel", 30_000, 30_000, None, TODAY) == (
        0, "Done: your stokvel contribution for this month is put aside.")

    # Buffer
    assert pot_pace("buffer", 100_000, 0, None, TODAY) == (None, "R1 000 emergency buffer to keep aside.")
    assert pot_pace("buffer", 100_000, 40_000, None, TODAY) == (
        None, "R1 000 emergency buffer: R400 aside so far, R600 still to find.")
    assert pot_pace("buffer", 100_000, 100_000, None, TODAY) == (0, "Done: your buffer is fully funded.")

    # Big purchase with stokvel funding
    due = TODAY + timedelta(days=14)
    per_week, line = pot_pace("big_purchase", 70_000, 0, due, TODAY, stokvel_funded=True)
    assert per_week == 35_000
    assert "About R350 a week for 2 weeks gets you there by Mon 26 Oct 2026. Paying through a stokvel." == line

    per_week_done, line_done = pot_pace("big_purchase", 70_000, 70_000, due, TODAY, stokvel_funded=True)
    assert per_week_done == 0
    assert line_done == "Done: you've put it all aside (paying through your stokvel)."
