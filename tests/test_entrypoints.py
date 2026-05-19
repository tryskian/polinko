import importlib
import unittest


class EntrypointTests(unittest.TestCase):
    def test_cli_entrypoint_imports_without_running_loop(self) -> None:
        cli_main = importlib.import_module("main")

        self.assertTrue(callable(cli_main.main))

    def test_legacy_app_launcher_points_to_main(self) -> None:
        cli_main = importlib.import_module("main")
        legacy_app = importlib.import_module("app")

        self.assertIs(legacy_app.main, cli_main.main)


if __name__ == "__main__":
    unittest.main()
