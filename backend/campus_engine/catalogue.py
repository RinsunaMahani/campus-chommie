"""Load and validate university data packs and the national funding and colleges packs."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import TypeVar

import yaml
from pydantic import BaseModel, ValidationError

from .schemas import CollegesPack, FundingPack, University, UniversityMap

ROOT = Path(__file__).resolve().parents[1]
UNIVERSITIES_DIR = ROOT / "data" / "universities"
FUNDING_PATH = ROOT / "data" / "national" / "funding.yaml"
COLLEGES_PATH = ROOT / "data" / "national" / "colleges.yaml"
MAPS_DIR = ROOT / "data" / "maps"
#: In the maps folder but not a map: which OpenStreetMap outline is which campus (scripts/fetch_osm_maps.py).
MAPS_CONFIG = "osm_campuses.yaml"
#: The packs again as JSON, written when the container image is built (build_cache). Parsing YAML was most of the
#: CPU a free host spent warming up after a start (measured 26 Oct 2026); pydantic reads its own JSON about ten
#: times faster, and still validates it. Each file is named by the hash of the YAML it came from, so a changed pack
#: never meets an old copy: without a matching copy the YAML itself is read, as before.
CACHE_DIR = ROOT / "data" / ".cache"

Pack = TypeVar("Pack", bound=BaseModel)


def _parse(fh):
    """libyaml's C parser reads the packs about eight times faster than PyYAML's pure-Python one, with the same
    result. On a small free host the difference is most of a cold start, so use it whenever the wheel ships it."""
    if hasattr(yaml, "CSafeLoader"):
        return yaml.load(fh, Loader=yaml.CSafeLoader)
    return yaml.safe_load(fh)


class DataPackError(ValueError):
    """A data pack failed validation."""


def _cached(raw: bytes, model: type[Pack]) -> Path:
    return CACHE_DIR / f"{model.__name__}-{hashlib.sha256(raw).hexdigest()[:32]}.json"


def _load(path: str | Path, model: type[Pack], use_cache: bool = True) -> Pack:
    path = Path(path)
    raw = path.read_bytes()
    if use_cache:
        cached = _cached(raw, model)
        if cached.is_file():
            try:
                return model.model_validate_json(cached.read_bytes())
            except ValidationError:
                pass  # a broken copy: the YAML below decides
    try:
        return model.model_validate(_parse(raw.decode("utf-8")))
    except ValidationError as exc:
        raise DataPackError(f"{path.name}: {exc}") from exc


def _packs() -> list[tuple[Path, type[BaseModel]]]:
    """Every pack the app reads, with its model."""
    found: list[tuple[Path, type[BaseModel]]] = [(FUNDING_PATH, FundingPack), (COLLEGES_PATH, CollegesPack)]
    found += [(p, University) for p in sorted(UNIVERSITIES_DIR.glob("*.yaml")) if not p.name.startswith("_")]
    found += [(p, UniversityMap) for p in sorted(MAPS_DIR.glob("*.yaml"))
              if p.name != MAPS_CONFIG and not p.name.startswith("_")]
    return found


def build_cache() -> int:
    """Write the JSON copy of every pack (the image build runs this). Returns how many were written."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    for path, model in _packs():
        raw = path.read_bytes()
        _cached(raw, model).write_text(_load(path, model, use_cache=False).model_dump_json(), encoding="utf-8")
    return len(_packs())


def load_university(path: str | Path) -> University:
    return _load(path, University)


def load_funding(path: str | Path = FUNDING_PATH) -> FundingPack:
    """The national funders (NSFAS), which every plan shows beside its universities."""
    return _load(path, FundingPack)


def load_colleges(path: str | Path = COLLEGES_PATH) -> CollegesPack:
    """Public TVET colleges and DHET's registers of private colleges and higher education institutions."""
    return _load(path, CollegesPack)


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
