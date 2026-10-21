"""
What the funding pack tells other features. The course finder reads it here,
never through the repository.

A pack nobody has checked yet is still served, with `confirmed: false` and a
notice the app shows next to it.
"""
from __future__ import annotations

from campus_engine.schemas import FundingPack

from ..constants import UNCONFIRMED_NOTICE
from ..repositories.pack_repository import funding_pack


def pack() -> FundingPack:
    """The national funders, which every plan shows beside its universities."""
    return funding_pack()


def confirmation(funding: FundingPack) -> dict:
    """Whether a person has checked the pack, and the notice to show if not."""
    return {"confirmed": funding.release, "notice": None if funding.release else UNCONFIRMED_NOTICE}
