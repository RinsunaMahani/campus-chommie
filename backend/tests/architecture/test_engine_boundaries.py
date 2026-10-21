"""
The engine stays pure, enforced.

campus_engine does the thinking (matching, plans, workload, runway,
forecasts, extraction) and nothing else: no web, no database, no app
code. That is what lets the same functions serve the API, the WhatsApp
bot and plain tests, and what keeps every result explainable from its
inputs alone. Services call the engine; the engine never calls back.

Read with Python's own parser (not a text search), so aliased,
multi-line and in-function imports are all caught, while the same words
in a docstring are not.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Iterator, List, Tuple

ENGINE = Path(__file__).resolve().parents[2] / "campus_engine"

# Named, so a failure says WHICH boundary was crossed and why it matters.
FORBIDDEN = {
    "src": "The engine must not know the app. Services call the engine, never the reverse.",
    "flask": "No web framework in the engine: it must run the same in a request, a job or a test.",
    "werkzeug": "No web framework in the engine.",
    "marshmallow": "Request validation belongs to the API layer; the engine validates data packs with pydantic.",
    "sqlalchemy": "The engine never reads or writes the database: services pass it the data.",
    "flask_sqlalchemy": "The engine never reads or writes the database.",
    "alembic": "The engine never touches the database.",
    "psycopg2": "The engine never touches the database.",
}

# Everything the engine may import besides the standard library and itself.
ALLOWED_THIRD_PARTY = {"pydantic", "yaml"}


def _engine_files() -> List[Path]:
    files = sorted(p for p in ENGINE.rglob("*.py") if "__pycache__" not in p.parts)
    assert files, f"campus_engine not found at {ENGINE}"
    return files


def _imports(path: Path) -> Iterator[Tuple[str, int]]:
    """Every absolute module name `path` imports, with its line number.
    Relative imports (from .points import ...) stay inside the engine."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name, node.lineno
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            yield node.module, node.lineno


def _top(module: str) -> str:
    return module.split(".")[0]


def test_engine_never_imports_the_app_the_web_or_the_database():
    violations = []
    for path in _engine_files():
        for module, line in _imports(path):
            reason = FORBIDDEN.get(_top(module))
            if reason or _top(module).startswith("flask_"):
                rel = path.relative_to(ENGINE.parent)
                violations.append(f"\n  {rel}:{line} imports {module}\n    -> {reason or FORBIDDEN['flask']}")
    assert not violations, "ARCHITECTURE VIOLATION -- campus_engine crossed its boundary:" + "".join(violations)


def test_engine_only_imports_the_standard_library_pydantic_and_yaml():
    """Stricter companion: anything new is excluded by default, so a
    dependency added next month has to be argued for here first."""
    allowed = set(sys.stdlib_module_names) | ALLOWED_THIRD_PARTY | {"campus_engine"}
    violations = []
    for path in _engine_files():
        for module, line in _imports(path):
            if _top(module) not in allowed:
                violations.append(f"\n  {path.relative_to(ENGINE.parent)}:{line} imports {module}")
    assert not violations, (
        "campus_engine imported something outside its allowed surface"
        f" (standard library, {', '.join(sorted(ALLOWED_THIRD_PARTY))}):" + "".join(violations)
    )


def test_routes_never_call_the_engine():
    """Services call the engine; routes never do (CLAUDE.md). A route validates, calls one
    service and answers, so each rule lives in one place and is tested there."""
    src = ENGINE.parent / "src"
    violations = []
    for path in sorted(p for p in src.rglob("*.py") if "__pycache__" not in p.parts):
        if "api" not in path.relative_to(src).parts:
            continue
        for module, line in _imports(path):
            if _top(module) == "campus_engine":
                violations.append(f"\n  {path.relative_to(src.parent)}:{line} imports {module}")
    assert not violations, "Routes must reach the engine through a service:" + "".join(violations)


def test_the_boundary_test_would_catch_a_violation(tmp_path):
    """The parser really sees imports, including ones hidden inside a function."""
    sample = tmp_path / "sample.py"
    sample.write_text("def f():\n    from src.extensions import db\n    import flask_limiter\n", encoding="utf-8")
    assert [m for m, _ in _imports(sample)] == ["src.extensions", "flask_limiter"]
