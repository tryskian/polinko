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
EXPECTED_VENV = ROOT / "polinko-repositioning-system"
EXPECTED_PYTHON = EXPECTED_VENV / "bin" / "python"
ALT_EXPECTED_PYTHON = ROOT / "venv" / "bin" / "python"


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


def _check_interpreter() -> int:
    issues = 0
    current_raw = Path(sys.executable)
    current = current_raw.resolve()
    expected_candidates = [EXPECTED_PYTHON, ALT_EXPECTED_PYTHON]
    runnable_candidates = [path for path in expected_candidates if _is_runnable_python(path)]

    if runnable_candidates:
        expected_raw = runnable_candidates[0]
        expected = expected_raw.resolve()
        if current == expected:
            _ok(f"Interpreter: {current_raw} (resolved: {current})")
        else:
            issues += 1
            _warn(f"Interpreter mismatch: {current_raw} (resolved: {current})")
            _warn(f"Expected: {expected_raw} (resolved: {expected})")
            _warn("Use: source polinko-repositioning-system/bin/activate")
    else:
        _warn(
            "No runnable project venv interpreter found "
            "(common when host is macOS and venv was built in Linux container)."
        )
        _ok(f"Using host interpreter: {current_raw} (resolved: {current})")

    active_venv = os.environ.get("VIRTUAL_ENV")
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
