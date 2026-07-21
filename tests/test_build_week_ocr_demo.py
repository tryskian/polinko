from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
    return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


class BuildWeekOcrDemoTests(unittest.TestCase):
    def test_build_week_demo_make_target_uses_runner(self) -> None:
        makefile = _read("makefiles/evals/core/reports.mk")

        self.assertIn("build-week-demo:", makefile)
        self.assertIn("bash ./tools/run_build_week_demo.sh", makefile)
        self.assertIn("build-week-ocr-demo:", makefile)
        self.assertIn("bash ./tools/run_build_week_ocr_demo.sh", makefile)
        self.assertIn("build-week-ocr-notebook-demo:", makefile)
        self.assertIn("bash ./tools/run_build_week_ocr_notebook_demo.sh", makefile)
        self.assertIn("build-week-ocr-smoke-demo:", makefile)
        self.assertIn("bash ./tools/run_build_week_ocr_smoke_demo.sh", makefile)

    def test_build_week_demo_runner_surfaces_are_tracked(self) -> None:
        for rel_path in (
            "tools/run_build_week_demo.sh",
            "tools/run_build_week_ocr_demo.sh",
            "tools/run_build_week_ocr_notebook_demo.sh",
            "tools/run_build_week_ocr_smoke_demo.sh",
        ):
            self.assertTrue((REPO_ROOT / rel_path).is_file(), rel_path)

    def test_build_week_demo_keeps_source_preview_in_terminal(self) -> None:
        script = _read("tools/run_build_week_demo.sh")

        self.assertIn('print(f"image={resolved_image}")', script)
        self.assertIn('pass "OCR source image resolved"', script)
        self.assertNotIn("BUILD_WEEK_DEMO_OPEN_OCR_SOURCE", script)
        self.assertNotIn('open "$ocr_source_image"', script)

    def test_build_week_demo_runner_is_bounded_and_self_cleaning(self) -> None:
        script = _read("tools/run_build_week_ocr_demo.sh")

        self.assertIn('source "$script_dir/repo_root.sh"', script)
        self.assertIn('source "$script_dir/make_runtime.sh"', script)
        self.assertIn('source "$script_dir/python_runtime.sh"', script)
        self.assertIn("trap cleanup EXIT", script)
        self.assertIn("server-daemon-stop", script)
        self.assertIn("OCR_GROWTH_EVAL_MAX_CASES=1", script)
        self.assertIn("summary_written=", script)
        self.assertIn("extracted_text_recorded=yes", script)
