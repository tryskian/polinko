import os
import stat
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "run_ocr_workflow.sh"


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


class RunOcrWorkflowTests(unittest.TestCase):
    def test_ocr_notebook_workflow_uses_default_export_root_from_subdirectory(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            export_root = tmp_path / "export"
            export_root.mkdir()
            make_log = tmp_path / "make.log"
            fake_make = tmp_path / "make.sh"
            _write_executable(
                fake_make,
                textwrap.dedent(
                    """\
                    #!/usr/bin/env sh
                    set -eu
                    printf 'pwd=%s args:' "$PWD" >> "$MAKE_LOG"
                    for arg in "$@"; do
                        printf ' <%s>' "$arg" >> "$MAKE_LOG"
                    done
                    printf '\\n' >> "$MAKE_LOG"
                    """
                ),
            )
            env = os.environ.copy()
            env.update(
                {
                    "CGPT_EXPORT_ROOT": "",
                    "CGPT_EXPORT_ROOT_DEFAULT": str(export_root),
                    "MAKE": str(fake_make),
                    "MAKE_LOG": str(make_log),
                }
            )

            result = subprocess.run(
                ["bash", str(SCRIPT), "ocr-notebook-workflow"],
                cwd=REPO_ROOT / "docs",
                env=env,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            log_lines = make_log.read_text(encoding="utf-8").splitlines()

        self.assertEqual(
            log_lines,
            [
                f"pwd={REPO_ROOT} args: <--no-print-directory> <doctor-env>",
                f"pwd={REPO_ROOT} args: <--no-print-directory> <ocrmine> "
                f"<CGPT_EXPORT_ROOT={export_root}>",
                f"pwd={REPO_ROOT} args: <--no-print-directory> <ocrall>",
                f"pwd={REPO_ROOT} args: <--no-print-directory> <ocrstable>",
                f"pwd={REPO_ROOT} args: <--no-print-directory> <ocrwiden>",
                f"pwd={REPO_ROOT} args: <--no-print-directory> <ocrstablegrowth>",
                f"pwd={REPO_ROOT} args: <--no-print-directory> <ocrgrowth>",
                f"pwd={REPO_ROOT} args: <--no-print-directory> <ocrfails>",
            ],
        )

    def test_ocr_notebook_workflow_missing_export_root_uses_target_guidance(
        self,
    ) -> None:
        env = os.environ.copy()
        env.update({"CGPT_EXPORT_ROOT": "", "CGPT_EXPORT_ROOT_DEFAULT": ""})

        result = subprocess.run(
            ["bash", str(SCRIPT), "ocr-notebook-workflow"],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("CGPT_EXPORT_ROOT is required.", result.stdout)
        self.assertIn(
            "make ocr-notebook-workflow CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT",
            result.stdout,
        )


if __name__ == "__main__":
    unittest.main()
