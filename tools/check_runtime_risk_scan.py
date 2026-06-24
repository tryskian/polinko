from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
RUNTIME_SURFACE_MAP = Path("docs/runtime/RUNTIME_SURFACE_MAP.md")
PRECOMMIT_CONFIG = Path(".pre-commit-config.yaml")

REQUIRED_FILES = (
    Path("Makefile"),
    Path("makefiles/build.mk"),
    Path("makefiles/checks.mk"),
    Path("makefiles/runtime.mk"),
    Path("makefiles/surfaces.mk"),
    Path("makefiles/evals/gates.mk"),
    Path("tools/start_of_day_routine.sh"),
    Path("tools/end_of_day_routine.sh"),
    Path("tools/repo_root.sh"),
    Path("tools/check_shell_scripts.py"),
    Path("tools/path_leak_check.py"),
    Path("tools/check_local_runtime_config.py"),
    Path("tools/check_runtime_risk_scan.py"),
    Path("tools/check_operator_aliases.py"),
    Path("tools/manage_caffeinate.sh"),
    Path("tools/run_server_daemon.sh"),
    Path("tools/run_eval_sidecar_start.sh"),
    Path("tools/run_portfolio_mockups.sh"),
    Path("tools/setup_devcontainer.sh"),
    Path("tools/local_privacy_guard.sh"),
    Path(".github/workflows/ci.yml"),
    Path(".github/workflows/dependency-review.yml"),
    Path(".github/dependabot.yml"),
    Path(".pre-commit-config.yaml"),
    RUNTIME_SURFACE_MAP,
)

REQUIRED_MAKE_TARGETS = (
    "start",
    "end",
    "end-preflight",
    "end-stop",
    "session-status",
    "pr-preflight",
    "ci",
    "ci-docs",
    "risk-scan",
    "operator-alias-check",
    "scripts-check",
    "path-leak-check",
    "path-leak-audit-local",
    "local-runtime-config-check",
    "api-smoke",
    "caffeinate",
    "caffeinate-status",
    "server-daemon",
    "server-daemon-status",
    "server-daemon-stop",
    "eval-sidecar-start",
    "eval-sidecar-status",
    "eval-sidecar-stop",
    "portfolio-mockups",
    "portfolio-mockups-status",
    "portfolio-mockups-stop",
    "privacy-local-on",
    "privacy-local-off",
)

FORBIDDEN_MAKE_TARGETS = ("eod-stop",)
FORBIDDEN_RUNTIME_MAP_TOKENS = ("Startup and workspace bootstrap",)
FORBIDDEN_PRECOMMIT_TOKENS = ("isort", "black")
REQUIRED_PRECOMMIT_EXCLUDE = r"^(docs/peanut/|public/portfolio/assets/)"
REQUIRED_PRECOMMIT_LOCAL_HOOKS = {
    "polinko-ruff-check": "make ruff-check",
    "polinko-ruff-format-check": "make ruff-format-check",
    "polinko-markdownlint-docs": "make lint-docs",
}

REQUIRED_CI_DOCS_DEPS = (
    "path-leak-check",
    "scripts-check",
    "local-runtime-config-check",
    "risk-scan",
    "operator-alias-check",
    "startup-contracts-check",
    "lint-docs",
)


@dataclass(frozen=True)
class MapSurface:
    name: str
    required_tokens: tuple[str, ...]


