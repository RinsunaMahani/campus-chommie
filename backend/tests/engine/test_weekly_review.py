"""
Your week in review: what's behind the student, what's coming, how their marks moved and how their spending compares
with their usual, each in plain words with its numbers. A week still under way compares like with like. Made-up
situations.
"""
from __future__ import annotations

from datetime import date, timedelta

from campus_engine.weekly_review import Facts, Item, MarkEntered, ModuleMarks, weekly_review

START, END = date(2026, 10, 19), date(2026, 10, 25)  # Monday to Sunday: a Sunday check-in week
CFG = {"coming_days": 7, "compare_weeks": 4, "same_band": 0.1, "max_items": 8}


def review(**kw):
    return weekly_review(Facts(START, END, kw.pop("today", END), **kw), CFG)


def test_a_full_week_says_what_was_done_what_is_coming_and_counts_both():
    r = review(
        behind=[Item("test", "STK110 Test 2", date(2026, 10, 21), "09:00"), Item("assignment", "INF171 Assignment 3", date(2026, 10, 23))],
        coming=[Item("exam", "STK110 exam", date(2026, 10, 30), "08:30"), Item("funding", "NSFAS", date(2026, 10, 31))],
        marks=[MarkEntered("STK110", "Test 2", 68)],
        checked_in=True, streak_weeks=3,
    )
    assert r.headline == "4 things done and 2 dates in the next 7 days."
    assert [d.text for d in r.done] == [
        "STK110 Test 2 (Wed 21 Oct at 09:00)",
        "INF171 Assignment 3 (Fri 23 Oct)",
        "You entered 1 mark: STK110 Test 2 (68%).",
        "You checked in on your money (3 weeks in a row).",
    ]
    assert [c.text for c in r.coming] == ["STK110 exam, in 5 days (Fri 30 Oct at 08:30)", "NSFAS closes in 6 days (Sat 31 Oct)"]
    assert r.finished


def test_a_quiet_week_says_so_and_how_to_fill_it():
    r = review()
    assert r.headline == "A quiet week. Add your classes, marks and money to see more here."
    assert r.done == [] and r.coming == [] and r.marks == []
    assert r.spending.direction == "unknown"
    assert r.spending.text == "No spending logged this week. A money check-in takes a minute and fills in the week."


def test_long_lists_are_cut_with_a_count_of_the_rest():
    coming = [Item("quiz", f"MOD{i} Quiz", START + timedelta(days=7 + i % 7)) for i in range(11)]
    r = review(coming=coming)
    assert len(r.coming) == 9 and r.coming[-1].text == "And 3 more: see your week."
    assert r.headline == "11 dates in the next 7 days."


def test_more_than_three_marks_name_three_and_count_the_rest():
    marks = [MarkEntered("STK110", f"Quiz {i}", 70 + i) for i in range(1, 6)]
    r = review(marks=marks)
    assert r.done[0].text == "You entered 5 marks: STK110 Quiz 1 (71%), STK110 Quiz 2 (72%), STK110 Quiz 3 (73%) and 2 more."


def test_a_goal_and_a_closed_funder_read_in_words():
    r = review(behind=[Item("funding", "Funza Lushaka", date(2026, 10, 20))], coming=[Item("goal", "Laptop", date(2026, 10, 27))])
    assert r.done[0].text == "Funza Lushaka closed (Tue 20 Oct)"
    assert r.coming[0].text == 'Your goal "Laptop" is due in 2 days (Tue 27 Oct)'


# ---------------------------------------------------------------- marks


def test_marks_moving_up_down_staying_and_first_ones():
    r = review(modules=[
        ModuleMarks("STK110", 60, 58.0, 64.25),
        ModuleMarks("INF171", 60, 71.0, 66.0),
        ModuleMarks("WTW114", 50, 55.0, 55.0),
        ModuleMarks("BME120", 50, None, 62.0),
        ModuleMarks("EKN110", 50, None, None),  # nothing written yet: left out
    ])
    assert [(m.code, m.direction) for m in r.marks] == [("BME120", "first"), ("INF171", "down"), ("STK110", "up"), ("WTW114", "same")]
    texts = {m.code: m.text for m in r.marks}
    assert texts["STK110"] == "STK110: your average went up from 58% to 64.2% with this week's marks."
    assert texts["INF171"] == "INF171: your average moved from 71% to 66% with this week's marks."
    assert texts["WTW114"] == "WTW114: your average stayed at 55% with this week's marks."
    assert texts["BME120"] == "BME120: your first marks are in, averaging 62%."
    assert r.support  # a mark went down: Support is pointed to


