"""
The national colleges pack, read once per process. campus_engine loads and validates it (a broken
pack fails CI before it gets here); a changed pack reaches a running server on its next restart.
"""
from __future__ import annotations

from functools import lru_cache

from campus_engine.catalogue import load_colleges
from campus_engine.schemas import CollegesPack


@lru_cache(maxsize=1)
def colleges_pack() -> CollegesPack:
    return load_colleges()
