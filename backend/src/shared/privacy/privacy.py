"""
What each feature holds about a person, for GET /me/export (POPIA: a person
may see everything we hold about them). A feature registers its exporter at
startup (src/__init__.py); identity's export calls every one, knowing
nothing about what they hold. The same registry pattern as
shared/notifications: this module knows no feature and imports none.

Deleting needs no registry: every feature's rows point at the account with
ON DELETE CASCADE, so DELETE /me takes them all with it.

An exporter takes the signed-in user and returns plain data (dicts, lists,
strings, numbers): only that person's own records, never anyone else's, and
never a secret (hashes, tokens, codes).
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

_exporters: dict[str, Callable[[Any], Any]] = {}


def register_exporter(section: str, export: Callable[[Any], Any]) -> None:
    """`section` names the part of the export, for example "money". Registering it again replaces it."""
    _exporters[section] = export


def clear_exporters() -> None:
    """Test helper."""
    _exporters.clear()


def sections() -> list[str]:
    return list(_exporters)


def export_all(user: Any) -> dict[str, Any]:
    """Every registered section for `user`. A failing exporter fails the export: one with a part
    silently missing would tell the person we hold less than we do."""
    return {section: export(user) for section, export in _exporters.items()}
