import importlib
import os
from pathlib import Path
import sys
import types
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def _read_makefile_source(relative_path: str, seen: set[Path] | None = None) -> str:
    if seen is None:
        seen = set()
    path = REPO_ROOT / relative_path
    resolved_path = path.resolve()
    if resolved_path in seen:
        return ""
    seen.add(resolved_path)

    text = path.read_text(encoding="utf-8")
    source_texts = [text]
    for line in text.splitlines():
        if line.startswith("include "):
            for include_path in line.removeprefix("include ").split():
                source_texts.append(_read_makefile_source(include_path, seen))
    return "\n".join(source_texts)


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

    def test_operator_entrypoint_compatibility_contract_is_wired(self) -> None:
        boundary = _read("docs/runtime/PACKAGE_BOUNDARY.md")
        decisions = _read("docs/governance/DECISIONS.md")
        runtime_config = _read_makefile_source("makefiles/config/runtime.mk")
        runtime_make = _read_makefile_source("makefiles/runtime.mk")
        pyproject = _read("pyproject.toml")
        dockerfile = _read("Dockerfile")
        server_daemon = _read("tools/run_server_daemon.sh")
        local_eval_gate = _read("tools/run_local_eval_gate.sh")

        for expected in (
            "## Entrypoint Compatibility Contract",
            "`make chat`",
            "`python main.py`",
            "`polinko-chat`",
            "`make server` / `make localhost`",
            "`make server-daemon`",
            "local eval gates",
            "Docker CMD",
        ):
            self.assertIn(expected, boundary)

        self.assertIn(
            "## D-066: Treat entrypoint compatibility as an explicit audit surface",
            decisions,
        )
        self.assertIn("CLI_ENTRYPOINT ?= -m polinko.cli", runtime_config)
        self.assertIn("ASGI_APP ?= server:app", runtime_config)
        self.assertIn("chat:\n\t$(PYTHON) $(CLI_ENTRYPOINT)", runtime_make)
        self.assertIn(
            "localhost server:\n\t$(PYTHON) -m uvicorn $(ASGI_APP)",
            runtime_make,
        )
        self.assertIn('polinko-chat = "polinko.cli:main"', pyproject)
        self.assertIn('"server:app"', dockerfile)
        self.assertIn("asgi_app=${ASGI_APP:-server:app}", server_daemon)
        self.assertIn("asgi_app=${ASGI_APP:-server:app}", local_eval_gate)

    def test_root_launchers_stay_thin_compatibility_surfaces(self) -> None:
        root_modules = sorted(path.name for path in REPO_ROOT.glob("*.py"))
        main_text = _read("main.py")
        server_text = _read("server.py")

        self.assertEqual(root_modules, ["main.py", "server.py"])
        self.assertIn("from polinko.cli import main as run_main", main_text)
        self.assertNotIn("from agents import", main_text)
        self.assertNotIn("from openai import", main_text)
        self.assertIn('import_module("polinko.asgi")', server_text)
        self.assertIn("sys.modules[__name__] = _module", server_text)


if __name__ == "__main__":
    unittest.main()
