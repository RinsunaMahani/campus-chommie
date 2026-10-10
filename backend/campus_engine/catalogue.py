"""Load and validate university data packs and the national funding pack."""
from __future__ import annotations

from pathlib import Path
from typing import TypeVar

import yaml
from pydantic import BaseModel, ValidationError

from .schemas import FundingPack, University

ROOT = Path(__file__).resolve().parents[1]
UNIVERSITIES_DIR = ROOT / "data" / "universities"
FUNDING_PATH = ROOT / "data" / "national" / "funding.yaml"

Pack = TypeVar("Pack", bound=BaseModel)


class DataPackError(ValueError):
    """A data pack failed validation."""


def _load(path: str | Path, model: type[Pack]) -> Pack:
    path = Path(path)
    with path.open(encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    try:
        return model.model_validate(raw)
    except ValidationError as exc:
        raise DataPackError(f"{path.name}: {exc}") from exc


def load_university(path: str | Path) -> University:
    return _load(path, University)


def load_funding(path: str | Path = FUNDING_PATH) -> FundingPack:
    """The national funders (NSFAS), which every plan shows beside its universities."""
    return _load(path, FundingPack)


def load_catalogue(directory: str | Path = UNIVERSITIES_DIR) -> dict[str, University]:
    """Load every pack in a folder. Files starting with '_' are templates and are skipped."""
    catalogue: dict[str, University] = {}
    for path in sorted(Path(directory).glob("*.yaml")):
        if path.name.startswith("_"):
            continue
        uni = load_university(path)
        if uni.university in catalogue:
            raise DataPackError(f"duplicate university id '{uni.university}' in {path.name}")
        catalogue[uni.university] = uni
    return catalogue
