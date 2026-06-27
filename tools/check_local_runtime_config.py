from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
VSCODE_CONFIG_FILES = (
    "settings.json",
    "extensions.json",
    "tasks.json",
    "mcp.json",
)
DEVCONTAINER_CONFIG_FILES = ("devcontainer.json",)
DEVCONTAINER_SETUP_SCRIPT = Path("tools/setup_devcontainer.sh")
DEVCONTAINER_BOOTSTRAP_DEFAULT = (
    'bootstrap_python="${POLINKO_DEVCONTAINER_BOOTSTRAP_PYTHON:-python3.14}"'
)
RETIRED_LOCAL_DOC_PATHS = (
    "docs/INSTANCE_HANDOFF.md",
    "docs/POL1_COMMS.md",
    "docs/AGENT_BUILDER_MIRROR.md",
    "docs/HYBRID_OPENAI_ADOPTION_PLAN.md",
    "docs/portfolio/raw_evidence",
)
RETIRED_VSCODE_EXTENSION_IDS = (
    "ms-python.pylint",
    "ms-python.isort",
    "ms-pyright.pyright",
    "donjayamanne.python-extension-pack",
    "kevinrose.vsc-python-indent",
    "mgesbert.python-path",
    "formulahendry.code-runner",
    "ritwickdey.liveserver",
    "batisteo.vscode-django",
    "bradlc.vscode-tailwindcss",
    "vue.volar",
    "github.copilot-chat",
    "ms-toolsai.jupyter",
    "ms-toolsai.datawrangler",
    "ms-vscode.cpptools-extension-pack",
    "vscode-arduino.vscode-arduino-community",
    "ms-vscode.powershell",
)


