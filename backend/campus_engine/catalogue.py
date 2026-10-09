"""Load and validate university data packs."""
from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError

from .schemas import University

ROOT = Path(__file__).resolve().parents[1]
UNIVERSITIES_DIR = ROOT / "data" / "universities"


class DataPackError(ValueError):
    """A data pack failed validation."""


def load_university(path: str | Path) -> University:
    path = Path(path)
    with path.open(encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    try:
        return University.model_validate(raw)
    except ValidationError as exc:
        raise DataPackError(f"{path.name}: {exc}") from exc


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
