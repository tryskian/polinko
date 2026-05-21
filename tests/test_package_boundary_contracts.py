import ast
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ACTIVE_FILE_EXTENSIONS = {".py", ".sh", ".mk"}
ACTIVE_ROOT_FILES = {"Makefile", "Dockerfile", "pyproject.toml"}
RETIRED_ROOT_IMPORTS = ("api", "config", "core")
RETIRED_ROOT_SURFACES = ("app.py", "config.py", "api", "core")


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def _tracked_files(*patterns: str) -> list[str]:
    command = ["git", "ls-files", *patterns]
    return subprocess.check_output(command, cwd=REPO_ROOT, text=True).splitlines()


def _active_tracked_paths() -> list[str]:
    return [
        path
        for path in _tracked_files()
        if Path(path).suffix in ACTIVE_FILE_EXTENSIONS or path in ACTIVE_ROOT_FILES
    ]


def _retired_root_import_mentions(
    root_name: str,
    *,
    allowed_paths: set[str],
) -> list[str]:
    mentions = []
    dynamic_import_markers = (
        f'import_module("{root_name}.',
        f"import_module('{root_name}.",
        f'__import__("{root_name}"',
        f"__import__('{root_name}'",
    )

    for relative_path in _active_tracked_paths():
        if relative_path in allowed_paths:
            continue
        if not (REPO_ROOT / relative_path).exists():
            continue
        source = _read(relative_path)
        if Path(relative_path).suffix == ".py":
            tree = ast.parse(source, filename=relative_path)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.split(".", maxsplit=1)[0] == root_name:
                            mentions.append(f"{relative_path}:{node.lineno}")
                elif isinstance(node, ast.ImportFrom) and node.module is not None:
                    if node.module.split(".", maxsplit=1)[0] == root_name:
                        mentions.append(f"{relative_path}:{node.lineno}")

        if any(marker in source for marker in dynamic_import_markers):
            mentions.append(relative_path)

    return mentions


