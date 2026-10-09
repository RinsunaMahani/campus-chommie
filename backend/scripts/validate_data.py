"""Validate every university data pack.

Errors (exit code 1, so CI fails): schema problems and broken references, plus
anything incomplete in a pack marked release: true.
Warnings: unverified programmes and stale or missing verification dates.

Usage: python scripts/validate_data.py [folder]
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from campus_engine.catalogue import DataPackError, load_university  # noqa: E402

STALE_AFTER_DAYS = 365


def check(path: Path, today: date) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        uni = load_university(path)
    except DataPackError as exc:
        return [str(exc)], warnings

    def problem(message: str) -> None:
        (errors if uni.release else warnings).append(message)

    if uni.points_rules is None:
        problem(f"{uni.university}: no points rules yet")
    if uni.max_choices is None:
        problem(f"{uni.university}: max_choices not verified")
    for p in uni.programmes:
        if p.requirements is None:
            problem(f"{uni.university}/{p.id}: requirements not verified yet")
    for s in uni.sources:
        if s.last_verified is None:
            problem(f"{uni.university}/{s.id}: never verified")
        elif (today - s.last_verified).days > STALE_AFTER_DAYS:
            warnings.append(f"{uni.university}/{s.id}: last verified {s.last_verified}, re-check it")
    return errors, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate university data packs.")
    parser.add_argument("folder", nargs="?", default=str(ROOT / "data" / "universities"))
    args = parser.parse_args(argv)
    today = date.today()
    all_errors: list[str] = []
    for path in sorted(Path(args.folder).glob("*.yaml")):
        errors, warnings = check(path, today)
        for w in warnings:
            print(f"WARN  {w}")
        for e in errors:
            print(f"ERROR {e}")
        all_errors.extend(errors)
    print(f"{'FAILED' if all_errors else 'OK'}: {len(all_errors)} error(s)")
    return 1 if all_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
