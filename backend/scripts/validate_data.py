"""Validate every university data pack and the national funding pack.

Errors (exit code 1, so CI fails): schema problems and broken references, plus
anything incomplete in a pack marked release: true.
Warnings: unverified programmes and application facts, and stale or missing
verification dates.

Usage: python scripts/validate_data.py [folder] [--funding path]
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from campus_engine.catalogue import FUNDING_PATH, DataPackError, load_funding, load_university  # noqa: E402
from campus_engine.schemas import Applications, Source  # noqa: E402

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
    _check_applications(uni.university, uni.applications, problem)
    _check_sources(uni.university, uni.sources, today, problem, warnings)
    return errors, warnings


def check_funding(path: Path, today: date) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        pack = load_funding(path)
    except DataPackError as exc:
        return [str(exc)], warnings

    def problem(message: str) -> None:
        (errors if pack.release else warnings).append(message)

    for f in pack.funders:
        _check_applications(f"funding/{f.id}", f.applications, problem)
    _check_sources("funding", pack.sources, today, problem, warnings)
    return errors, warnings


def _check_applications(who: str, apps: Applications | None, problem) -> None:
    if apps is None:
        problem(f"{who}: how to apply not verified yet")
        return
    for missing, label in ((apps.url, "where to apply"), (apps.fee_cents, "the application fee"), (apps.documents, "documents")):
        if missing is None:
            problem(f"{who}: {label} not verified yet")
    if not apps.windows:
        problem(f"{who}: no application dates yet")


def _check_sources(who: str, sources: list[Source], today: date, problem, warnings: list[str]) -> None:
    for s in sources:
        if s.last_verified is None:
            problem(f"{who}/{s.id}: never verified")
        elif (today - s.last_verified).days > STALE_AFTER_DAYS:
            warnings.append(f"{who}/{s.id}: last verified {s.last_verified}, re-check it")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate university data packs and the national funding pack.")
    parser.add_argument("folder", nargs="?", default=str(ROOT / "data" / "universities"))
    parser.add_argument("--funding", default=str(FUNDING_PATH))
    args = parser.parse_args(argv)
    today = date.today()
    all_errors: list[str] = []
    results = [check(path, today) for path in sorted(Path(args.folder).glob("*.yaml"))]
    results.append(check_funding(Path(args.funding), today))
    for errors, warnings in results:
        for w in warnings:
            print(f"WARN  {w}")
        for e in errors:
            print(f"ERROR {e}")
        all_errors.extend(errors)
    print(f"{'FAILED' if all_errors else 'OK'}: {len(all_errors)} error(s)")
    return 1 if all_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