class PackageBoundaryContractTests(unittest.TestCase):
    def test_package_boundary_doc_names_current_and_target_shapes(self) -> None:
        boundary = _read("docs/runtime/PACKAGE_BOUNDARY.md")

        for expected in (
            "Tracked root compatibility launchers",
            "`main.py`",
            "compatibility launcher for `python main.py`",
            "legacy root `app.py` launcher is retired",
            "`server.py`",
            "compatibility shim for `uvicorn server:app`",
            "`src/polinko/cli.py`",
            "canonical CLI chat implementation",
            "`src/polinko/asgi.py`",
            "canonical ASGI app construction",
            "`polinko-chat`",
            "legacy root `config.py` import shim is retired",
            "legacy root `api/` import shims are retired",
            "legacy root `core/` import shims are retired",
            "The runtime import package is `polinko` under `src/polinko/`.",
            "`src/polinko/config.py`",
            "`src/polinko/api/`",
            "`src/polinko/core/`",
            "root `tools/`",
            "Keep `polinko-chat` as the installed console-script entrypoint.",
            "Keep runtime modules under `src/polinko/`",
            "Do not change ASGI import compatibility for `server:app`.",
        ):
            self.assertIn(expected, boundary)

    def test_package_boundary_doc_records_root_compatibility_audit(self) -> None:
        boundary = _read("docs/runtime/PACKAGE_BOUNDARY.md")

        for expected in (
            "## Current Boundary",
            "active runtime and tool imports should use `polinko.*`",
            "remaining root compatibility surfaces are launchers, not import shims",
            "compatibility launcher retirement must happen through",
            "active `server:app` references still exist in Docker",
            "legacy `app.py` launcher is retired",
            "legacy root `config.py` import shim is retired",
            "### Readiness Snapshot: 2026-05-20",
            "retired in a separate deprecation/removal kernel",
            "not retirement-ready",
            "`server.py`",
            "Make defaults, server-daemon, local eval gates, Docker",
            "`config.py`",
            "focused local ignored-lane search found no legacy root import usage",
            "`api/`",
            "replacement imports use `polinko.api.*`",
            "`core/`",
            "replacement imports use `polinko.core.*`",
        ):
            self.assertIn(expected, boundary)

    def test_architecture_and_state_link_package_boundary(self) -> None:
        architecture = _read("docs/runtime/ARCHITECTURE.md")
        state = _read("docs/governance/STATE.md")
        docs_index = _read("docs/README.md")
        decisions = _read("docs/governance/DECISIONS.md")

        self.assertIn("docs/runtime/PACKAGE_BOUNDARY.md", architecture)
        self.assertIn("`PACKAGE_BOUNDARY`", architecture)
        self.assertIn("package-boundary contract is documented", state)
        self.assertIn("legacy root `api/` has been retired", state)
        self.assertIn("legacy root `core/` has been retired", state)
        self.assertIn("`PACKAGE_BOUNDARY` holds the Python", state)
        self.assertIn("docs/runtime/PACKAGE_BOUNDARY.md", docs_index)
        self.assertIn(
            "## D-044: Preflight the Python package boundary before moving imports",
            decisions,
        )
        self.assertIn(
            "## D-045: Add the editable-install rail before moving runtime imports",
            decisions,
        )
        self.assertIn(
            "## D-046: Move config into the Python package first",
            decisions,
        )
        self.assertIn(
            "## D-047: Move API implementation into the Python package",
            decisions,
        )
        self.assertIn(
            "## D-048: Move core runtime into the Python package",
            decisions,
        )
        self.assertIn(
            "## D-049: Package the CLI implementation behind stable launchers",
            decisions,
        )
        self.assertIn(
            "## D-050: Package ASGI app construction behind server compatibility",
            decisions,
        )
        self.assertIn(
            "## D-051: Keep audited root shims compatibility-only",
            decisions,
        )
        self.assertIn(
            "## D-060: Audit root shim retirement readiness before deletion",
            decisions,
        )
        self.assertIn(
            "## D-061: Retire the legacy root app.py launcher",
            decisions,
        )
        self.assertIn(
            "## D-062: Retire the legacy root config.py import shim",
            decisions,
        )
        self.assertIn(
            "## D-063: Retire the legacy root api package shims",
            decisions,
        )
        self.assertIn(
            "## D-064: Retire the legacy root core package shims",
            decisions,
        )
        self.assertIn(
            "## D-065: Consolidate the Python package boundary around root launchers",
            decisions,
        )

    def test_runtime_modules_are_moved_with_entrypoint_compatibility_shims(
        self,
    ) -> None:
        package_root = REPO_ROOT / "src" / "polinko"

        self.assertTrue((package_root / "__init__.py").is_file())
        self.assertTrue((package_root / "asgi.py").is_file())
        self.assertTrue((package_root / "cli.py").is_file())
        self.assertTrue((package_root / "config.py").is_file())
        self.assertTrue((package_root / "api" / "__init__.py").is_file())
        self.assertTrue((package_root / "api" / "app_factory.py").is_file())
        self.assertTrue((package_root / "api" / "static" / "favicon.png").is_file())
        self.assertTrue((package_root / "core" / "__init__.py").is_file())
        self.assertTrue((package_root / "core" / "runtime.py").is_file())
        self.assertTrue((package_root / "core" / "history_store.py").is_file())

        legacy_server = _read("server.py")
        self.assertIn('import_module("polinko.asgi")', legacy_server)
        self.assertIn("sys.modules[__name__] = _module", legacy_server)

    def test_current_root_runtime_modules_are_explicit(self) -> None:
        tracked_python = _tracked_files("*.py")
        existing_python = [
            path for path in tracked_python if (REPO_ROOT / path).exists()
        ]
        root_modules = sorted(path for path in existing_python if "/" not in path)

        self.assertEqual(root_modules, ["main.py", "server.py"])

    def test_active_source_and_tool_imports_use_packaged_runtime(self) -> None:
        tracked_python = _tracked_files("*.py")
        active_paths = [
            path for path in tracked_python if path.startswith(("src/", "tools/"))
        ]
        violations = []

        for relative_path in active_paths:
            source = _read(relative_path)
            tree = ast.parse(source, filename=relative_path)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        root_name = alias.name.split(".", maxsplit=1)[0]
                        if root_name in RETIRED_ROOT_IMPORTS:
                            violations.append(f"{relative_path}:{node.lineno}")
                elif isinstance(node, ast.ImportFrom) and node.module is not None:
                    root_name = node.module.split(".", maxsplit=1)[0]
                    if root_name in RETIRED_ROOT_IMPORTS:
                        violations.append(f"{relative_path}:{node.lineno}")

        self.assertEqual(violations, [])

    def test_server_shim_still_has_active_operator_and_container_references(
        self,
    ) -> None:
        expected_refs = {
            "Dockerfile": '"server:app"',
            "makefiles/config/runtime.mk": "ASGI_APP ?= server:app",
            "tools/run_server_daemon.sh": "asgi_app=${ASGI_APP:-server:app}",
            "tools/run_local_eval_gate.sh": "asgi_app=${ASGI_APP:-server:app}",
        }

        for relative_path, expected in expected_refs.items():
            with self.subTest(relative_path=relative_path):
                self.assertIn(expected, _read(relative_path))

    def test_retired_root_surfaces_stay_absent(self) -> None:
        for relative_path in RETIRED_ROOT_SURFACES:
            with self.subTest(relative_path=relative_path):
                self.assertFalse((REPO_ROOT / relative_path).exists())

    def test_active_tracked_files_do_not_regain_retired_root_imports(self) -> None:
        allowed_paths = {
            "docs/governance/DECISIONS.md",
            "docs/governance/STATE.md",
            "docs/runtime/ARCHITECTURE.md",
            "docs/runtime/PACKAGE_BOUNDARY.md",
            "tests/test_package_boundary_contracts.py",
        }
        mentions = []

        for root_name in RETIRED_ROOT_IMPORTS:
            mentions.extend(
                _retired_root_import_mentions(root_name, allowed_paths=allowed_paths)
            )

        self.assertEqual(mentions, [])

    def test_active_tracked_files_do_not_regain_retired_app_launcher_calls(
        self,
    ) -> None:
        allowed_paths = {
            "docs/governance/DECISIONS.md",
            "docs/governance/STATE.md",
            "docs/runtime/ARCHITECTURE.md",
            "docs/runtime/PACKAGE_BOUNDARY.md",
            "tests/test_entrypoints.py",
            "tests/test_package_boundary_contracts.py",
        }
        mentions = []

        for relative_path in _active_tracked_paths():
            if relative_path in allowed_paths:
                continue
            if not (REPO_ROOT / relative_path).exists():
                continue
            source = _read(relative_path)
            if "python app.py" in source or 'import_module("app")' in source:
                mentions.append(relative_path)

        self.assertEqual(mentions, [])


if __name__ == "__main__":
    unittest.main()