RUNTIME_MAP_SURFACES = (
    MapSurface(
        "startup",
        (
            "make start",
            "tools/start_of_day_routine.sh",
            "tools/repo_root.sh",
            "make doctor-env",
            "make caffeinate",
            "make api-smoke",
            "alignment pause",
        ),
    ),
    MapSurface(
        "closeout",
        (
            "make end-preflight",
            "make end",
            "tools/repo_root.sh",
            "make end-stop",
            "make session-status",
            "make scripts-check",
            "make path-leak-check",
            "make risk-scan",
            "make end-git-check",
        ),
    ),
    MapSurface(
        "background runners",
        (
            "server-daemon",
            "eval-sidecar",
            "portfolio mockups",
            "repo-managed caffeinate",
            "PID",
            "cleanup",
        ),
    ),
    MapSurface(
        "manual eval and OCR tooling",
        (
            "manual eval workbench",
            "manual_evals_db_health",
            "read-only OCR inventory",
            "operator-alias-check",
            "Make eval aliases",
            "OCR workflow wrappers",
        ),
    ),
    MapSurface(
        "CI and dependency automation",
        (
            "GitHub Actions",
            "Dependabot",
            "dependency-review",
            "pip-audit",
            "npm audit",
        ),
    ),
    MapSurface(
        "hidden local config",
        (
            "make path-leak-audit-local",
            "make local-runtime-config-check",
            "tools.check_local_runtime_config",
            "VS Code",
            "devcontainer",
            "tools/repo_root.sh",
            "pre-commit",
            "privacy-local-on",
        ),
    ),
)


def makefile_text(root: Path, path: Path = Path("Makefile")) -> str:
    return _makefile_source_text(root, path, set())


def _makefile_source_text(root: Path, path: Path, seen: set[Path]) -> str:
    absolute = (root / path).resolve()
    if absolute in seen:
        return ""
    seen.add(absolute)

    text = absolute.read_text(encoding="utf-8")
    parts = [text]
    for match in re.finditer(r"^include\s+(.+)$", text, re.MULTILINE):
        for include_path in match.group(1).split():
            parts.append(_makefile_source_text(root, Path(include_path), seen))
    return "\n".join(parts)


def make_targets(text: str) -> set[str]:
    targets: set[str] = set()
    for line in text.splitlines():
        if not line or line.startswith(("\t", "#")) or ":" not in line:
            continue
        head = line.split(":", 1)[0].strip()
        if not head or any(marker in head for marker in ("=", "$", "(")):
            continue
        targets.update(head.split())
    return targets


def ci_docs_deps(text: str) -> tuple[str, ...]:
    match = re.search(r"(?m)^ci-docs:\s*(?P<deps>.+)$", text)
    if not match:
        return ()
    return tuple(match.group("deps").split())


def check_required_files(root: Path) -> list[str]:
    failures: list[str] = []
    for path in REQUIRED_FILES:
        absolute = root / path
        if not absolute.exists():
            failures.append(f"{path}: missing required runtime/tooling surface")
    return failures


def check_make_contracts(text: str) -> list[str]:
    failures: list[str] = []
    targets = make_targets(text)
    for target in REQUIRED_MAKE_TARGETS:
        if target not in targets:
            failures.append(f"make target {target!r}: missing from Make surface")
    for target in FORBIDDEN_MAKE_TARGETS:
        if target in targets:
            failures.append(f"make target {target!r}: deprecated target is active")

    deps = ci_docs_deps(text)
    if not deps:
        failures.append("ci-docs: missing Make target")
    else:
        for dep in REQUIRED_CI_DOCS_DEPS:
            if dep not in deps:
                failures.append(f"ci-docs: missing dependency {dep!r}")
    return failures


def check_runtime_surface_map(root: Path) -> list[str]:
    text = (root / RUNTIME_SURFACE_MAP).read_text(encoding="utf-8")
    failures: list[str] = []
    for token in FORBIDDEN_RUNTIME_MAP_TOKENS:
        if token in text:
            failures.append(
                f"{RUNTIME_SURFACE_MAP}: retired runtime map token {token!r} is active"
            )
    for surface in RUNTIME_MAP_SURFACES:
        for token in surface.required_tokens:
            if token not in text:
                failures.append(
                    f"{RUNTIME_SURFACE_MAP}: {surface.name} omits {token!r}"
                )
    return failures


def _strip_yaml_quotes(value: str) -> str:
    stripped = value.strip()
    if len(stripped) >= 2 and stripped[0] == stripped[-1] and stripped[0] in {"'", '"'}:
        return stripped[1:-1]
    return stripped


