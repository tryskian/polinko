import re
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MAKEFILE = REPO_ROOT / "Makefile"


def _makefile_text() -> str:
    return MAKEFILE.read_text(encoding="utf-8")


def _makefile_contract_text() -> str:
    root_text = _makefile_text()
    source_texts = [root_text]
    for match in re.finditer(r"^include\s+(.+)$", root_text, re.MULTILINE):
        for include_path in match.group(1).split():
            source_texts.append((REPO_ROOT / include_path).read_text(encoding="utf-8"))
    return "\n".join(source_texts)


def _phony_targets() -> list[str]:
    targets: list[str] = []
    for match in re.finditer(
        r"^\.PHONY:\s*(.*)$",
        _makefile_contract_text(),
        re.MULTILINE,
    ):
        targets.extend(match.group(1).split())
    return targets


class MakefileContractTests(unittest.TestCase):
    def test_default_goal_is_chat(self) -> None:
        self.assertRegex(_makefile_text(), r"(?m)^\.DEFAULT_GOAL\s*:=\s*chat$")

    def test_target_families_are_extracted_through_includes(self) -> None:
        self.assertRegex(_makefile_text(), r"(?m)^include\s+makefiles/build\.mk$")
        self.assertRegex(_makefile_text(), r"(?m)^include\s+makefiles/checks\.mk$")
        self.assertRegex(_makefile_text(), r"(?m)^include\s+makefiles/runtime\.mk$")
        self.assertRegex(_makefile_text(), r"(?m)^include\s+makefiles/surfaces\.mk$")
        self.assertRegex(_makefile_text(), r"(?m)^include\s+makefiles/evals\.mk$")
        self.assertRegex(_makefile_text(), r"(?m)^include\s+makefiles/ops\.mk$")

    def test_no_argument_make_still_launches_chat_entrypoint(self) -> None:
        result = subprocess.run(
            ["make", "-n"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        lines = result.stdout.splitlines()
        self.assertTrue(lines)
        self.assertTrue(any("main.py" in line for line in lines), lines)

    def test_phony_targets_are_unique(self) -> None:
        targets = _phony_targets()

        self.assertEqual(sorted(targets), sorted(set(targets)))

    def test_chat_and_manual_eval_entrypoints_stay_phony(self) -> None:
        targets = set(_phony_targets())

        self.assertIn("ci", targets)
        self.assertIn("chat", targets)
        self.assertIn("server-daemon", targets)
        self.assertIn("caffeinate", targets)
        self.assertIn("manual-evals-db", targets)
        self.assertIn("manualdb", targets)
        self.assertIn("portfolio", targets)
        self.assertIn("portfolio-mockups", targets)
        self.assertIn("pwcli", targets)

    def test_lifecycle_aliases_delegate_to_canonical_targets(self) -> None:
        text = _makefile_contract_text()

        self.assertRegex(text, r"(?m)^eod end-preflight:\s*end$")
        self.assertRegex(text, r"(?m)^caffeinate-on:\s*caffeinate$")
        self.assertRegex(text, r"(?m)^caffeinate-off:\s*decaffeinate$")
        self.assertRegex(text, r"(?m)^decaffeinate-status:\s*caffeinate-status$")

    def test_eval_entrypoints_stay_phony(self) -> None:
        targets = set(_phony_targets())

        self.assertIn("api-smoke", targets)
        self.assertIn("eval-smoke", targets)
        self.assertIn("quality-gate", targets)
        self.assertIn("quality-gate-deterministic", targets)
        self.assertIn("ocrmine", targets)
        self.assertIn("ocrkernel", targets)
        self.assertIn("eval-sidecar-start", targets)
        self.assertIn("eval-ocr-transcript-cases-growth-batched", targets)

    def test_external_check_entrypoints_stay_phony(self) -> None:
        targets = set(_phony_targets())

        self.assertIn("k6-chat-smoke", targets)
        self.assertIn("trivy-fs", targets)
        self.assertIn("trivy-image", targets)
        self.assertIn("docker-build", targets)
        self.assertIn("docker-run", targets)


if __name__ == "__main__":
    unittest.main()
