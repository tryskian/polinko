from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

SHELL_LIBRARIES = {
    Path("tools/eval_case_guard.sh"): "eval_case_guard_or_exit",
    Path("tools/make_runtime.sh"): "polinko_make_bin",
    Path("tools/ocr_workflow_common.sh"): "ocr_workflow_use_eval_case_guard",
    Path("tools/process_lifecycle_common.sh"): "polinko_pid_is_running",
    Path("tools/python_runtime.sh"): "polinko_default_python_bin",
    Path("tools/shell_command_common.sh"): "polinko_command_available",
}
ROOT_HELPER_EXEMPT_EXECUTABLES = {
    Path("tools/open_local_url.sh"),
    Path("tools/repo_root.sh"),
}
SOURCE_LIBRARY_EXEMPTIONS = {
    Path("tools/repo_root.sh"),
}
ROOT_HELPER_SNIPPETS = (
    'source "$script_dir/repo_root.sh"',
    "polinko_cd_repo_root",
)
ROOT_HELPER_SCRIPT_DIR_SNIPPETS = (
    'script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"',
    'script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)',
)

EXECUTABLE_STRICT_MODE = {
    "#!/usr/bin/env bash": "set -euo pipefail",
    "#!/usr/bin/env sh": "set -eu",
}
SHELL_PARSERS = {
    "#!/usr/bin/env bash": "bash",
    "#!/usr/bin/env sh": "sh",
}
SCRIPT_DIR_SOURCE_RE = re.compile(
    r"""(?mx)
    ^\s*
    (?:source|\.)
    \s+
    (?P<quote>["']?)
    \$script_dir/
    (?P<name>[^"'\s]+\.sh)
    (?P=quote)
    (?:\s|$)
    """
)
QUOTED_HEREDOC_START_RE = re.compile(
    r"""
    <<(?P<strip_tabs>-?)\s*
    (?P<quote>['"])
    (?P<marker>[A-Za-z_][A-Za-z0-9_]*)
    (?P=quote)
    """,
    re.VERBOSE,
)


def legacy_backtick_failures(
    lines: list[str], *, make_recipe_tabs: bool = False
) -> list[str]:
    failures: list[str] = []
    quoted_heredoc_marker: str | None = None
    quoted_heredoc_strips_tabs = False

    for line_number, line in enumerate(lines, start=1):
        if quoted_heredoc_marker is not None:
            terminator = (
                line.lstrip("\t")
                if quoted_heredoc_strips_tabs or make_recipe_tabs
                else line
            )
            if terminator == quoted_heredoc_marker:
                quoted_heredoc_marker = None
                quoted_heredoc_strips_tabs = False
            continue

        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue

        if "`" in line:
            failures.append(
                f"line {line_number} uses legacy backtick command substitution; "
                "use $(...)"
            )

        heredoc_match = QUOTED_HEREDOC_START_RE.search(line)
        if heredoc_match is not None:
            quoted_heredoc_marker = heredoc_match.group("marker")
            quoted_heredoc_strips_tabs = bool(heredoc_match.group("strip_tabs"))

    return failures


def tracked_shell_scripts() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "tools"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [Path(path) for path in result.stdout.splitlines() if path.endswith(".sh")]


def tracked_makefiles() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "Makefile", "makefiles"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [
        Path(path)
        for path in result.stdout.splitlines()
        if path == "Makefile" or path.endswith(".mk")
    ]


def shell_syntax_failure(path: Path, shebang: str) -> str | None:
    parser = SHELL_PARSERS[shebang]
    try:
        result = subprocess.run(
            [parser, "-n", str(REPO_ROOT / path)],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return f"cannot run {parser!r} syntax parser"

    if result.returncode == 0:
        return None

    detail = " ".join((result.stderr or result.stdout).split())
    if detail:
        return f"fails {parser} syntax check: {detail}"
    return f"fails {parser} syntax check with exit code {result.returncode}"


def sourced_shell_paths(shell_scripts: list[Path]) -> set[Path]:
    sourced: set[Path] = set()
    for path in shell_scripts:
        text = (REPO_ROOT / path).read_text(encoding="utf-8")
        for match in SCRIPT_DIR_SOURCE_RE.finditer(text):
            sourced.add(Path("tools") / match.group("name"))
    return sourced


def unregistered_sourced_shell_libraries(shell_scripts: list[Path]) -> set[Path]:
    registered = set(SHELL_LIBRARIES) | SOURCE_LIBRARY_EXEMPTIONS
    return sourced_shell_paths(shell_scripts) - registered


def check_script(path: Path) -> list[str]:
    text = (REPO_ROOT / path).read_text(encoding="utf-8")
    lines = text.splitlines()
    failures: list[str] = []

    if "\r\n" in text:
        failures.append("uses CRLF line endings")

    if not lines:
        return ["is empty"]

    shebang = lines[0]
    if shebang not in EXECUTABLE_STRICT_MODE:
        failures.append(
            "uses unsupported shebang "
            f"{shebang!r}; expected one of {sorted(EXECUTABLE_STRICT_MODE)}"
        )
        return failures

    syntax_failure = shell_syntax_failure(path, shebang)
    if syntax_failure is not None:
        failures.append(syntax_failure)

    failures.extend(legacy_backtick_failures(lines))

    if path in SHELL_LIBRARIES:
        function_name = SHELL_LIBRARIES[path]
        direct_execution_guard = f'if [ "${{0##*/}}" = "{path.name}" ]; then'
        if f"{function_name}()" not in text:
            failures.append(f"does not define {function_name}()")
        if direct_execution_guard not in text:
            failures.append("does not guard direct execution")
        return failures

    expected_strict_mode = EXECUTABLE_STRICT_MODE[shebang]
    if len(lines) < 2 or lines[1] != expected_strict_mode:
        failures.append(
            f"does not enable strict mode on line 2 ({expected_strict_mode!r})"
        )

    if path not in ROOT_HELPER_EXEMPT_EXECUTABLES:
        if not any(snippet in text for snippet in ROOT_HELPER_SCRIPT_DIR_SNIPPETS):
            failures.append("does not include root-helper script_dir resolver")
        for snippet in ROOT_HELPER_SNIPPETS:
            if snippet not in text:
                failures.append(f"does not include root-helper snippet {snippet!r}")

    return failures


def check_makefile(path: Path) -> list[str]:
    text = (REPO_ROOT / path).read_text(encoding="utf-8")
    failures: list[str] = []

    if "\r\n" in text:
        failures.append("uses CRLF line endings")

    failures.extend(legacy_backtick_failures(text.splitlines(), make_recipe_tabs=True))

    return failures


def main() -> int:
    failures: list[str] = []
    shell_scripts = tracked_shell_scripts()
    makefiles = tracked_makefiles()

    if not shell_scripts:
        failures.append("no tracked tools/*.sh scripts found")

    tracked = set(shell_scripts)
    for path in sorted(sourced_shell_paths(shell_scripts) - tracked):
        failures.append(f"{path}: is sourced but is not a tracked tools/*.sh script")

    for path in sorted(unregistered_sourced_shell_libraries(shell_scripts)):
        failures.append(
            f"{path}: is sourced by another shell script but is not registered "
            "in SHELL_LIBRARIES"
        )

    for path in shell_scripts:
        for failure in check_script(path):
            failures.append(f"{path}: {failure}")

    for path in makefiles:
        for failure in check_makefile(path):
            failures.append(f"{path}: {failure}")

    if failures:
        print("shell-script-contracts: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(
        "shell-script-contracts: PASS "
        f"({len(shell_scripts)} scripts, {len(makefiles)} Make files checked)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
