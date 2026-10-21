"""
"Find a time": free stretches long enough, around what's already in each day with a buffer, on the quarter hour,
spread over the week, never in the past.
"""
from __future__ import annotations

from datetime import date, time

from campus_engine.timetable import Busy, FreeSlot, find_time, find_time_lines

CFG = {"day_starts": "07:00", "day_ends": "21:00", "buffer_minutes": 15, "step_minutes": 15, "per_day": 2, "suggestions": 5}
MON, TUE = date(2026, 10, 26), date(2026, 10, 27)


def test_free_time_goes_round_classes_with_a_buffer_on_the_quarter_hour():
    busy = {MON: [Busy(time(7, 30), time(9, 10)), Busy(time(10, 0), time(16, 55))]}
    slots = find_time(busy, [MON], 60, CFG)
    # 09:10 + 15 min buffer = 09:25 -> 09:30, but only 15 minutes before 09:45 (10:00 less the buffer): too short.
    # After 16:55 + 15 = 17:10 -> 17:15.
    assert slots == [FreeSlot(MON, time(17, 15), time(18, 15))]


def test_at_most_two_a_day_and_five_in_all():
    days = [date(2026, 10, 26 + i) for i in range(5)]
    slots = find_time({}, days, 60, CFG)
    assert len(slots) == 5
    assert [s.on for s in slots] == [days[0], days[1], days[2], days[3], days[4]][:5]
    two_day = find_time({d: [Busy(time(12, 0), time(13, 0))] for d in days}, days, 60, CFG)
    assert sum(1 for s in two_day if s.on == days[0]) == 2


def test_nothing_in_the_past_and_nothing_past_the_day_end():
    slots = find_time({}, [MON, TUE], 120, CFG, not_before=(MON, 20 * 60))
    assert slots[0].on == TUE and slots[0].starts == time(7, 0)
    assert find_time({}, [MON], 15 * 60, CFG) == []


def test_in_words():
    assert find_time_lines([FreeSlot(MON, time(17, 15), time(18, 15))], 60) == [
        "Free for 1 hour: Mon 26 Oct 2026, 17:15 to 18:15."]
    assert find_time_lines([], 90) == [
        "No free 1 hour 30 minutes this week between your classes and plans. Try a shorter time or next week."]
