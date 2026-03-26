from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    details: str


REPO_ROOT = Path(__file__).resolve().parent.parent
README_PATH = REPO_ROOT / "README.md"
MAKEFILE_PATH = REPO_ROOT / "Makefile"
APP_FACTORY_PATH = REPO_ROOT / "api" / "app_factory.py"
PACKAGE_JSON_PATH = REPO_ROOT / "package.json"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_app_routes(text: str) -> set[str]:
    pattern = re.compile(r'@app\.(get|post|patch|delete)\("([^"]+)"')
    return {f"{method.upper()} {path}" for method, path in pattern.findall(text)}


def _extract_readme_routes(text: str) -> set[str]:
    pattern = re.compile(r"^- `([A-Z]+) ([^`]+)`$", flags=re.MULTILINE)
    return {f"{method} {path}" for method, path in pattern.findall(text)}


def _extract_make_tools_modules(text: str) -> list[str]:
    modules: set[str] = set()
    for line in text.splitlines():
        if "$(PYTHON) -m tools." not in line:
            continue
        match = re.search(r"\$\(PYTHON\)\s+-m\s+tools\.([a-zA-Z0-9_]+)", line)
        if match:
            modules.add(match.group(1))
    return sorted(modules)


def _load_package_scripts() -> dict[str, str]:
    payload = json.loads(_read_text(PACKAGE_JSON_PATH))
    scripts = payload.get("scripts", {})
    if not isinstance(scripts, dict):
        return {}
    return {str(key): str(value) for key, value in scripts.items()}


def _format_missing(items: Iterable[str], *, limit: int = 8) -> str:
    collected = sorted(items)
    if not collected:
        return ""
    if len(collected) <= limit:
        return ", ".join(collected)
    head = ", ".join(collected[:limit])
    return f"{head}, ... (+{len(collected) - limit} more)"


def check_readme_route_parity() -> CheckResult:
    app_routes = _extract_app_routes(_read_text(APP_FACTORY_PATH))
    readme_routes = _extract_readme_routes(_read_text(README_PATH))
    missing_from_readme = app_routes - readme_routes
    stale_in_readme = readme_routes - app_routes
    if missing_from_readme or stale_in_readme:
        detail_parts: list[str] = []
        if missing_from_readme:
            detail_parts.append(f"missing from README: {_format_missing(missing_from_readme)}")
        if stale_in_readme:
            detail_parts.append(f"stale in README: {_format_missing(stale_in_readme)}")
        return CheckResult(
            name="readme_route_parity",
            ok=False,
            details="; ".join(detail_parts),
        )
    return CheckResult(
        name="readme_route_parity",
        ok=True,
        details=f"{len(app_routes)} routes matched",
    )


def check_make_tool_module_existence() -> CheckResult:
    modules = _extract_make_tools_modules(_read_text(MAKEFILE_PATH))
    missing: list[str] = []
    for module in modules:
        path = REPO_ROOT / "tools" / f"{module}.py"
        if not path.exists():
            missing.append(f"tools/{module}.py")
    if missing:
        return CheckResult(
            name="make_tool_module_existence",
            ok=False,
            details=f"missing modules: {_format_missing(missing)}",
        )
    return CheckResult(
        name="make_tool_module_existence",
        ok=True,
        details=f"{len(modules)} tool modules resolved",
    )


def check_lint_docs_parity() -> CheckResult:
    scripts = _load_package_scripts()
    lint_cmd = scripts.get("lint:docs", "")
    wants_readme = "README.md" in lint_cmd
    wants_docs_glob = "docs/**/*.md" in lint_cmd
    if not wants_readme or not wants_docs_glob:
        return CheckResult(
            name="lint_docs_parity",
            ok=False,
            details=f"lint:docs must include README.md and docs/**/*.md; got: {lint_cmd!r}",
        )
    return CheckResult(
        name="lint_docs_parity",
        ok=True,
        details=f"lint:docs => {lint_cmd}",
    )


def check_eval_cleanup_guard() -> CheckResult:
    text = _read_text(MAKEFILE_PATH)
    has_target = re.search(r"^eval-cleanup:\s*$", text, flags=re.MULTILINE) is not None
    has_guard = "tools/cleanup_eval_chats.py is local-only and not tracked in this repo." in text
    if not has_target:
        return CheckResult(
            name="eval_cleanup_guard",
            ok=True,
            details="eval-cleanup target not present",
        )
    if has_guard:
        return CheckResult(
            name="eval_cleanup_guard",
            ok=True,
            details="local-only guard present",
        )
    return CheckResult(
        name="eval_cleanup_guard",
        ok=False,
        details="eval-cleanup target exists without local-only guard",
    )


def run_checks() -> list[CheckResult]:
    return [
        check_readme_route_parity(),
        check_make_tool_module_existence(),
        check_lint_docs_parity(),
        check_eval_cleanup_guard(),
    ]


def main() -> int:
    results = run_checks()
    failures = [result for result in results if not result.ok]

    print("Polinko build-block audit")
    for result in results:
        status = "OK" if result.ok else "FAIL"
        print(f"- [{status}] {result.name}: {result.details}")

    if failures:
        print(f"\nAudit failed: {len(failures)} check(s) failed.")
        return 1

    print(f"\nAudit passed: {len(results)} check(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
