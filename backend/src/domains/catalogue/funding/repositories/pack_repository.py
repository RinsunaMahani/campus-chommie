"""
The national funding pack, read once per process. campus_engine loads and
validates it (a broken pack fails CI before it gets here); a changed pack
reaches a running server on its next restart.
"""
from __future__ import annotations

from functools import lru_cache

from campus_engine.catalogue import load_funding
from campus_engine.schemas import FundingPack


@lru_cache(maxsize=1)
def funding_pack() -> FundingPack:
    return load_funding()
