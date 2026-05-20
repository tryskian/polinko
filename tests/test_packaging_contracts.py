import tomllib
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


class PackagingContractTests(unittest.TestCase):
    def test_pyproject_defines_src_layout_package(self) -> None:
        pyproject = tomllib.loads(_read("pyproject.toml"))

        self.assertEqual(
            pyproject["build-system"]["build-backend"], "setuptools.build_meta"
        )
        self.assertIn("setuptools>=77", pyproject["build-system"]["requires"])

        project = pyproject["project"]
        self.assertEqual(project["name"], "polinko")
        self.assertEqual(project["dynamic"], ["version"])
        self.assertEqual(project["requires-python"], ">=3.14")
        self.assertEqual(project["license"], "Apache-2.0")
        self.assertEqual(project["scripts"], {"polinko-chat": "polinko.cli:main"})
        self.assertNotIn("dependencies", project)

        setuptools = pyproject["tool"]["setuptools"]
        self.assertEqual(setuptools["package-dir"], {"": "src"})

        package_find = pyproject["tool"]["setuptools"]["packages"]["find"]
        self.assertEqual(package_find["where"], ["src"])
        self.assertEqual(package_find["include"], ["polinko*"])

        package_data = pyproject["tool"]["setuptools"]["package-data"]
        self.assertEqual(package_data["polinko.api"], ["static/*.png"])

        dynamic = pyproject["tool"]["setuptools"]["dynamic"]
        self.assertEqual(dynamic["version"], {"attr": "polinko.__version__"})

        ruff = pyproject["tool"]["ruff"]
        self.assertEqual(ruff["target-version"], "py313")

    def test_package_scaffold_has_runtime_boundaries(self) -> None:
        package_root = REPO_ROOT / "src" / "polinko"
        init_text = _read("src/polinko/__init__.py")

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
        self.assertIn('__version__ = "0.0.0"', init_text)

    def test_editable_install_check_is_named_and_ci_exercised(self) -> None:
        build_make = _read("makefiles/build.mk")
        ci_workflow = _read(".github/workflows/ci.yml")
        install_check = _read("tools/check_package_install.py")
        pyright_config = _read("pyrightconfig.json")

        self.assertIn(
            "ci: ci-docs ci-python-style ci-python-type-check ci-package ci-test",
            build_make,
        )
        self.assertIn("ci-package: package-install-check", build_make)
        self.assertIn("pip install --no-build-isolation --no-deps -e .", build_make)
        self.assertIn("$(PYTHON) tools/check_package_install.py", build_make)
        self.assertIn("make package-install-check PYTHON=python", ci_workflow)
        self.assertIn('metadata.version("polinko")', install_check)
        self.assertIn("polinko.__version__", install_check)
        self.assertIn(
            "from polinko.config import AppConfig, load_config", install_check
        )
        self.assertIn('find_spec("polinko.api.app_factory")', install_check)
        self.assertIn('find_spec("polinko.core.runtime")', install_check)
        self.assertIn('find_spec("polinko.cli")', install_check)
        self.assertIn('find_spec("polinko.asgi")', install_check)
        self.assertIn('resources.files("polinko.api")', install_check)
        self.assertIn('metadata.entry_points(group="console_scripts")', install_check)
        self.assertIn('"polinko-chat"', install_check)
        self.assertIn('"src"', pyright_config)


if __name__ == "__main__":
    unittest.main()
