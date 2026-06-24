from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools import check_local_runtime_config


REPO_ROOT = Path(__file__).resolve().parents[1]


def _write(root: Path, relative_path: str, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class LocalRuntimeConfigTests(unittest.TestCase):
    def test_missing_vscode_directory_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            failures = check_local_runtime_config.check_vscode_config(Path(tmpdir))

        self.assertEqual(failures, [])

    def test_invalid_json_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write(root, ".vscode/tasks.json", "{bad")

            failures = check_local_runtime_config.check_vscode_config(root)

        self.assertEqual(len(failures), 1)
        self.assertIn("invalid JSON", failures[0])

    def test_retired_folder_open_bootstrap_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write(
                root,
                ".vscode/tasks.json",
                """
                {
                  "tasks": [
                    {
                      "label": "workspace bootstrap",
                      "type": "shell",
                      "command": "make start",
                      "runOptions": {"runOn": "folderOpen"}
                    }
                  ]
                }
                """,
            )

            failures = check_local_runtime_config.check_vscode_config(root)

        self.assertTrue(any("retired task label" in failure for failure in failures))
        self.assertTrue(any("folderOpen" in failure for failure in failures))

    def test_background_task_without_matcher_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write(
                root,
                ".vscode/tasks.json",
                """
                {
                  "tasks": [
                    {
                      "label": "make localhost",
                      "type": "shell",
                      "command": "make localhost",
                      "isBackground": true,
                      "problemMatcher": []
                    }
                  ]
                }
                """,
            )

            failures = check_local_runtime_config.check_vscode_config(root)

            self.assertIn(
                "'make localhost' is background without a readiness problemMatcher",
                failures[0],
            )

    def test_manual_make_start_task_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write(
                root,
                ".vscode/tasks.json",
                """
                {
                  "tasks": [
                    {
                      "label": "make start",
                      "type": "shell",
                      "command": "make start",
                      "problemMatcher": []
                    },
                    {
                      "label": "make localhost",
                      "type": "shell",
                      "command": "make localhost",
                      "problemMatcher": []
                    }
                  ]
                }
                """,
            )

            failures = check_local_runtime_config.check_vscode_config(root)

        self.assertEqual(failures, [])

    def test_retired_local_doc_paths_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write(
                root,
                ".vscode/settings.json",
                """
                {
                  "files.exclude": {
                    "docs/INSTANCE_HANDOFF.md": true
                  },
                  "search.exclude": {
                    "docs/POL1_COMMS.md": true
                  }
                }
                """,
            )

            failures = check_local_runtime_config.check_vscode_config(root)

        self.assertEqual(len(failures), 2)
        self.assertTrue(
            any("docs/INSTANCE_HANDOFF.md" in failure for failure in failures)
        )
        self.assertTrue(any("docs/POL1_COMMS.md" in failure for failure in failures))

    def test_retired_local_editor_doc_tokens_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write(
                root,
                ".vscode/settings.json",
                """
                {
                  "files.exclude": {
                    "docs/AGENT_BUILDER_MIRROR.md": true,
                    "docs/HYBRID_OPENAI_ADOPTION_PLAN.md": true
                  },
                  "markdownlint.ignore": [
                    "**/docs/portfolio/raw_evidence/**"
                  ]
                }
                """,
            )

            failures = check_local_runtime_config.check_vscode_config(root)

        self.assertEqual(len(failures), 3)
        self.assertTrue(
            any("docs/AGENT_BUILDER_MIRROR.md" in failure for failure in failures)
        )
        self.assertTrue(
            any(
                "docs/HYBRID_OPENAI_ADOPTION_PLAN.md" in failure for failure in failures
            )
        )
        self.assertTrue(
            any("docs/portfolio/raw_evidence" in failure for failure in failures)
        )

    def test_retired_devcontainer_doc_tokens_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write(
                root,
                ".devcontainer/devcontainer.json",
                """
                {
                  "customizations": {
                    "vscode": {
                      "settings": {
                        "markdownlint.ignore": [
                          "**/docs/portfolio/raw_evidence/**"
                        ],
                        "files.exclude": {
                          "docs/AGENT_BUILDER_MIRROR.md": true
                        }
                      }
                    }
                  }
                }
                """,
            )

            failures = check_local_runtime_config.check_devcontainer_config(root)

        self.assertEqual(len(failures), 2)
        self.assertTrue(
            any("docs/AGENT_BUILDER_MIRROR.md" in failure for failure in failures)
        )
        self.assertTrue(
            any("docs/portfolio/raw_evidence" in failure for failure in failures)
        )

    def test_run_checks_vscode_and_devcontainer_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write(
                root,
                ".vscode/settings.json",
                """
                {
                  "search.exclude": {
                    "docs/POL1_COMMS.md": true
                  }
                }
                """,
            )
            _write(
                root,
                ".devcontainer/devcontainer.json",
                """
                {
                  "customizations": {
                    "vscode": {
                      "settings": {
                        "files.exclude": {
                          "docs/HYBRID_OPENAI_ADOPTION_PLAN.md": true
                        }
                      }
                    }
                  }
                }
                """,
            )

            failures = check_local_runtime_config.run(root)

        self.assertEqual(len(failures), 2)
        self.assertTrue(any("docs/POL1_COMMS.md" in failure for failure in failures))
        self.assertTrue(
            any(
                "docs/HYBRID_OPENAI_ADOPTION_PLAN.md" in failure for failure in failures
            )
        )

    def test_current_checkout_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "tools.check_local_runtime_config"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("[ok] local runtime config check passed", result.stdout)


if __name__ == "__main__":
    unittest.main()
