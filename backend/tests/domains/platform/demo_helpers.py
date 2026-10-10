"""
The demo tests' helpers, which live with the student tests' helpers so every
folder can use them. pytest puts each test file's own folder on the path, so
the student tests' folder is added here.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "student"))

from student_helpers import CONSENT, PASSWORD, fresh_password, on_day, student  # noqa: E402,F401
from student_helpers import DEMO_EMAILS as EMAILS  # noqa: E402,F401
from student_helpers import DEMO_TODAY as TODAY  # noqa: E402,F401
from student_helpers import seed_demo as seed  # noqa: E402,F401
from student_helpers import sign_in_demo as sign_in  # noqa: E402,F401
