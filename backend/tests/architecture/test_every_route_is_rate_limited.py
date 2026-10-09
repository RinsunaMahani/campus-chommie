"""
Every route has a rate limit (brief section 10), enforced.

Read with Python's own parser: any function decorated as a route on a
blueprint (api_bp.get, reset_page_bp.route, ...) must also carry
@limiter.limit(...). A new endpoint without one fails the build, so the
rule can't quietly decay one route at a time.
"""
from __future__ import annotations

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src"
ROUTE_METHODS = {"get", "post", "put", "patch", "delete", "route"}

#: Routes deliberately left without a limit, with the reason. Keep it empty.
EXEMPT: dict[str, str] = {}


def _routes():
    for path in sorted(SRC.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            route = None
            limited = False
            for deco in node.decorator_list:
                call = deco.func if isinstance(deco, ast.Call) else deco
                if not isinstance(call, ast.Attribute) or not isinstance(call.value, ast.Name):
                    continue
                if call.value.id.endswith("bp") and call.attr in ROUTE_METHODS:
                    route = ast.unparse(deco)
                if call.value.id == "limiter" and call.attr == "limit":
                    limited = True
            if route:
                yield path.relative_to(SRC.parent), node.name, route, limited


def test_every_route_has_a_rate_limit():
    missing = [f"{path}::{name}  {route}" for path, name, route, limited in _routes() if not limited and name not in EXEMPT]
    assert not missing, "These routes have no @limiter.limit (every route needs one):\n  " + "\n  ".join(missing)


def test_the_scan_finds_the_routes():
    """A scan that finds nothing would pass forever: make sure it sees the known routes."""
    found = {name for _, name, _, _ in _routes()}
    assert {"health", "me", "register", "login", "logout", "my_notifications"} <= found