def _precommit_scalar(value: str) -> str | bool | list[str]:
    stripped = _strip_yaml_quotes(value)
    if stripped.lower() == "false":
        return False
    if stripped.lower() == "true":
        return True
    if stripped.startswith("[") and stripped.endswith("]"):
        return [
            _strip_yaml_quotes(item)
            for item in stripped[1:-1].split(",")
            if item.strip()
        ]
    return stripped


def _precommit_local_hooks(text: str) -> dict[str, dict[str, str | bool | list[str]]]:
    hooks: dict[str, dict[str, str | bool | list[str]]] = {}
    in_local_repo = False
    in_hooks = False
    current_hook: dict[str, str | bool | list[str]] | None = None

    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- repo:"):
            in_local_repo = stripped == "- repo: local"
            in_hooks = False
            current_hook = None
            continue
        if not in_local_repo:
            continue
        if stripped == "hooks:":
            in_hooks = True
            continue
        if not in_hooks:
            continue
        if stripped.startswith("- id:"):
            hook_id = _strip_yaml_quotes(stripped.split(":", 1)[1])
            current_hook = {}
            hooks[hook_id] = current_hook
            continue
        if current_hook is not None and ":" in stripped:
            key, raw_value = stripped.split(":", 1)
            current_hook[key.strip()] = _precommit_scalar(raw_value)

    return hooks


def check_precommit_config(root: Path) -> list[str]:
    path = root / PRECOMMIT_CONFIG
    failures: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"{PRECOMMIT_CONFIG}: cannot read file: {exc}"]
    for token in FORBIDDEN_PRECOMMIT_TOKENS:
        if token in text:
            failures.append(
                f"{PRECOMMIT_CONFIG}: retired hook token {token!r} is active"
            )

    exclude_match = re.search(r"(?m)^exclude:\s*(?P<exclude>.+)$", text)
    exclude = (
        _strip_yaml_quotes(exclude_match.group("exclude")) if exclude_match else ""
    )
    if exclude != REQUIRED_PRECOMMIT_EXCLUDE:
        failures.append(
            f"{PRECOMMIT_CONFIG}: exclude must be {REQUIRED_PRECOMMIT_EXCLUDE!r}"
        )

    hooks_by_id = _precommit_local_hooks(text)
    if not hooks_by_id:
        failures.append(f"{PRECOMMIT_CONFIG}: missing local repo hooks")
        return failures

    for hook_id, entry in REQUIRED_PRECOMMIT_LOCAL_HOOKS.items():
        hook = hooks_by_id.get(hook_id)
        if hook is None:
            failures.append(f"{PRECOMMIT_CONFIG}: missing local hook {hook_id!r}")
            continue
        if hook.get("entry") != entry:
            failures.append(f"{PRECOMMIT_CONFIG}: {hook_id!r} entry must be {entry!r}")
        if hook.get("language") != "system":
            failures.append(f"{PRECOMMIT_CONFIG}: {hook_id!r} must use system language")
        if hook.get("pass_filenames") is not False:
            failures.append(f"{PRECOMMIT_CONFIG}: {hook_id!r} must not pass filenames")
        stages = hook.get("stages")
        if not isinstance(stages, list) or {
            "pre-commit",
            "manual",
        } - set(stages):
            failures.append(
                f"{PRECOMMIT_CONFIG}: {hook_id!r} must run at pre-commit and manual stages"
            )

    return failures


def scan(root: Path = ROOT) -> list[str]:
    text = makefile_text(root)
    failures: list[str] = []
    failures.extend(check_required_files(root))
    failures.extend(check_make_contracts(text))
    failures.extend(check_runtime_surface_map(root))
    failures.extend(check_precommit_config(root))
    return failures


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate that known high-risk runtime, script, CI, and local "
            "configuration surfaces remain visible in tracked gates and docs."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="repository root to scan; defaults to this checkout",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    failures = scan(args.root.resolve())
    if failures:
        print("[fail] runtime risk scan found issue(s):", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    print("[ok] runtime risk scan passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
