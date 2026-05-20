"""Compatibility launcher for the packaged Polinko CLI.

`make chat` and `python main.py` are stable operator entrypoints. The CLI
implementation lives in `polinko.cli`.
"""

import os
import sys
from collections.abc import Callable
from pathlib import Path
from typing import NoReturn

_PROJECT_ROOT = Path(__file__).resolve().parent
_PROJECT_VENV_NAMES = (".venv", "venv")
_PROJECT_PYTHON_BINARIES = ("python3.14", "python", "python3")

__all__ = ["main"]


def _project_python_candidates() -> list[Path]:
    return [
        _PROJECT_ROOT / venv_name / "bin" / python_name
        for venv_name in _PROJECT_VENV_NAMES
        for python_name in _PROJECT_PYTHON_BINARIES
    ]


def _first_existing_project_python() -> Path | None:
    for candidate in _project_python_candidates():
        if candidate.exists():
            return candidate
    return None


def _missing_dependency_exit(exc: ModuleNotFoundError) -> NoReturn:
    project_python = _first_existing_project_python()
    current_prefix = Path(sys.prefix).resolve()
    project_venv = project_python.parents[1].resolve() if project_python else None
    if project_python is not None and current_prefix != project_venv:
        os.execv(str(project_python), [str(project_python), __file__, *sys.argv[1:]])

    missing = exc.name or "a required package"
    python_hint = (
        project_python.relative_to(_PROJECT_ROOT)
        if project_python is not None
        else Path(_PROJECT_VENV_NAMES[0]) / "bin" / _PROJECT_PYTHON_BINARIES[0]
    )
    activate_hint = (
        project_venv.relative_to(_PROJECT_ROOT)
        if project_venv is not None
        else Path(_PROJECT_VENV_NAMES[0])
    )
    raise SystemExit(
        f"Missing dependency: {missing}. "
        f"Use the project interpreter at {python_hint} "
        f"or run: source {activate_hint}/bin/activate"
    ) from exc


def _load_cli_main() -> Callable[[], None]:
    try:
        from polinko.cli import main as run_main
    except ModuleNotFoundError as exc:
        _missing_dependency_exit(exc)
    return run_main


def main() -> None:
    _load_cli_main()()


if __name__ == "__main__":
    main()
