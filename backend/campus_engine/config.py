"""Load tunable settings from config.yaml, falling back to safe defaults."""
from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config.yaml"

DEFAULTS: dict[str, Any] = {
    "workload": {
        "base_load": {"quiz": 1, "assignment": 2, "practical": 3, "test": 3, "exam": 4},
        "cluster_hours": 48,
        "cluster_multiplier": 1.5,
        "thresholds": {"amber": 4.0, "red": 7.0},
    },
    "runway": {"late_days": 14, "buffer_days": 3, "horizon_days": 120},
    "forecast": {"ewma_alpha": 0.3, "min_days_of_history": 5, "spread_window": 14},
    "applications": {"closing_soon_days": 14, "seen_open_days": 14},
    "funding": {"per_choice": 5, "remind_days": [7, 1]},
    "alerts": {"lookahead_weeks": 3},
    "timetable_import": {"line_tolerance": 2.0, "merge_gap_minutes": 10, "max_rows": 2000, "max_exam_minutes": 480},
}


def _merge(base: dict, override: dict) -> dict:
    out = deepcopy(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = value
    return out


@lru_cache(maxsize=4)
def load_config(path: str | None = None) -> dict[str, Any]:
    """Return the merged configuration. Treat the result as read-only."""
    p = Path(path) if path else CONFIG_PATH
    if not p.exists():
        return deepcopy(DEFAULTS)
    with p.open(encoding="utf-8") as fh:
        return _merge(DEFAULTS, yaml.safe_load(fh) or {})
