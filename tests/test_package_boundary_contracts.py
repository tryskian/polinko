from importlib import import_module
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


class PackageBoundaryContractTests(unittest.TestCase):
    def test_package_boundary_doc_names_current_and_target_shapes(self) -> None:
        boundary = _read("docs/runtime/PACKAGE_BOUNDARY.md")

        for expected in (
            "Tracked root runtime compatibility modules",
            "`main.py`",
            "`app.py`",
            "`server.py`",
            "`config.py`",
            "re-exports `AppConfig` and `load_config` from `polinko.config`",
            "`api/`",
            "compatibility shims for legacy `api.*` imports",
            "`core/`",
            "compatibility shims for legacy `core.*` imports",
            "The future runtime import package should be `polinko` under `src/polinko/`.",
            "`src/polinko/config.py`",
            "`src/polinko/api/`",
            "`src/polinko/core/`",
            "root `tools/`",
            "Do not move runtime modules into `src/polinko/`",
            "Do not change ASGI import compatibility for `server:app`.",
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

    def test_runtime_modules_are_moved_with_root_compatibility_shims(self) -> None:
        package_root = REPO_ROOT / "src" / "polinko"

        self.assertTrue((package_root / "__init__.py").is_file())
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

    def test_current_root_runtime_modules_are_explicit(self) -> None:
        tracked_python = subprocess.check_output(
            ["git", "ls-files", "*.py"],
            cwd=REPO_ROOT,
            text=True,
        ).splitlines()
        root_modules = sorted(path for path in tracked_python if "/" not in path)

        self.assertEqual(root_modules, ["app.py", "config.py", "main.py", "server.py"])


if __name__ == "__main__":
    unittest.main()
