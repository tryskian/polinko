import re
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.splitlines()


def _read_tracked_text(paths: list[str]) -> str:
    chunks: list[str] = []
    for rel_path in paths:
        try:
            chunks.append((REPO_ROOT / rel_path).read_text(encoding="utf-8"))
        except FileNotFoundError:
            continue
        except UnicodeDecodeError:
            continue
    return "\n".join(chunks)


def _current_runtime_reference_surfaces(tracked_files: list[str]) -> list[str]:
    surfaces: list[str] = []
    for rel_path in tracked_files:
        if rel_path == "Makefile" or rel_path.startswith(
            (
                "makefiles/",
                "tools/",
                ".github/",
                ".vscode/",
                ".devcontainer/",
            )
        ):
            surfaces.append(rel_path)
        elif rel_path in {"README.md", "pyproject.toml", ".pre-commit-config.yaml"}:
            surfaces.append(rel_path)
        elif rel_path.startswith(("docs/runtime/", "docs/public/")):
            surfaces.append(rel_path)
    return surfaces


def _referenced_tools(text: str) -> set[str]:
    path_refs = set(
        re.findall(r"(?:\./|\.\./)*(tools/[A-Za-z0-9_./-]+\.(?:py|sh))", text)
    )
    module_refs = {
        match.replace(".", "/") + ".py"
        for match in re.findall(
            r"(?:python\S*|PYTHON|\$\(PYTHON\)|\$\{PYTHON[^}]*\})"
            r"\s+-m\s+(tools\.[A-Za-z0-9_\.]+)",
            text,
        )
    }
    return path_refs | module_refs


def _referenced_tracked_tools(text: str, tracked_tools: set[str]) -> set[str]:
    return {ref for ref in _referenced_tools(text) if ref in tracked_tools}


def _test_visibility_tokens(tool_path: str) -> set[str]:
    path = Path(tool_path)
    tokens = {tool_path, path.name, path.stem}
    if tool_path.endswith(".py"):
        tokens.add(tool_path.removesuffix(".py").replace("/", "."))
    return tokens


class RuntimeToolReferenceCoverageTests(unittest.TestCase):
    def test_active_runtime_tool_references_exist(self) -> None:
        tracked_files = _tracked_files()
        reference_text = _read_tracked_text(
            _current_runtime_reference_surfaces(tracked_files)
        )

        missing_tools = [
            tool_path
            for tool_path in sorted(_referenced_tools(reference_text))
            if not (REPO_ROOT / tool_path).exists()
        ]

        self.assertEqual(
            missing_tools,
            [],
            "Active Make, CI, runtime, and tooling surfaces must not reference "
            "missing tools/*.py or tools/*.sh helpers.",
        )

    def test_referenced_runtime_tools_have_direct_test_visibility(self) -> None:
        tracked_files = _tracked_files()
        tracked_tools = {
            rel_path
            for rel_path in tracked_files
            if rel_path.startswith("tools/") and rel_path.endswith((".py", ".sh"))
        }
        reference_text = _read_tracked_text(
            _current_runtime_reference_surfaces(tracked_files)
        )
        test_text = _read_tracked_text(
            [
                rel_path
                for rel_path in tracked_files
                if rel_path.startswith("tests/test_") and rel_path.endswith(".py")
            ]
        )

        missing_visibility = [
            tool_path
            for tool_path in sorted(
                _referenced_tracked_tools(reference_text, tracked_tools)
            )
            if not any(
                token in test_text for token in _test_visibility_tokens(tool_path)
            )
        ]

        self.assertEqual(
            missing_visibility,
            [],
            "Tracked runtime tools referenced by active surfaces need direct test "
            "visibility by path, filename, stem, or module name.",
        )
