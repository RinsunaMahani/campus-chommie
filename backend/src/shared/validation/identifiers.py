"""
Identifier normalization — turns messy real-world input into the
canonical form used for INDEXED MATCHING (not display). Scope matches
this module's sibling validators.py: infrastructure-level, format/shape
only, never business rules.

WHY THIS EXISTS: real South African phone input varies too much for an
inline regex to be safe -- leading zero vs +27, spaces, dashes, users
pasting a number with a stray "tel:" prefix. Using `phonenumbers`
(Google's libphonenumber, the same library iOS/Android's own dialers
use) is worth the dependency rather than re-deriving that logic badly.

Shared here (not owned by one feature) since normalizing a phone number
for matching is a cross-cutting concern.
"""
from __future__ import annotations

from typing import Optional

import phonenumbers

# Default region for parsing a NATIONAL-format number (one without a
# leading + / country code) — Campus Chommie's users are South African
# (+27...). A number that's
# already in full international format (+<any country>...) is parsed
# correctly regardless of this default.
DEFAULT_REGION = "ZA"


def normalize_email(value: str) -> str:
    """Matches the existing inline convention in user_repository.py
    exactly (`.strip().lower()`) — this function exists so
    connections doesn't re-derive that logic locally, not to
    change what it does."""
    return value.strip().lower()


def normalize_phone(value: str, region: str = DEFAULT_REGION) -> Optional[str]:
    """Returns E.164 (e.g. "+27712345678") for a valid, real number, or
    None if the input isn't parseable/valid — callers decide what a
    None means for them (e.g. "this can't be a phone search, try it as
    a name instead"), this function never guesses.

    NEVER raises on bad input — phonenumbers.NumberParseException is
    caught and turned into None, since this runs on arbitrary user
    search input that's expected to sometimes just be wrong.
    """
    try:
        parsed = phonenumbers.parse(value, region)
    except phonenumbers.NumberParseException:
        return None

    if not phonenumbers.is_valid_number(parsed):
        return None

    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)


def looks_like_phone(value: str) -> bool:
    """Cheap pre-check so callers can decide "try phone matching"
    without paying for a full parse on obviously-not-a-phone input
    (e.g. a business name search). Deliberately permissive — the real
    validity check is normalize_phone()'s job, not this one's."""
    digits_and_symbols = value.strip()
    if not digits_and_symbols:
        return False
    stripped = digits_and_symbols.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if stripped.startswith("+"):
        stripped = stripped[1:]
    return stripped.isdigit() and 7 <= len(stripped) <= 15


def escape_like_pattern(value: str) -> str:
    """Escapes SQL LIKE/ILIKE's three special characters (%, _, and
    the escape character itself) in raw user input BEFORE it gets
    turned into a search pattern, for any search by name prefix.
    Without this, someone searching for a literal name such as
    "50% Off" would have their own "%" interpreted as a wildcard, and someone searching a single "%"
    character would get back the first N results alphabetically
    instead of a real narrow match -- not a data-exposure risk (the
    caller already only returns the same narrow, already-masked
    fields any search result shows), but a genuine correctness bug in
    what "search" means.

    Callers still append their own trailing "%" for the prefix match
    AFTER calling this -- this function only escapes what the PERSON
    typed, never adds the wildcard itself.
    """
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
