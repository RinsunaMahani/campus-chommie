"""
OWASP A01 (server-side request forgery), enforced: only the files below may make the server call out, and each one
calls a fixed host from config, never an address a student sent. A new import of an HTTP or socket library anywhere
else fails the build, so the reviewer sees it (security sweep 3, docs/SECURITY.md).

Read with Python's own parser, like the other architecture rules.
"""
from __future__ import annotations

import ast
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[2]
SCANNED = [BACKEND / "src", BACKEND / "campus_engine"]
OUTBOUND = {"requests", "urllib.request", "urllib3", "httpx", "aiohttp", "http.client", "smtplib", "socket", "ftplib",
            "google.auth.transport", "google.auth.transport.requests"}

#: File -> the one host it calls and where that comes from.
ALLOWED = {
    "src/shared/email/email.py": "the SMTP server in MAIL_SERVER",
    "src/domains/classes/whatsapp/services/sender.py": "graph.facebook.com, with WHATSAPP_PHONE_NUMBER_ID from config",
    "src/domains/identity/auth/services/google_verifier.py": "Google's public sign-in keys (google-auth's fixed URL)",
}


def _imports(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            yield from (a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            yield node.module
            yield from (f"{node.module}.{a.name}" for a in node.names)


def _callers():
    for root in SCANNED:
        for path in sorted(root.rglob("*.py")):
            found = sorted({m for m in _imports(path) if m in OUTBOUND})
            if found:
                yield path.relative_to(BACKEND).as_posix(), found


def test_only_the_reviewed_files_call_out():
    unexpected = [f"{path}: {', '.join(mods)}" for path, mods in _callers() if path not in ALLOWED]
    assert not unexpected, (
        "These files import a library that makes the server call out. Make sure the address can't come from a "
        "request (SSRF), then add the file to ALLOWED with the host it calls:\n  " + "\n  ".join(unexpected)
    )


def test_the_scan_finds_the_known_callers():
    """A scan that finds nothing would pass forever."""
    assert {path for path, _ in _callers()} == set(ALLOWED)
