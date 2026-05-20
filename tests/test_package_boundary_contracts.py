import ast
from importlib import import_module
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LEGACY_ROOT_IMPORTS = ("api", "config", "core")
LEGACY_API_SHIMS = (
    "app_factory",
    "eval_viz",
    "manual_evals_surface",
    "portfolio_sankey",
)
LEGACY_CORE_SHIMS = (
    "history_store",
    "prompts",
    "rate_limit",
    "responses_parse",
    "runtime",
    "vector_store",
)


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


class PackageBoundaryContractTests(unittest.TestCase):
    def test_package_boundary_doc_names_current_and_target_shapes(self) -> None:
        boundary = _read("docs/runtime/PACKAGE_BOUNDARY.md")

        for expected in (
            "Tracked root runtime compatibility modules",
            "`main.py`",
            "compatibility launcher for `python main.py`",
            "`app.py`",
            "`server.py`",
            "compatibility shim for `uvicorn server:app`",
            "`src/polinko/cli.py`",
            "canonical CLI chat implementation",
            "`src/polinko/asgi.py`",
            "canonical ASGI app construction",
            "`polinko-chat`",
            "`config.py`",
            "re-exports `AppConfig` and `load_config` from `polinko.config`",
            "`api/`",
            "compatibility shims for legacy `api.*` imports",
            "explicit `__all__` list for supported legacy",
            "`from api import ...` imports",
            "`core/`",
            "compatibility shims for legacy `core.*` imports",
            "`from core import ...` imports",
            "The future runtime import package should be `polinko` under `src/polinko/`.",
            "`src/polinko/config.py`",
            "`src/polinko/api/`",
            "`src/polinko/core/`",
            "root `tools/`",
            "current console script: `polinko-chat`",
            "Do not move runtime modules into `src/polinko/`",
            "Do not change ASGI import compatibility for `server:app`.",
        ):
            self.assertIn(expected, boundary)

    def test_package_boundary_doc_records_root_compatibility_audit(self) -> None:
        boundary = _read("docs/runtime/PACKAGE_BOUNDARY.md")

        for expected in (
            "## Compatibility Audit",
            "active runtime and tool imports should use `polinko.*`",
            "root compatibility imports are allowed only in the tracked shim layer",
            "do not delete compatibility launchers or shims in this audit kernel",
            "active `server:app` references still exist in Docker",
            "`app.py` has no active tracked code caller",
            "### Readiness Snapshot: 2026-05-20",
            "closest to retirement",
            "not retirement-ready",
            "`server.py`",
            "Make defaults, server-daemon, local eval gates, Docker",
            "`config.py`",
            "older local scripts have moved to `polinko.config`",
            "`api/`",
            "older local scripts have moved to `polinko.api.*`",
            "`core/`",
            "older local scripts have moved to `polinko.core.*`",
        ):
            self.assertIn(expected, boundary)

    def test_architecture_and_state_link_package_boundary(self) -> None:
        architecture = _read("docs/runtime/ARCHITECTURE.md")
        state = _read("docs/governance/STATE.md")
        docs_index = _read("docs/README.md")
        decisions = _read("docs/governance/DECISIONS.md")

        self.assertIn("docs/runtime/PACKAGE_BOUNDARY.md", architecture)
        self.assertIn("`PACKAGE_BOUNDARY`", architecture)
        self.assertIn("package-boundary migration contract is documented", state)
        self.assertIn("root `api/` and `core/` shim packages", state)
        self.assertIn("`from api import ...` and `from core import ...`", state)
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

    def test_runtime_modules_are_moved_with_root_compatibility_shims(self) -> None:
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

        legacy_config = _read("config.py")
        self.assertIn(
            "from polinko.config import AppConfig, load_config", legacy_config
        )
        self.assertIn('__all__ = ["AppConfig", "load_config"]', legacy_config)

        legacy_api = _read("api/app_factory.py")
        self.assertIn('import_module("polinko.api.app_factory")', legacy_api)
        self.assertIs(
            import_module("api.app_factory"),
            import_module("polinko.api.app_factory"),
        )

        legacy_core = _read("core/runtime.py")
        self.assertIn('import_module("polinko.core.runtime")', legacy_core)
        self.assertIs(
            import_module("core.runtime"),
            import_module("polinko.core.runtime"),
        )

        legacy_server = _read("server.py")
        self.assertIn('import_module("polinko.asgi")', legacy_server)
        self.assertIn("sys.modules[__name__] = _module", legacy_server)

    def test_all_root_package_shims_forward_module_identity(self) -> None:
        legacy_config = import_module("config")
        packaged_config = import_module("polinko.config")
        self.assertIs(legacy_config.AppConfig, packaged_config.AppConfig)
        self.assertIs(legacy_config.load_config, packaged_config.load_config)

        legacy_api_package = import_module("api")
        legacy_core_package = import_module("core")
        self.assertEqual(legacy_api_package.__all__, list(LEGACY_API_SHIMS))
        self.assertEqual(legacy_core_package.__all__, list(LEGACY_CORE_SHIMS))

        for module_name in LEGACY_API_SHIMS:
            self.assertIs(
                import_module(f"api.{module_name}"),
                import_module(f"polinko.api.{module_name}"),
            )

        for module_name in LEGACY_CORE_SHIMS:
            self.assertIs(
                import_module(f"core.{module_name}"),
                import_module(f"polinko.core.{module_name}"),
            )

    def test_root_package_shims_support_legacy_fromlist_imports(self) -> None:
        legacy_api_package = __import__("api", fromlist=list(LEGACY_API_SHIMS))
        legacy_core_package = __import__("core", fromlist=list(LEGACY_CORE_SHIMS))

        for module_name in LEGACY_API_SHIMS:
            self.assertIs(
                getattr(legacy_api_package, module_name),
                import_module(f"polinko.api.{module_name}"),
            )

        for module_name in LEGACY_CORE_SHIMS:
            self.assertIs(
                getattr(legacy_core_package, module_name),
                import_module(f"polinko.core.{module_name}"),
            )

    def test_current_root_runtime_modules_are_explicit(self) -> None:
        tracked_python = subprocess.check_output(
            ["git", "ls-files", "*.py"],
            cwd=REPO_ROOT,
            text=True,
        ).splitlines()
        root_modules = sorted(path for path in tracked_python if "/" not in path)

        self.assertEqual(root_modules, ["app.py", "config.py", "main.py", "server.py"])

    def test_active_source_and_tool_imports_use_packaged_runtime(self) -> None:
        tracked_python = subprocess.check_output(
            ["git", "ls-files", "*.py"],
            cwd=REPO_ROOT,
            text=True,
        ).splitlines()
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
                        if root_name in LEGACY_ROOT_IMPORTS:
                            violations.append(f"{relative_path}:{node.lineno}")
                elif isinstance(node, ast.ImportFrom) and node.module is not None:
                    root_name = node.module.split(".", maxsplit=1)[0]
                    if root_name in LEGACY_ROOT_IMPORTS:
                        violations.append(f"{relative_path}:{node.lineno}")

        self.assertEqual(violations, [])

    def test_legacy_root_imports_stay_confined_to_compatibility_tests(self) -> None:
        tracked_python = subprocess.check_output(
            ["git", "ls-files", "*.py"],
            cwd=REPO_ROOT,
            text=True,
        ).splitlines()
        allowed_paths = {
            "tests/test_config.py",
            "tests/test_package_boundary_contracts.py",
        }
        violations = []

        for relative_path in tracked_python:
            if relative_path in allowed_paths:
                continue
            source = _read(relative_path)
            tree = ast.parse(source, filename=relative_path)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        root_name = alias.name.split(".", maxsplit=1)[0]
                        if root_name in LEGACY_ROOT_IMPORTS:
                            violations.append(f"{relative_path}:{node.lineno}")
                elif isinstance(node, ast.ImportFrom) and node.module is not None:
                    root_name = node.module.split(".", maxsplit=1)[0]
                    if root_name in LEGACY_ROOT_IMPORTS:
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

    def test_legacy_app_launcher_has_no_active_tracked_code_callers(self) -> None:
        tracked_files = subprocess.check_output(
            ["git", "ls-files"],
            cwd=REPO_ROOT,
            text=True,
        ).splitlines()
        active_extensions = {".py", ".sh", ".mk"}
        active_paths = [
            path
            for path in tracked_files
            if Path(path).suffix in active_extensions
            or path in {"Makefile", "Dockerfile", "pyproject.toml"}
        ]
        allowed_paths = {
            "app.py",
            "docs/governance/DECISIONS.md",
            "docs/governance/STATE.md",
            "docs/runtime/ARCHITECTURE.md",
            "docs/runtime/PACKAGE_BOUNDARY.md",
            "tests/test_entrypoints.py",
            "tests/test_package_boundary_contracts.py",
        }
        mentions = []

        for relative_path in active_paths:
            if relative_path in allowed_paths:
                continue
            source = _read(relative_path)
            if "python app.py" in source or 'import_module("app")' in source:
                mentions.append(relative_path)

        self.assertEqual(mentions, [])


if __name__ == "__main__":
    unittest.main()
