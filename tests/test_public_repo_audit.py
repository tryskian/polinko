import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from tools.public_repo_audit import find_blocked_paths
from tools.public_repo_audit import find_secret_markers


class PublicRepoAuditTests(unittest.TestCase):
    def test_find_blocked_paths(self) -> None:
        tracked_paths = [
            "README.md",
            "docs/governance/STATE.md",
            "output/jupyter-notebook/starter.ipynb",
            "docs/peanut/transcripts/x.md",
        ]
        blocked = find_blocked_paths(
            tracked_paths=tracked_paths,
            blocked_prefixes=("output/", "docs/peanut/"),
        )
        self.assertEqual(
            blocked,
            [
                "docs/peanut/transcripts/x.md",
                "output/jupyter-notebook/starter.ipynb",
            ],
        )

    def test_find_secret_markers(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "safe.md").write_text("hello", encoding="utf-8")
            openai_key_name = "OPENAI_API_KEY"
            synthetic_live_value = "sk-" + "proj-" + "abcdefghijklmnopqrstuvwxyz0123456789"
            (root / "notes.md").write_text(
                f"{openai_key_name}={synthetic_live_value}",
                encoding="utf-8",
            )
            (root / ".env.example").write_text("OPENAI_API_KEY=", encoding="utf-8")
            (root / "placeholder.md").write_text(
                "OPENAI_API_KEY=sk-test-key-1234567890",
                encoding="utf-8",
            )

            findings = find_secret_markers(
                repo_root=root,
                tracked_paths=["safe.md", "notes.md", ".env.example", "placeholder.md"],
            )

            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0]["path"], "notes.md")
            self.assertEqual(findings[0]["marker"], "OPENAI_API_KEY")


if __name__ == "__main__":
    unittest.main()