def _load_json(path: Path) -> tuple[Any | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except json.JSONDecodeError as exc:
        return None, f"{path}: invalid JSON: {exc.msg} at line {exc.lineno}"
    except OSError as exc:
        return None, f"{path}: cannot read file: {exc}"


def _task_name(task: dict[str, Any], index: int) -> str:
    label = task.get("label")
    if isinstance(label, str) and label.strip():
        return label.strip()
    return f"task #{index + 1}"


def _has_folder_open_run(task: dict[str, Any]) -> bool:
    run_options = task.get("runOptions")
    return isinstance(run_options, dict) and run_options.get("runOn") == "folderOpen"


def _has_empty_problem_matcher(task: dict[str, Any]) -> bool:
    problem_matcher = task.get("problemMatcher")
    return problem_matcher in (None, "", [])


def _contains_string(value: Any, needle: str) -> bool:
    if isinstance(value, str):
        return needle in value
    if isinstance(value, list):
        return any(_contains_string(item, needle) for item in value)
    if isinstance(value, dict):
        return any(
            (isinstance(key, str) and needle in key) or _contains_string(item, needle)
            for key, item in value.items()
        )
    return False


def _retired_local_doc_failures(path: Path, value: Any) -> list[str]:
    failures: list[str] = []
    for retired_path in RETIRED_LOCAL_DOC_PATHS:
        if _contains_string(value, retired_path):
            failures.append(
                f"{path}: retired local doc path {retired_path!r} is still referenced"
            )
    return failures


def _extension_ids(path: Path, value: Any, key: str) -> tuple[set[str], list[str]]:
    raw_extensions = value.get(key)
    if raw_extensions is None:
        return set(), []
    if not isinstance(raw_extensions, list):
        return set(), [f"{path}: {key} must be a list"]

    failures: list[str] = []
    extension_ids: set[str] = set()
    for index, raw_extension in enumerate(raw_extensions):
        if not isinstance(raw_extension, str):
            failures.append(
                f"{path}: {key}[{index}] must be a VS Code extension id string"
            )
            continue
        extension_id = raw_extension.strip().lower()
        if extension_id:
            extension_ids.add(extension_id)
    return extension_ids, failures


def _retired_extension_failures(
    path: Path, extension_ids: set[str], surface: str
) -> list[str]:
    failures: list[str] = []
    retired_extensions = set(RETIRED_VSCODE_EXTENSION_IDS)
    for extension_id in sorted(extension_ids & retired_extensions):
        failures.append(
            f"{path}: {surface} includes retired VS Code extension {extension_id!r}"
        )
    return failures


def _extensions_json_failures(path: Path, value: dict[str, Any]) -> list[str]:
    recommendations, recommendation_failures = _extension_ids(
        path, value, "recommendations"
    )
    unwanted, unwanted_failures = _extension_ids(path, value, "unwantedRecommendations")

    failures = [*recommendation_failures, *unwanted_failures]
    for extension_id in sorted(recommendations & unwanted):
        failures.append(
            f"{path}: extension {extension_id!r} is both recommended and unwanted"
        )
    failures.extend(
        _retired_extension_failures(path, recommendations, "recommendations")
    )

    missing_unwanted = set(RETIRED_VSCODE_EXTENSION_IDS) - unwanted
    for extension_id in sorted(missing_unwanted):
        failures.append(
            f"{path}: retired VS Code extension {extension_id!r} is missing from "
            "unwantedRecommendations"
        )
    return failures


def _devcontainer_extension_failures(path: Path, value: dict[str, Any]) -> list[str]:
    customizations = value.get("customizations")
    if not isinstance(customizations, dict):
        return []
    vscode = customizations.get("vscode")
    if not isinstance(vscode, dict):
        return []

    extension_ids, failures = _extension_ids(path, vscode, "extensions")
    return [
        *failures,
        *_retired_extension_failures(path, extension_ids, "devcontainer extensions"),
    ]


def check_vscode_config(root: Path = ROOT) -> list[str]:
    vscode_dir = root / ".vscode"
    if not vscode_dir.exists():
        return []

    failures: list[str] = []
    parsed: dict[str, Any] = {}
    for file_name in VSCODE_CONFIG_FILES:
        path = vscode_dir / file_name
        if not path.exists():
            continue
        value, failure = _load_json(path)
        if failure:
            failures.append(failure)
            continue
        if not isinstance(value, dict):
            failures.append(f"{path}: expected top-level JSON object")
            continue
        parsed[file_name] = value

    for file_name, value in parsed.items():
        failures.extend(_retired_local_doc_failures(vscode_dir / file_name, value))

    extensions_json = parsed.get("extensions.json")
    if extensions_json is not None:
        failures.extend(
            _extensions_json_failures(vscode_dir / "extensions.json", extensions_json)
        )

    tasks_json = parsed.get("tasks.json")
    if tasks_json is None:
        return failures

    tasks = tasks_json.get("tasks", [])
    if not isinstance(tasks, list):
        failures.append(f"{vscode_dir / 'tasks.json'}: tasks must be a list")
        return failures

    for index, raw_task in enumerate(tasks):
        if not isinstance(raw_task, dict):
            failures.append(
                f"{vscode_dir / 'tasks.json'}: task #{index + 1} must be an object"
            )
            continue

        name = _task_name(raw_task, index)
        command = raw_task.get("command")
        command_text = command.strip() if isinstance(command, str) else ""
        if "workspace bootstrap" in name.lower():
            failures.append(
                f"{vscode_dir / 'tasks.json'}: {name!r} is a retired task label"
            )
        if _has_folder_open_run(raw_task):
            failures.append(
                f"{vscode_dir / 'tasks.json'}: {name!r} uses retired folderOpen runOn"
            )
        if raw_task.get("isBackground") is True and _has_empty_problem_matcher(
            raw_task
        ):
            failures.append(
                f"{vscode_dir / 'tasks.json'}: {name!r} is background without a "
                "readiness problemMatcher"
            )
        if name == "make start" or command_text == "make start":
            if raw_task.get("isBackground") is True:
                failures.append(
                    f"{vscode_dir / 'tasks.json'}: 'make start' must be a "
                    "foreground manual task"
                )
            if _has_folder_open_run(raw_task):
                failures.append(
                    f"{vscode_dir / 'tasks.json'}: 'make start' must not run "
                    "on folder open"
                )

    return failures


def check_devcontainer_config(root: Path = ROOT) -> list[str]:
    devcontainer_dir = root / ".devcontainer"
    if not devcontainer_dir.exists():
        return []

    failures: list[str] = []
    for file_name in DEVCONTAINER_CONFIG_FILES:
        path = devcontainer_dir / file_name
        if not path.exists():
            continue
        value, failure = _load_json(path)
        if failure:
            failures.append(failure)
            continue
        if not isinstance(value, dict):
            failures.append(f"{path}: expected top-level JSON object")
            continue
        failures.extend(_retired_local_doc_failures(path, value))
        failures.extend(_devcontainer_extension_failures(path, value))

    return failures


def check_devcontainer_setup_script(root: Path = ROOT) -> list[str]:
    path = root / DEVCONTAINER_SETUP_SCRIPT
    if not path.exists():
        return []

    failures: list[str] = []
    text = path.read_text(encoding="utf-8")
    if DEVCONTAINER_BOOTSTRAP_DEFAULT not in text:
        failures.append(
            f"{path}: devcontainer bootstrap Python default must be python3.14"
        )
    if "POLINKO_DEVCONTAINER_BOOTSTRAP_PYTHON" not in text:
        failures.append(f"{path}: devcontainer bootstrap Python override is missing")
    if '"$venv_python" -m pip install --upgrade pip' not in text:
        failures.append(f"{path}: pip upgrade must run through venv_python")
    if '"$venv_python" -m pip install -r requirements.txt' not in text:
        failures.append(f"{path}: requirements install must run through venv_python")
    return failures


def run(root: Path = ROOT) -> list[str]:
    resolved_root = root.resolve()
    return [
        *check_vscode_config(resolved_root),
        *check_devcontainer_config(resolved_root),
        *check_devcontainer_setup_script(resolved_root),
    ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate ignored local runtime configuration that can affect "
            "startup and operator tasks."
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
    failures = run(args.root)
    if failures:
        print("[fail] local runtime config check found issue(s):", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    print("[ok] local runtime config check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
