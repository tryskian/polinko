import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_SCRIPT = REPO_ROOT / "tools" / "run_ocr_intake_workflow.sh"


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


class OcrIntakeWorkflowTests(unittest.TestCase):
    def _python_env(self, tmp_path: Path) -> tuple[dict[str, str], Path]:
        python_args = tmp_path / "python-args.txt"
        python_script = tmp_path / "python.sh"
        _write_executable(
            python_script,
            '#!/usr/bin/env sh\nset -eu\nprintf "%s\\n" "$@" > "$PYTHON_ARGS"\n',
        )

        env = os.environ.copy()
        env.pop("CGPT_EXPORT_ROOT", None)
        env.pop("CGPT_EXPORT_ROOT_DEFAULT", None)
        env.update(
            {
                "PYTHON": str(python_script),
                "PYTHON_ARGS": str(python_args),
            }
        )
        return env, python_args

    def _run(
        self,
        env: dict[str, str],
        *args: str,
        cwd: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(WORKFLOW_SCRIPT), *args],
            cwd=cwd or REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
        )

    def test_export_index_uses_default_export_root_and_output_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            env, python_args = self._python_env(tmp_path)
            export_root = tmp_path / "export"
            output_dir = tmp_path / "cases"
            export_root.mkdir()
            env.update(
                {
                    "CGPT_EXPORT_ROOT_DEFAULT": str(export_root),
                    "CGPT_EXPORT_OUTPUT_DIR": str(output_dir),
                }
            )

            result = self._run(env, "export-index")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                python_args.read_text(encoding="utf-8").splitlines(),
                [
                    "-m",
                    "tools.index_cgpt_export",
                    "--export-root",
                    str(export_root),
                    "--output-dir",
                    str(output_dir),
                ],
            )

    def test_export_index_uses_repo_default_output_dir_from_subdirectory(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            env, python_args = self._python_env(tmp_path)
            export_root = tmp_path / "export"
            export_root.mkdir()
            env["CGPT_EXPORT_ROOT_DEFAULT"] = str(export_root)

            result = self._run(env, "export-index", cwd=REPO_ROOT / "docs")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                python_args.read_text(encoding="utf-8").splitlines(),
                [
                    "-m",
                    "tools.index_cgpt_export",
                    "--export-root",
                    str(export_root),
                    "--output-dir",
                    ".local/eval_cases",
                ],
            )

    def test_cases_from_export_snapshots_review_and_forwards_extra_args(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            env, python_args = self._python_env(tmp_path)
            export_root = tmp_path / "export"
            export_root.mkdir()
            review = tmp_path / "review.json"
            previous_review = tmp_path / "review-prev.json"
            review.write_text('{"before": true}\n', encoding="utf-8")
            env.update(
                {
                    "CGPT_EXPORT_ROOT": str(export_root),
                    "OCR_TRANSCRIPT_CASES_ALL": str(tmp_path / "all.json"),
                    "OCR_TRANSCRIPT_CASES_GROWTH": str(tmp_path / "growth.json"),
                    "OCR_TRANSCRIPT_CASES_HANDWRITING": str(
                        tmp_path / "handwriting.json"
                    ),
                    "OCR_TRANSCRIPT_CASES_TYPED": str(tmp_path / "typed.json"),
                    "OCR_TRANSCRIPT_CASES_ILLUSTRATION": str(
                        tmp_path / "illustration.json"
                    ),
                    "OCR_TRANSCRIPT_REVIEW": str(review),
                    "OCR_TRANSCRIPT_REVIEW_PREV": str(previous_review),
                    "OCR_GENERALIZATION_CANDIDATES": str(tmp_path / "candidates.json"),
                    "OCR_GROWTH_MAX_CASES": "12",
                }
            )

            result = self._run(
                env,
                "cases-from-export-build",
                "--include-lanes",
                "handwriting",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                previous_review.read_text(encoding="utf-8"),
                '{"before": true}\n',
            )
            self.assertEqual(
                python_args.read_text(encoding="utf-8").splitlines(),
                [
                    "-m",
                    "tools.build_ocr_cases_from_export",
                    "--export-root",
                    str(export_root),
                    "--output-cases",
                    str(tmp_path / "all.json"),
                    "--output-cases-growth",
                    str(tmp_path / "growth.json"),
                    "--output-cases-handwriting",
                    str(tmp_path / "handwriting.json"),
                    "--output-cases-typed",
                    str(tmp_path / "typed.json"),
                    "--output-cases-illustration",
                    str(tmp_path / "illustration.json"),
                    "--output-review",
                    str(review),
                    "--output-generalization-candidates",
                    str(tmp_path / "candidates.json"),
                    "--max-growth-cases",
                    "12",
                    "--include-lanes",
                    "handwriting",
                ],
            )

    def test_benchmark_lanes_route_to_expected_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            env, python_args = self._python_env(tmp_path)
            review = tmp_path / "review.json"
            review.write_text("{}", encoding="utf-8")
            lane_expectations = {
                "handwriting": ("OCR_TRANSCRIPT_CASES_HANDWRITING", "6", "3"),
                "typed": ("OCR_TRANSCRIPT_CASES_TYPED", "8", "3"),
                "illustration": ("OCR_TRANSCRIPT_CASES_ILLUSTRATION", "6", "2"),
            }
            env["OCR_TRANSCRIPT_REVIEW"] = str(review)
            env["OCR_HANDWRITING_BENCHMARK_TOP_K"] = "6"
            env["OCR_HANDWRITING_BENCHMARK_MIN_ANCHORS"] = "3"
            env["OCR_TYPED_BENCHMARK_TOP_K"] = "8"
            env["OCR_TYPED_BENCHMARK_MIN_ANCHORS"] = "3"
            env["OCR_ILLUSTRATION_BENCHMARK_TOP_K"] = "6"
            env["OCR_ILLUSTRATION_BENCHMARK_MIN_ANCHORS"] = "2"

            for lane, (cases_key, top_k, min_anchors) in lane_expectations.items():
                with self.subTest(lane=lane):
                    lane_cases = tmp_path / f"{lane}.json"
                    output_cases = tmp_path / f"{lane}-benchmark.json"
                    lane_cases.write_text("[]", encoding="utf-8")
                    env[cases_key] = str(lane_cases)
                    env[f"OCR_TRANSCRIPT_CASES_{lane.upper()}_BENCHMARK"] = str(
                        output_cases
                    )
                    if python_args.exists():
                        python_args.unlink()

                    result = self._run(env, "benchmark", lane)

                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(
                        python_args.read_text(encoding="utf-8").splitlines(),
                        [
                            "-m",
                            "tools.build_handwriting_benchmark_cases",
                            "--review",
                            str(review),
                            "--lane",
                            lane,
                            "--lane-cases",
                            str(lane_cases),
                            "--output-cases",
                            str(output_cases),
                            "--top-k",
                            top_k,
                            "--min-anchor-terms",
                            min_anchors,
                        ],
                    )

    def test_generalization_review_routes_to_builder_after_preflight(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            env, python_args = self._python_env(tmp_path)
            candidates = tmp_path / "candidates.json"
            output_review = tmp_path / "generalization-review.json"
            candidates.write_text("[]", encoding="utf-8")
            env.update(
                {
                    "OCR_GENERALIZATION_CANDIDATES": str(candidates),
                    "OCR_GENERALIZATION_REVIEW": str(output_review),
                    "OCR_GENERALIZATION_REVIEW_MAX_CASES": "9",
                    "OCR_GENERALIZATION_REVIEW_MAX_PER_CONVERSATION": "1",
                    "OCR_GENERALIZATION_REVIEW_INCLUDE_IDS": "a,b",
                }
            )

            result = self._run(env, "generalization-review")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                python_args.read_text(encoding="utf-8").splitlines(),
                [
                    "-m",
                    "tools.build_ocr_generalization_review",
                    "--candidates",
                    str(candidates),
                    "--output-review",
                    str(output_review),
                    "--max-cases",
                    "9",
                    "--max-per-conversation",
                    "1",
                    "--include-candidate-ids",
                    "a,b",
                ],
            )

    def test_transcript_delta_prints_report_path_after_python(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            env, python_args = self._python_env(tmp_path)
            review = tmp_path / "review.json"
            previous_review = tmp_path / "review-prev.json"
            markdown = tmp_path / "delta.md"
            json_report = tmp_path / "delta.json"
            env.update(
                {
                    "OCR_TRANSCRIPT_REVIEW": str(review),
                    "OCR_TRANSCRIPT_REVIEW_PREV": str(previous_review),
                    "OCR_TRANSCRIPT_DELTA_MD": str(markdown),
                    "OCR_TRANSCRIPT_DELTA_JSON": str(json_report),
                }
            )

            result = self._run(env, "transcript-delta")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(f"OCR transcript delta report: {markdown}", result.stdout)
            self.assertEqual(
                python_args.read_text(encoding="utf-8").splitlines(),
                [
                    "-m",
                    "tools.report_ocr_case_mining_delta",
                    "--current-review",
                    str(review),
                    "--previous-review",
                    str(previous_review),
                    "--output-markdown",
                    str(markdown),
                    "--output-json",
                    str(json_report),
                ],
            )

    def test_missing_export_root_preserves_guidance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            env, python_args = self._python_env(tmp_path)

            result = self._run(env, "export-index")

        self.assertEqual(result.returncode, 2)
        self.assertIn("CGPT_EXPORT_ROOT is required.", result.stdout)
        self.assertIn(
            "Run: make cgpt-export-index CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT",
            result.stdout,
        )
        self.assertFalse(python_args.exists())

    def test_missing_benchmark_review_preserves_message(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            env, python_args = self._python_env(tmp_path)
            missing_review = tmp_path / "missing-review.json"
            env["OCR_TRANSCRIPT_REVIEW"] = str(missing_review)

            result = self._run(env, "benchmark", "handwriting")

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            f"Transcript OCR review not found: {missing_review}",
            result.stdout,
        )
        self.assertFalse(python_args.exists())

    def test_missing_generalization_candidates_preserves_guidance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            env, python_args = self._python_env(tmp_path)
            missing_candidates = tmp_path / "missing-candidates.json"
            env["OCR_GENERALIZATION_CANDIDATES"] = str(missing_candidates)

            result = self._run(env, "generalization-review")

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            f"OCR generalization candidates not found: {missing_candidates}",
            result.stdout,
        )
        self.assertIn(
            "Run: make ocrmine CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT",
            result.stdout,
        )
        self.assertFalse(python_args.exists())

    def test_rejects_unknown_or_missing_suite(self) -> None:
        for args in ([], ["unknown"], ["benchmark"], ["benchmark", "unknown"]):
            with self.subTest(args=args):
                result = self._run(os.environ.copy(), *args)

                self.assertEqual(result.returncode, 2)
                self.assertTrue(
                    "Usage:" in result.stderr or "Unknown OCR intake" in result.stderr
                )


if __name__ == "__main__":
    unittest.main()
