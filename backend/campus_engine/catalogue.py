"""Load and validate university data packs and the national funding pack."""
from __future__ import annotations

from pathlib import Path
from typing import TypeVar

import yaml
from pydantic import BaseModel, ValidationError

from .schemas import FundingPack, University, UniversityMap

ROOT = Path(__file__).resolve().parents[1]
UNIVERSITIES_DIR = ROOT / "data" / "universities"
FUNDING_PATH = ROOT / "data" / "national" / "funding.yaml"
MAPS_DIR = ROOT / "data" / "maps"
#: In the maps folder but not a map: which OpenStreetMap outline is which campus (scripts/fetch_osm_maps.py).
MAPS_CONFIG = "osm_campuses.yaml"

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


def load_map(path: str | Path) -> UniversityMap:
    return _load(path, UniversityMap)


def load_maps(directory: str | Path = MAPS_DIR) -> dict[str, UniversityMap]:
    """Every university's campus maps, by university id (the config and the names folder aren't maps)."""
    maps: dict[str, UniversityMap] = {}
    for path in sorted(Path(directory).glob("*.yaml")):
        if path.name == MAPS_CONFIG or path.name.startswith("_"):
            continue
        umap = load_map(path)
        if umap.university in maps:
            raise DataPackError(f"duplicate map for '{umap.university}' in {path.name}")
        maps[umap.university] = umap
    return maps


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
