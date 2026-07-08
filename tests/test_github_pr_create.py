from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "github_pr_create.sh"


class GitHubPrCreateTests(unittest.TestCase):
    def test_helper_routes_markdown_through_body_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            fake_gh = tmp_path / "gh"
            captured_args = tmp_path / "args.txt"
            body_file = tmp_path / "body.md"
            body_file.write_text(
                "Summary with `literal code span` in Markdown.\n",
                encoding="utf-8",
            )
            fake_gh.write_text(
                "\n".join(
                    [
                        "#!/usr/bin/env bash",
                        "set -euo pipefail",
                        'printf "%s\\n" "$@" >"$POLINKO_CAPTURE_ARGS"',
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            fake_gh.chmod(0o755)
            env = {**os.environ, "POLINKO_CAPTURE_ARGS": str(captured_args)}

            result = subprocess.run(
                [
                    str(SCRIPT),
                    "--gh",
                    str(fake_gh),
                    "--base",
                    "main",
                    "--head",
                    "codex/bigbrain/example",
                    "--title",
                    "Safe PR body",
                    "--body-file",
                    str(body_file),
                ],
                cwd=REPO_ROOT,
                env=env,
                check=False,
                capture_output=True,
                text=True,
            )
            captured = captured_args.read_text(encoding="utf-8").splitlines()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            captured,
            [
                "pr",
                "create",
                "--base",
                "main",
                "--head",
                "codex/bigbrain/example",
                "--title",
                "Safe PR body",
                "--body-file",
                str(body_file),
            ],
        )

    def test_helper_rejects_missing_body_file_argument(self) -> None:
        result = subprocess.run(
            [
                str(SCRIPT),
                "--gh",
                "gh",
                "--base",
                "main",
                "--head",
                "codex/bigbrain/example",
                "--title",
                "Missing body file",
            ],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("--body-file is required", result.stderr)

    def test_make_target_uses_safe_helper_not_inline_body(self) -> None:
        make_text = "\n".join(
            [
                (REPO_ROOT / "makefiles/config/ops/github.mk").read_text(
                    encoding="utf-8"
                ),
                (REPO_ROOT / "makefiles/checks/dev-tools/github.mk").read_text(
                    encoding="utf-8"
                ),
            ]
        )

        self.assertIn("GITHUB_PR_BASE ?= main", make_text)
        self.assertIn("GITHUB_PR_HEAD ?=", make_text)
        self.assertIn("GITHUB_PR_TITLE ?=", make_text)
        self.assertIn("GITHUB_PR_BODY_FILE ?=", make_text)
        self.assertIn("github-pr-create:", make_text)
        self.assertIn("./tools/github_pr_create.sh", make_text)
        self.assertIn('--body-file "$(GITHUB_PR_BODY_FILE)"', make_text)
        self.assertNotIn("--body ", make_text)

    def test_operator_docs_name_body_file_path_for_pr_creation(self) -> None:
        docs_text = "\n".join(
            [
                (REPO_ROOT / "docs/runtime/RUNBOOK.md").read_text(encoding="utf-8"),
                (REPO_ROOT / "docs/runtime/START_END_REFERENCE.md").read_text(
                    encoding="utf-8"
                ),
                (REPO_ROOT / "docs/governance/CHARTER.md").read_text(encoding="utf-8"),
            ]
        )

        self.assertIn("make github-pr-create", docs_text)
        self.assertIn("GITHUB_PR_BODY_FILE", docs_text)
        self.assertIn("`--body-file`", docs_text)


if __name__ == "__main__":
    unittest.main()
