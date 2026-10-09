"""Course-finder text. Only the course finder is multilingual (ADR-006).

English is the source text. A language is added here only after a fluent speaker
has reviewed every string, and translated rules are always shown next to the
English original, so a translation can never change what a rule says.
"""
from __future__ import annotations

LANGUAGES = {"en": "English"}

STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "title": "Find my course",
        "intro": "Enter your marks to see which programmes fit you, and get a three-choice application plan.",
        "language": "Language",
        "language_note": "More South African languages will be added once a fluent speaker has reviewed each translation.",
        "university": "University",
        "marks_heading": "Your marks",
        "marks_help": "Use your latest results: final Grade 11 or Grade 12. These are example marks, so replace them with yours.",
        "subject": "Subject {n}",
        "percent": "Mark (%)",
        "goal": "The programme you want most",
        "show": "Show my options",
        "results": "How you match",
        "plan": "Your three-choice plan",
        "slot_goal": "1. Your goal",
        "slot_bridge": "2. A route into your goal",
        "slot_safe": "3. A safer related choice",
        "other_routes": "Other routes into your goal",
        "nothing_stored": "Nothing you enter here is saved.",
        "source": "Source",
        "duplicate": "You picked {subject} more than once. Only the last mark counts.",
        "no_plan": "Pick the programme you want most to see a plan.",
    }
}


def t(key: str, lang: str = "en", **values: object) -> str:
    text = STRINGS.get(lang, {}).get(key) or STRINGS["en"][key]
    return text.format(**values) if values else text
