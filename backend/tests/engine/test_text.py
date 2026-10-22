"""
Where a pack's facts come from, said plainly instead of "not confirmed": the source and the last day it was read.
"""
from __future__ import annotations

from datetime import date

from campus_engine.text import read_from


def test_where_the_facts_come_from_and_the_last_day_they_were_read():
    read = [date(2026, 10, 9), None, date(2026, 10, 22), date(2026, 10, 13)]
    assert read_from("UP's own documents", read) == "From UP's own documents, last read on Thu 22 Oct 2026."


def test_with_no_reading_date_it_names_the_source_only():
    assert read_from("OpenStreetMap", [None]) == "From OpenStreetMap."
    assert read_from("OpenStreetMap", []) == "From OpenStreetMap."
