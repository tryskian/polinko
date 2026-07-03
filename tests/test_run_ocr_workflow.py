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


def _fake_make_run(target: str) -> tuple[list[str], Path]:
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
            ["bash", str(SCRIPT), target],
            cwd=REPO_ROOT / "docs",
            env=env,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise AssertionError(result.stderr or result.stdout)
        return make_log.read_text(encoding="utf-8").splitlines(), export_root


class RunOcrWorkflowTests(unittest.TestCase):
    def test_ocrkernel_uses_expected_make_sequence_from_subdirectory(self) -> None:
        log_lines, export_root = _fake_make_run("ocrkernel")

        self.assertEqual(
            log_lines,
            [
                f"pwd={REPO_ROOT} args: <--no-print-directory> <doctor-env>",
                f"pwd={REPO_ROOT} args: <--no-print-directory> <ocrmine> "
                f"<CGPT_EXPORT_ROOT={export_root}>",
                f"pwd={REPO_ROOT} args: <--no-print-directory> <ocrdelta>",
                f"pwd={REPO_ROOT} args: <--no-print-directory> <ocrwiden>",
                f"pwd={REPO_ROOT} args: <--no-print-directory> <ocrstablegrowth>",
                f"pwd={REPO_ROOT} args: <--no-print-directory> <ocrgrowth>",
                f"pwd={REPO_ROOT} args: <--no-print-directory> <ocrfails>",
                f"pwd={REPO_ROOT} args: <--no-print-directory> <ocrfocuscases>",
                f"pwd={REPO_ROOT} args: <--no-print-directory> "
                "<eval-ocr-focus-stability>",
                f"pwd={REPO_ROOT} args: <--no-print-directory> <ocrfocusreport>",
            ],
        )

    def test_ocr_data_uses_expected_make_sequence_from_subdirectory(self) -> None:
        log_lines, export_root = _fake_make_run("ocr-data")

        self.assertEqual(
            log_lines,
            [
                f"pwd={REPO_ROOT} args: <--no-print-directory> <doctor-env>",
                f"pwd={REPO_ROOT} args: <--no-print-directory> <ocrmine> "
                f"<CGPT_EXPORT_ROOT={export_root}>",
                f"pwd={REPO_ROOT} args: <--no-print-directory> "
                "<ocr-generalization-review>",
                f"pwd={REPO_ROOT} args: <--no-print-directory> <ocrdelta>",
            ],
        )

    def test_ocr_notebook_workflow_uses_default_export_root_from_subdirectory(
        self,
    ) -> None:
        log_lines, export_root = _fake_make_run("ocr-notebook-workflow")

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

    def test_reports_missing_make_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing_make = Path(tmp) / "missing-make"
            export_root = Path(tmp) / "export"
            export_root.mkdir()
            env = os.environ.copy()
            env.update(
                {
                    "CGPT_EXPORT_ROOT": str(export_root),
                    "CGPT_EXPORT_ROOT_DEFAULT": "",
                    "MAKE": str(missing_make),
                }
            )

            result = subprocess.run(
                ["bash", str(SCRIPT.relative_to(REPO_ROOT)), "ocr-data"],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn(
                f"ocr-workflow: missing make command: {missing_make}",
                result.stderr,
            )


if __name__ == "__main__":
    unittest.main()
