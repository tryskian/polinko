import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FIX_SCRIPT = REPO_ROOT / "tools" / "fix_transcripts.py"
VALIDATE_SCRIPT = REPO_ROOT / "tools" / "validate_transcripts.py"


def _write(root: Path, relative_path: str, content: str) -> Path:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _run(script: Path, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script)],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _base_transcript(insights: str = "") -> str:
    parts = [
        "# Example Transcript",
        "",
        "## Scope",
        "",
        "Identifiers:",
        "",
        "- id: example",
        "",
        "## Transcript (Verbatim Block)",
        "",
        "```text",
        "human: hello",
        "assistant: hello",
        "```",
    ]
    if insights:
        parts.extend(["", insights.rstrip()])
    return "\n".join(parts) + "\n"


VALID_INSIGHTS = """## Structured Insights (Assistant Interpretation)

### Distilled Signal

The transcript preserves a focused signal.

### Key Points

- The verbatim transcript remains the source of truth.
- Interpretation stays linked to transcript evidence.
"""


class TranscriptCloseoutTests(unittest.TestCase):
    def test_validate_skips_when_transcript_root_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = _run(VALIDATE_SCRIPT, Path(tmp))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "transcript-check: SKIP (missing docs/peanut/transcripts)",
            result.stdout,
        )

    def test_validate_excludes_readme_and_sessions_exports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "docs/peanut/transcripts/README.md", "# README\n")
            _write(root, "docs/peanut/transcripts/sessions/export.md", "# Export\n")

            result = _run(VALIDATE_SCRIPT, root)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "transcript-check: SKIP (no curated transcript files found)",
            result.stdout,
        )

    def test_validate_passes_curated_transcript_with_required_structure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(
                root,
                "docs/peanut/transcripts/co_reasoning/example.md",
                _base_transcript(VALID_INSIGHTS),
            )

            result = _run(VALIDATE_SCRIPT, root)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "transcript-check: PASS (1 curated transcript files)", result.stdout
        )

    def test_validate_fails_curated_transcript_missing_distillation(self) -> None:
        insights = """## Structured Insights (Assistant Interpretation)

### Key Points

- No distillation heading is present.
"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(
                root,
                "docs/peanut/transcripts/co_reasoning/example.md",
                _base_transcript(insights),
            )

            result = _run(VALIDATE_SCRIPT, root)

        self.assertEqual(result.returncode, 1)
        self.assertIn("transcript-check: FAIL", result.stdout)
        self.assertIn("structured insights missing distillation heading", result.stdout)
        self.assertIn("structured insights must include at least two H3", result.stdout)

    def test_fix_inserts_default_insights_then_validate_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            transcript = _write(
                root,
                "docs/peanut/transcripts/co_reasoning/example.md",
                _base_transcript(),
            )

            fix_result = _run(FIX_SCRIPT, root)
            validate_result = _run(VALIDATE_SCRIPT, root)

            updated = transcript.read_text(encoding="utf-8")

        self.assertEqual(fix_result.returncode, 0, fix_result.stderr)
        self.assertIn("transcript-fix: DONE (1 files updated)", fix_result.stdout)
        self.assertIn("### Distilled Signal", updated)
        self.assertIn("### Key Points", updated)
        self.assertEqual(validate_result.returncode, 0, validate_result.stderr)
        self.assertIn(
            "transcript-check: PASS (1 curated transcript files)",
            validate_result.stdout,
        )

    def test_fix_adds_key_points_when_existing_insights_are_too_thin(self) -> None:
        insights = """## Structured Insights (Assistant Interpretation)

### Distilled Signal

The transcript has only one H3 section.
"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            transcript = _write(
                root,
                "docs/peanut/transcripts/co_reasoning/example.md",
                _base_transcript(insights),
            )

            fix_result = _run(FIX_SCRIPT, root)
            validate_result = _run(VALIDATE_SCRIPT, root)

            updated = transcript.read_text(encoding="utf-8")

        self.assertEqual(fix_result.returncode, 0, fix_result.stderr)
        self.assertIn("transcript-fix: DONE (1 files updated)", fix_result.stdout)
        self.assertIn("### Key Points", updated)
        self.assertEqual(validate_result.returncode, 0, validate_result.stderr)


if __name__ == "__main__":
    unittest.main()
