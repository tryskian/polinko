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
        self.assertIn("Today's kernels: likely work lanes", script)
        self.assertIn("pause for alignment with the human lead", script)
        self.assertNotIn("/abs/path/to/polinko", script)
        self.assertNotIn("In 5 bullets", script)
        self.assertNotIn("Then execute the Next Slice", script)

    def test_runtime_docs_match_start_alignment_contract(self) -> None:
        start_reference = _read("docs/runtime/START_END_REFERENCE.md")
        runbook = _read("docs/runtime/RUNBOOK.md")

        self.assertIn("reply in the morning ritual", start_reference)
        self.assertIn("pause for alignment with the human lead", start_reference)
        self.assertIn("Reply in the morning ritual before implementation", runbook)
        self.assertIn("Pause for alignment with the human lead", runbook)
        self.assertNotIn("execute the `Next Slice`", start_reference)


if __name__ == "__main__":
    unittest.main()
