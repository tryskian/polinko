import importlib
import os
from pathlib import Path
import sys
import types
import unittest


class EntrypointTests(unittest.TestCase):
    def test_cli_entrypoint_imports_without_running_loop(self) -> None:
        cli_main = importlib.import_module("main")

        self.assertTrue(callable(cli_main.main))

    def test_packaged_cli_imports_without_running_loop(self) -> None:
        cli = importlib.import_module("polinko.cli")

        self.assertTrue(callable(cli.main))
        self.assertTrue(callable(cli.export_transcript))

    def test_root_main_import_does_not_load_packaged_cli_runtime(self) -> None:
        original_main = sys.modules.pop("main", None)
        original_cli = sys.modules.pop("polinko.cli", None)
        try:
            cli_main = importlib.import_module("main")

            self.assertNotIn("polinko.cli", sys.modules)
            self.assertEqual(cli_main.__all__, ["main"])
        finally:
            sys.modules.pop("main", None)
            if original_main is not None:
                sys.modules["main"] = original_main
            if original_cli is not None:
                sys.modules["polinko.cli"] = original_cli

    def test_root_main_launcher_forwards_to_packaged_cli(self) -> None:
        cli_main = importlib.import_module("main")
        original_cli = sys.modules.get("polinko.cli")
        called = []
        fake_cli = types.ModuleType("polinko.cli")

        def run_main() -> None:
            called.append("cli")

        fake_cli.main = run_main
        sys.modules["polinko.cli"] = fake_cli

        try:
            cli_main.main()
        finally:
            if original_cli is not None:
                sys.modules["polinko.cli"] = original_cli
            else:
                sys.modules.pop("polinko.cli", None)

        self.assertEqual(called, ["cli"])

    def test_server_compatibility_shim_forwards_to_packaged_asgi(self) -> None:
        os.environ.setdefault("OPENAI_API_KEY", "sk-test-key-123456789012345")
        server = importlib.import_module("server")
        asgi = importlib.import_module("polinko.asgi")

        self.assertIs(server, asgi)
        self.assertIs(server.app, asgi.app)
        self.assertTrue(callable(server.get_runtime_deps))
        self.assertIs(server.runtime_deps, server.get_runtime_deps())

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
