#!/usr/bin/env python3
"""Environment diagnostics for the Polinko repo."""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFERRED_VENV_NAMES = (".venv", "venv", "polinko-repositioning-system")
PREFERRED_PYTHON_NAMES = ("python3.14", "python3", "python")


def _ok(message: str) -> None:
    print(f"[ok]   {message}")


def _warn(message: str) -> None:
    print(f"[warn] {message}")


def _is_runnable_python(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        proc = subprocess.run(
            [str(path), "-V"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return False
    return proc.returncode == 0


def _expected_python_candidates(active_venv: str | None) -> list[Path]:
    roots: list[Path] = []
    seen: set[Path] = set()

    if active_venv:
        roots.append(Path(active_venv).expanduser())
    roots.extend(ROOT / name for name in PREFERRED_VENV_NAMES)

    candidates: list[Path] = []
    for root in roots:
        normalized_root = root.resolve()
        if normalized_root in seen:
            continue
        seen.add(normalized_root)
        for python_name in PREFERRED_PYTHON_NAMES:
            candidates.append(normalized_root / "bin" / python_name)
    return candidates


def _check_interpreter() -> int:
    issues = 0
    current_raw = Path(sys.executable)
    current = current_raw.resolve()
    active_venv = os.environ.get("VIRTUAL_ENV")
    expected_candidates = _expected_python_candidates(active_venv)
    runnable_candidates = [path for path in expected_candidates if _is_runnable_python(path)]

    if runnable_candidates:
        matching_candidate = next(
            (
                path
                for path in runnable_candidates
                if current_raw.resolve() == path.resolve() or current_raw == path
            ),
            None,
        )
        if matching_candidate is not None:
            _ok(f"Interpreter: {current_raw} (resolved: {current})")
        else:
            expected_raw = runnable_candidates[0]
            expected = expected_raw.resolve()
            issues += 1
            _warn(f"Interpreter mismatch: {current_raw} (resolved: {current})")
            _warn(f"Expected: {expected_raw} (resolved: {expected})")
            _warn(f"Use: source {expected_raw.parent / 'activate'}")
    else:
        _warn(
            "No runnable project venv interpreter found "
            "(common when host is macOS and venv was built in Linux container)."
        )
        _ok(f"Using host interpreter: {current_raw} (resolved: {current})")

    if active_venv:
        _ok(f"VIRTUAL_ENV={active_venv}")
    else:
        _warn("VIRTUAL_ENV is not set (ok when running via make with explicit interpreter)")

    python_on_path = shutil.which("python")
    if python_on_path:
        _ok(f"python on PATH: {python_on_path}")
    else:
        _warn("`python` is not on PATH (only `python3` may be available)")

    return issues


def _check_imports() -> int:
    issues = 0
    required_modules = [
        "agents",
        "openai",
        "fastapi",
        "uvicorn",
        "dotenv",
    ]
    for name in required_modules:
        if importlib.util.find_spec(name) is None:
            issues += 1
            _warn(f"Missing module: {name}")
        else:
            _ok(f"Import available: {name}")
    return issues


def _check_compaudit() -> int:
    issues = 0
    zsh_path = shutil.which("zsh")
    if not zsh_path:
        _warn("zsh not found; skipping compaudit check")
        return issues

    proc = subprocess.run(
        [zsh_path, "-lc", "autoload -Uz compaudit; compaudit"],
        capture_output=True,
        text=True,
        check=False,
    )
    output = (proc.stdout or "").strip()
    if output:
        issues += 1
        _warn("zsh reports insecure completion directories:")
        for line in output.splitlines():
            _warn(f"  {line}")
        _warn("Fix with: chmod g-w /opt/homebrew/share/zsh /opt/homebrew/share/zsh/site-functions")
    else:
        _ok("zsh compaudit: clean")
    return issues


def main() -> int:
    print("Polinko environment doctor")
    print(f"Repo root: {ROOT}")

    issues = 0
    issues += _check_interpreter()
    issues += _check_imports()
    issues += _check_compaudit()

    if issues:
        print(f"\nFound {issues} issue(s).")
        return 1

    print("\nEnvironment looks healthy.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
