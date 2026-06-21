from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools import check_shell_scripts


class CheckShellScriptsTests(unittest.TestCase):
    def test_check_script_reports_shell_syntax_errors(self) -> None:
        original_repo_root = check_shell_scripts.REPO_ROOT
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = root / "tools" / "bad.sh"
            script.parent.mkdir()
            script.write_text(
                "\n".join(
                    [
                        "#!/usr/bin/env bash",
                        "set -euo pipefail",
                        "if true; then",
                        "  echo broken",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            check_shell_scripts.REPO_ROOT = root
            try:
                failures = check_shell_scripts.check_script(Path("tools/bad.sh"))
            finally:
                check_shell_scripts.REPO_ROOT = original_repo_root

        self.assertTrue(
            any("fails bash syntax check" in failure for failure in failures),
            failures,
        )


if __name__ == "__main__":
    unittest.main()
