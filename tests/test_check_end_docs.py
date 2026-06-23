import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "check_end_docs.py"
TODAY = "2026-06-21"
YESTERDAY = "2026-06-20"


def _write_doc(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _run_check(
    cwd: Path, date: str = TODAY, expected_commit: str | None = None
) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(SCRIPT), "--date", date]
    if expected_commit is not None:
        command.extend(["--expected-commit", expected_commit])
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class CheckEndDocsTests(unittest.TestCase):
    def test_passes_when_required_state_was_updated_today(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_doc(
                root,
                "docs/governance/STATE.md",
                f"# State\n\nLast updated: {TODAY}\n",
            )

            result = _run_check(root)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            f"end-docs-check: PASS (1 docs updated for {TODAY})",
            result.stdout,
        )

    def test_passes_with_optional_local_handoff_updated_today(self) -> None:
        commit = "abc1234"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_doc(
                root,
                "docs/governance/STATE.md",
                f"# State\n\nLast updated: {TODAY}\n",
            )
            _write_doc(
                root,
                "docs/peanut/governance/SESSION_HANDOFF.md",
                f"# Session Handoff\n\nLast updated: {TODAY}\n\n{commit}\n",
            )

            result = _run_check(root, expected_commit=commit)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            f"end-docs-check: PASS (2 docs updated for {TODAY})",
            result.stdout,
        )

    def test_fails_when_optional_local_handoff_omits_current_commit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_doc(
                root,
                "docs/governance/STATE.md",
                f"# State\n\nLast updated: {TODAY}\n",
            )
            _write_doc(
                root,
                "docs/peanut/governance/SESSION_HANDOFF.md",
                f"# Session Handoff\n\nLast updated: {TODAY}\n\nold1234\n",
            )

            result = _run_check(root, expected_commit="new5678")

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "docs/peanut/governance/SESSION_HANDOFF.md: missing current commit "
            "new5678 in active handoff",
            result.stderr,
        )

    def test_fails_when_required_state_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_check(Path(tmp))

        self.assertEqual(result.returncode, 1)
        self.assertIn("end-docs-check: FAIL", result.stderr)
        self.assertIn(
            "docs/governance/STATE.md: missing required current-truth doc",
            result.stderr,
        )

    def test_fails_when_required_state_is_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_doc(
                root,
                "docs/governance/STATE.md",
                f"# State\n\nLast updated: {YESTERDAY}\n",
            )

            result = _run_check(root)

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            f"docs/governance/STATE.md: Last updated is {YESTERDAY}, expected {TODAY}",
            result.stderr,
        )

    def test_fails_when_optional_local_handoff_is_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_doc(
                root,
                "docs/governance/STATE.md",
                f"# State\n\nLast updated: {TODAY}\n",
            )
            _write_doc(
                root,
                "docs/peanut/governance/SESSION_HANDOFF.md",
                f"# Session Handoff\n\nLast updated: {YESTERDAY}\n",
            )

            result = _run_check(root)

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "docs/peanut/governance/SESSION_HANDOFF.md: Last updated is "
            f"{YESTERDAY}, expected {TODAY}",
            result.stderr,
        )

    def test_fails_when_last_updated_marker_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_doc(root, "docs/governance/STATE.md", "# State\n")

            result = _run_check(root)

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            f"docs/governance/STATE.md: Last updated is missing, expected {TODAY}",
            result.stderr,
        )


if __name__ == "__main__":
    unittest.main()
