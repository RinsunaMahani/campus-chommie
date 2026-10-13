"""
The campus maps, read once per process. campus_engine loads and validates them (a broken map fails
CI before it gets here); a changed map reaches a running server on its next restart.
"""
from __future__ import annotations

from functools import lru_cache

from campus_engine.catalogue import load_maps
from campus_engine.schemas import UniversityMap


@lru_cache(maxsize=1)
def all_maps() -> dict[str, UniversityMap]:
    return load_maps()
