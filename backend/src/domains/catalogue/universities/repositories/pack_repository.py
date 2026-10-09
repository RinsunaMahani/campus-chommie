"""
The data packs, read once per process. campus_engine loads and validates
them (a broken pack fails CI before it gets here); a new or changed pack
reaches a running server on its next restart.
"""
from __future__ import annotations

from functools import lru_cache

from campus_engine.catalogue import load_catalogue
from campus_engine.schemas import University


@lru_cache(maxsize=1)
def all_packs() -> dict[str, University]:
    """Every pack, by university id. Files starting with "_" are templates and are skipped."""
    return load_catalogue()