def test_support_is_pointed_to_when_a_target_is_out_of_reach_even_if_marks_went_up():
    assert review(modules=[ModuleMarks("STK110", 75, 30.0, 35.0, out_of_reach=True)]).support
    assert not review(modules=[ModuleMarks("STK110", 60, 58.0, 64.0)]).support


def test_no_words_label_or_frighten_the_student():
    r = review(modules=[ModuleMarks("STK110", 75, 50.0, 20.0, out_of_reach=True)], spent_cents=200_000, earlier_weeks_cents=[50_000])
    words = " ".join([r.headline] + [m.text for m in r.marks] + [r.spending.text]).lower()
    for banned in ("at risk", "fail", "bad", "overspent", "too much", "careless", "warning"):
        assert banned not in words


# ---------------------------------------------------------------- spending


def test_a_finished_week_compares_with_the_average_of_the_weeks_before():
    r = review(spent_cents=62_000, earlier_weeks_cents=[80_000, 78_000, 82_000, 80_000])
    s = r.spending
    assert (s.spent_cents, s.usual_cents, s.days, s.weeks_compared, s.direction) == (62_000, 80_000, 7, 4, "less")
    assert s.text == "You spent R620 this week, R180 less than your usual of about R800 (from the last 4 weeks)."
    assert s.weeks == [80_000, 82_000, 78_000, 80_000, 62_000]  # oldest first, this week last


def test_more_and_about_the_same():
    assert review(spent_cents=100_000, earlier_weeks_cents=[80_000]).spending.text == (
        "You spent R1 000 this week, R200 more than your usual of about R800 (from the last 1 week).")
    same = review(spent_cents=84_000, earlier_weeks_cents=[80_000]).spending
    assert same.direction == "same" and "about the same as your usual of about R800" in same.text


def test_a_week_under_way_compares_with_the_usual_for_the_same_days():
    r = review(today=date(2026, 10, 23), spent_cents=50_000, earlier_weeks_cents=[70_000, 70_000])  # Friday: 5 of 7 days
    s = r.spending
    assert (s.days, s.usual_cents, s.direction) == (5, 50_000, "same")
    assert s.text == "You spent R500 so far this week (5 of 7 days), about the same as your usual of about R500 for 5 days (from the last 2 weeks)."
    assert not r.finished


def test_weeks_with_nothing_logged_are_left_out_of_the_usual():
    s = review(spent_cents=40_000, earlier_weeks_cents=[None, 60_000, None, 60_000, 90_000]).spending
    assert (s.usual_cents, s.weeks_compared) == (60_000, 2)  # only the last 4 weeks, and only those with spending
    assert s.weeks == [60_000, None, 60_000, None, 40_000]


def test_the_first_week_logged_has_nothing_to_compare_yet():
    s = review(spent_cents=40_000, earlier_weeks_cents=[None, None]).spending
    assert s.direction == "unknown" and s.usual_cents is None
    assert s.text == "You spent R400 this week. Keep logging: from next week you'll see how it compares."


def test_a_past_week_reads_that_week_not_this_week():
    r = review(today=date(2026, 10, 27), modules=[ModuleMarks("STK110", 60, 58.0, 64.0)], spent_cents=50_000, earlier_weeks_cents=[50_000])
    assert r.marks[0].text == "STK110: your average went up from 58% to 64% with that week's marks."
    assert r.spending.text == "You spent R500 that week, about the same as your usual of about R500 (from the last 1 week)."
    assert review(today=date(2026, 10, 27)).spending.text.startswith("No spending logged that week.")
