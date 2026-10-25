"""Validate every university data pack, the national funding pack (NSFAS and bursaries), the colleges pack
(public TVET colleges and DHET's registers) and the campus maps.

Errors (exit code 1, so CI fails): schema problems and broken references, plus
anything incomplete in a pack marked release: true.
Warnings: unverified programmes and application facts, and stale or missing
verification dates.

Usage: python scripts/validate_data.py [folder] [--funding path] [--colleges path] [--maps folder]
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from campus_engine.catalogue import (  # noqa: E402
    COLLEGES_PATH,
    FUNDING_PATH,
    MAPS_CONFIG,
    MAPS_DIR,
    DataPackError,
    load_colleges,
    load_funding,
    load_map,
    load_university,
)
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
    if not uni.programmes:
        problem(f"{uni.university}: no programmes yet")
    for p in uni.programmes:
        if p.requirements is None:
            problem(f"{uni.university}/{p.id}: requirements not verified yet")
    for section, label in (
        (uni.campuses, "campuses"), (uni.calendar, "calendar"), (uni.support_services, "support services"),
        (uni.cheap_things, "cheap things to do"),
    ):
        if not section:
            problem(f"{uni.university}: no {label} yet")
    _check_applications(uni.university, uni.applications, problem)
    _check_sources(uni.university, uni.sources, today, problem, warnings)
    return errors, warnings


def check_funding(path: Path, today: date, universities: set[str] | None = None) -> tuple[list[str], list[str]]:
    """`universities`: the ids a funder's study_at may name (every pack's id), when known."""
    errors: list[str] = []
    warnings: list[str] = []
    try:
        pack = load_funding(path)
    except DataPackError as exc:
        return [str(exc)], warnings

    def problem(message: str) -> None:
        (errors if pack.release else warnings).append(message)

    for f in pack.funders:
        if f.applying == "direct":  # an automatic award or university route has no dates or fee of its own
            _check_applications(f"funding/{f.id}", f.applications, problem)
        if f.who_can_apply is None:
            problem(f"funding/{f.id}: who can apply not verified yet")
        if universities is not None and f.study_at != "any":
            errors += [f"funding/{f.id}: study_at names unknown university '{u}'" for u in f.study_at if u not in universities]
    _check_sources("funding", pack.sources, today, problem, warnings)
    return errors, warnings


def check_colleges(path: Path, today: date) -> tuple[list[str], list[str]]:
    """The colleges pack loads (sources cited, TVET colleges known), and says what nobody has checked yet."""
    errors: list[str] = []
    warnings: list[str] = []
    try:
        pack = load_colleges(path)
    except DataPackError as exc:
        return [str(exc)], warnings

    def problem(message: str) -> None:
        (errors if pack.release else warnings).append(message)

    for c in pack.colleges:
        if c.kind != "tvet" and not c.registration_number:
            problem(f"colleges/{c.id}: the register shows no registration number")
    _check_sources("colleges", pack.sources, today, problem, warnings)
    return errors, warnings


def check_maps(folder: Path, today: date, campuses: dict[str, set[str]]) -> tuple[list[str], list[str]]:
    """Every campus map loads, names a university we have, and only campuses its pack lists.
    `campuses`: each university's campus ids."""
    errors: list[str] = []
    warnings: list[str] = []
    for path in sorted(folder.glob("*.yaml")):
        if path.name == MAPS_CONFIG or path.name.startswith("_"):
            continue
        try:
            umap = load_map(path)
        except DataPackError as exc:
            errors.append(str(exc))
            continue
        if umap.university not in campuses:
            errors.append(f"maps/{path.name}: no pack for university '{umap.university}'")
            continue
        for c in umap.campuses:
            if c.campus not in campuses[umap.university]:
                errors.append(f"maps/{umap.university}: unknown campus '{c.campus}'")

        def problem(message: str, umap=umap) -> None:
            (errors if umap.release else warnings).append(message)

        _check_sources(f"maps/{umap.university}", umap.sources, today, problem, warnings)
    return errors, warnings


def _campus_ids(folder: Path) -> dict[str, set[str]]:
    """Each pack's campus ids, by university (a broken pack reports its own error)."""
    found: dict[str, set[str]] = {}
    for path in sorted(folder.glob("*.yaml")):
        if not path.name.startswith("_"):
            try:
                uni = load_university(path)
            except DataPackError:
                continue
            found[uni.university] = {c.id for c in uni.campuses}
    return found


def _university_ids(folder: Path) -> set[str]:
    """The id of every pack that loads (a broken pack reports its own error)."""
    ids: set[str] = set()
    for path in sorted(folder.glob("*.yaml")):
        if not path.name.startswith("_"):
            try:
                ids.add(load_university(path).university)
            except DataPackError:
                pass
    return ids


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
    if not sources:
        problem(f"{who}: no sources")
    for s in sources:
        if not s.verified and s.last_verified is None:
            problem(f"{who}/{s.id}: never verified")
        elif not s.verified:
            problem(f"{who}/{s.id}: verification needs a named human reviewer, not an agent")
        elif s.evidence_date > today:
            problem(f"{who}/{s.id}: verification evidence is in the future")
        elif (today - s.evidence_date).days > STALE_AFTER_DAYS:
            problem(f"{who}/{s.id}: last verified {s.evidence_date}, re-check it")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate university data packs and the national funding pack.")
    parser.add_argument("folder", nargs="?", default=str(ROOT / "data" / "universities"))
    parser.add_argument("--funding", default=str(FUNDING_PATH))
    parser.add_argument("--colleges", default=str(COLLEGES_PATH))
    parser.add_argument("--maps", default=str(MAPS_DIR))
    args = parser.parse_args(argv)
    today = date.today()
    all_errors: list[str] = []
    results = [check(path, today) for path in sorted(Path(args.folder).glob("*.yaml"))]
    results.append(check_funding(Path(args.funding), today, _university_ids(Path(args.folder))))
    results.append(check_colleges(Path(args.colleges), today))
    results.append(check_maps(Path(args.maps), today, _campus_ids(Path(args.folder))))
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
