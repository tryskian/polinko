import unittest
from pathlib import Path


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


class StartupContractTests(unittest.TestCase):
    def test_start_prompt_stops_at_alignment(self) -> None:
        script = _read("tools/start_of_day_routine.sh")

        self.assertIn("Morning startup is complete.", script)
        self.assertIn("Reply in the morning ritual before implementation:", script)
        self.assertIn("Context: repo root printed above", script)
        self.assertIn("Kernel map: likely lanes", script)
        self.assertIn("one recommended first kernel", script)
        self.assertIn("chat-first alignment pass", script)
        self.assertIn("Wait for human alignment before implementation", script)
        self.assertIn("stop before broadening", script)
        self.assertIn("QA browser / DevTools MCP", script)
        self.assertIn("explicit local-browser helper surface", script)
        self.assertNotIn("/abs/path/to/polinko", script)
        self.assertNotIn("In 5 bullets", script)
        self.assertNotIn("Then execute the Next Slice", script)

    def test_startup_surfaces_github_health_without_blocking(self) -> None:
        script = _read("tools/start_of_day_routine.sh")

        self.assertIn("make --no-print-directory github-health", script)
        self.assertIn(
            "github-health reported attention; continuing startup",
            script,
        )
        self.assertIn("make --no-print-directory doctor-env", script)
        self.assertLess(
            script.index("make --no-print-directory github-health"),
            script.index("make --no-print-directory doctor-env"),
        )

    def test_startup_step_reporting_is_centralized(self) -> None:
        script = _read("tools/start_of_day_routine.sh")

        expected_steps = [
            "workspace context",
            "github-health",
            "doctor-env",
            "caffeinate",
            "caffeinate-status",
            "server-daemon",
            "api-smoke",
        ]
        self.assertIn("START_TOTAL_STEPS=7", script)
        self.assertIn("start_step()", script)
        self.assertEqual(
            len(expected_steps),
            sum(f'start_step "{step}"' in script for step in expected_steps),
        )
        positions = [script.index(f'start_step "{step}"') for step in expected_steps]
        self.assertEqual(sorted(positions), positions)
        for hardcoded_step in range(1, 8):
            self.assertNotIn(f'echo "[start] {hardcoded_step}/7', script)

    def test_startup_starts_repo_managed_server_before_smoke(self) -> None:
        script = _read("tools/start_of_day_routine.sh")

        self.assertIn("make --no-print-directory server-daemon", script)
        self.assertLess(
            script.index("make --no-print-directory caffeinate-status"),
            script.index("make --no-print-directory server-daemon"),
        )
        self.assertLess(
            script.index("make --no-print-directory server-daemon"),
            script.index("make --no-print-directory api-smoke"),
        )

    def test_runtime_docs_match_start_alignment_contract(self) -> None:
        start_reference = _read("docs/runtime/START_END_REFERENCE.md")
        runbook = _read("docs/runtime/RUNBOOK.md")
        runtime_map = _read("docs/runtime/RUNTIME_SURFACE_MAP.md")

        self.assertIn(
            "reply in the morning ritual before implementation", start_reference
        )
        self.assertIn("kernel map", start_reference)
        self.assertIn("make github-health", start_reference)
        self.assertIn("make server-daemon", start_reference)
        self.assertIn("continues local startup", start_reference)
        self.assertIn("chat-first alignment pass", start_reference)
        self.assertIn("QA browser / DevTools MCP", start_reference)
        self.assertIn("wait for human alignment before implementation", start_reference)
        self.assertIn("docs/governance/DECISIONS.md", runbook)
        self.assertIn("Reply in the morning ritual before implementation", runbook)
        self.assertIn("repo root printed by `make start`", runbook)
        self.assertIn("GitHub health attention", runbook)
        self.assertIn("repo-managed server", runbook)
        self.assertIn("QA browser / DevTools MCP", runbook)
        self.assertIn("kernel map", runbook)
        self.assertIn("chat-first alignment pass", runbook)
        self.assertIn("Wait for human alignment before implementation", runbook)
        self.assertNotIn("/abs/path/to/polinko", runbook)
        self.assertIn('Startup["Startup and alignment"]', runtime_map)
        self.assertIn(
            'StartRoutine --> GitHubHealth["make github-health"]', runtime_map
        )
        self.assertIn(
            'StartRoutine --> ServerDaemonStart["make server-daemon"]',
            runtime_map,
        )
        self.assertNotIn("Startup and workspace bootstrap", runtime_map)
        self.assertNotIn("execute the `Next Slice`", start_reference)

    def test_docs_index_links_to_current_ritual_headings(self) -> None:
        docs_index = _read("docs/README.md")

        self.assertIn(
            "./runtime/RUNBOOK.md#morning-startup-ritual",
            docs_index,
        )
        self.assertIn("./runtime/RUNBOOK.md#end-of-day-ritual", docs_index)
        self.assertNotIn("morning-startup-check-codexbeab", docs_index)
        self.assertNotIn("end-of-day-routine-codexbeab", docs_index)

    def test_runtime_docs_define_active_kernel_validation(self) -> None:
        start_reference = _read("docs/runtime/START_END_REFERENCE.md")
        runbook = _read("docs/runtime/RUNBOOK.md")

        self.assertIn("Active kernel validation", start_reference)
        self.assertIn("During active refactor kernels", start_reference)
        self.assertIn("make end-preflight", start_reference)
        self.assertIn("recommended next kernel", start_reference)
        self.assertIn("Reserve `make end` for real session closeout", start_reference)
        self.assertIn("Active Kernel Validation", runbook)
        self.assertIn("Use focused checks during active refactor kernels", runbook)
        self.assertIn("recommended next kernel", runbook)
        self.assertIn("Reserve `make end` for real session closeout", runbook)

    def test_wake_lock_reference_matches_stop_all_contract(self) -> None:
        start_reference = _read("docs/runtime/START_END_REFERENCE.md")
        runtime_makefile = _read_makefile_source("makefiles/runtime.mk")
        caffeinate_script = _read("tools/manage_caffeinate.sh")

        self.assertIn("caffeinate-off-all", runtime_makefile)
        self.assertIn("stop-all", caffeinate_script)
        self.assertIn("repo-scoped by default", start_reference)
        self.assertIn("explicit operator opt-in", start_reference)
        self.assertIn("`ACTIVE`, `QUIET`,", start_reference)
        self.assertIn("without adopting their PIDs", start_reference)
        self.assertNotIn("never adopted or stopped", start_reference)


if __name__ == "__main__":
    unittest.main()
