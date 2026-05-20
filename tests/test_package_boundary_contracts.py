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
            "Tracked runtime Python currently has four root modules",
            "`main.py`",
            "`app.py`",
            "`server.py`",
            "`config.py`",
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

    def test_packaging_rail_does_not_move_runtime_modules(self) -> None:
        package_root = REPO_ROOT / "src" / "polinko"

        self.assertTrue((package_root / "__init__.py").is_file())
        self.assertFalse((package_root / "config.py").exists())
        self.assertFalse((package_root / "api").exists())
        self.assertFalse((package_root / "core").exists())

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
