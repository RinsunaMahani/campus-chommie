"""models -- a student's timetable, exams and own activities, in the "student" schema."""
from .activity import Activity
from .exam_entry import ExamEntry
from .timetable_entry import TimetableEntry

__all__ = ["Activity", "ExamEntry", "TimetableEntry"]
