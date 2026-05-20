import importlib
from pathlib import Path
import unittest


class EntrypointTests(unittest.TestCase):
    def test_cli_entrypoint_imports_without_running_loop(self) -> None:
        cli_main = importlib.import_module("main")

        self.assertTrue(callable(cli_main.main))

    def test_legacy_app_launcher_points_to_main(self) -> None:
        cli_main = importlib.import_module("main")
        legacy_app = importlib.import_module("app")

        self.assertIs(legacy_app.main, cli_main.main)

    def test_cli_interpreter_fallback_prefers_current_local_venv(self) -> None:
        cli_main = importlib.import_module("main")
        project_root = Path(cli_main.__file__).resolve().parent

        self.assertEqual(
            cli_main._project_python_candidates()[:3],
            [
                project_root / ".venv" / "bin" / "python3.14",
                project_root / ".venv" / "bin" / "python",
                project_root / ".venv" / "bin" / "python3",
            ],
        )
        self.assertNotIn(
            "polinko-repositioning-system", str(cli_main._project_python_candidates())
        )


if __name__ == "__main__":
    unittest.main()
