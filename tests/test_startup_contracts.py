import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


class StartupContractTests(unittest.TestCase):
    def test_start_prompt_stops_at_alignment(self) -> None:
        script = _read("tools/start_of_day_routine.sh")

        self.assertIn("Morning startup is complete.", script)
        self.assertIn("Reply in the morning ritual:", script)
        self.assertIn("Context: repo root printed above", script)
        self.assertIn("Kernel candidates: likely lanes", script)
        self.assertIn("one recommended first kernel", script)
        self.assertIn("stop before broadening", script)
        self.assertIn("pause for alignment with the human lead", script)
        self.assertNotIn("/abs/path/to/polinko", script)
        self.assertNotIn("In 5 bullets", script)
        self.assertNotIn("Then execute the Next Slice", script)

    def test_runtime_docs_match_start_alignment_contract(self) -> None:
        start_reference = _read("docs/runtime/START_END_REFERENCE.md")
        runbook = _read("docs/runtime/RUNBOOK.md")

        self.assertIn("reply in the morning ritual", start_reference)
        self.assertIn("kernel candidates", start_reference)
        self.assertIn("pause for alignment with the human lead", start_reference)
        self.assertIn("Reply in the morning ritual before implementation", runbook)
        self.assertIn("kernel candidates", runbook)
        self.assertIn("Pause for alignment with the human lead", runbook)
        self.assertNotIn("execute the `Next Slice`", start_reference)

    def test_runtime_docs_define_active_kernel_validation(self) -> None:
        start_reference = _read("docs/runtime/START_END_REFERENCE.md")
        runbook = _read("docs/runtime/RUNBOOK.md")

        self.assertIn("Active kernel validation", start_reference)
        self.assertIn("During active refactor kernels", start_reference)
        self.assertIn("make end-preflight", start_reference)
        self.assertIn("Do not run `make end` after every kernel", start_reference)
        self.assertIn("Active Kernel Validation", runbook)
        self.assertIn("Use focused checks during active refactor kernels", runbook)
        self.assertIn("Reserve `make end` for real session closeout", runbook)

    def test_wake_lock_reference_matches_stop_all_contract(self) -> None:
        start_reference = _read("docs/runtime/START_END_REFERENCE.md")
        runtime_makefile = _read("makefiles/runtime.mk")
        caffeinate_script = _read("tools/manage_caffeinate.sh")

        self.assertIn("caffeinate-off-all", runtime_makefile)
        self.assertIn("stop-all", caffeinate_script)
        self.assertIn("configured wake-lock", start_reference)
        self.assertIn("without adopting their PIDs", start_reference)
        self.assertNotIn("never adopted or stopped", start_reference)


if __name__ == "__main__":
    unittest.main()
