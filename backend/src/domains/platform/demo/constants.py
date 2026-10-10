"""The demo accounts' settings."""
from __future__ import annotations

from pathlib import Path

#: The fictional personas, with their dates as of the file's own "today".
PERSONAS_PATH = Path(__file__).resolve().parents[4] / "data" / "demo" / "personas.yaml"

#: The demo accounts' shared password is read from this environment variable, never from the repo.
PASSWORD_ENV = "DEMO_PASSWORD"

#: The brief: personas are re-based daily at 02:00 SAST. The job runs hourly and acts once a day from then.
REBASE_HOUR = 2
REBASE_EVERY_SECONDS = 3600

TIMEZONE = "Africa/Johannesburg"
