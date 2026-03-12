import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.eval_clip_ab_readiness import _evaluate_report
from tools.eval_clip_ab_readiness import _load_evaluations


def _report_payload(
    *,
    run_id: str,
    timestamp_unix: int,
    cases_count: int,
    proxy_any_rate: float,
    delta: float,
    baseline_errors: int = 0,
    baseline_skipped: int = 0,
    proxy_errors: int = 0,
    proxy_skipped: int = 0,
) -> dict[str, object]:
    baseline_any_rate = proxy_any_rate - delta
    return {
        "run_id": run_id,
        "timestamp_unix": timestamp_unix,
        "cases_count": cases_count,
        "summary": {
            "baseline_mixed": {
                "errors": baseline_errors,
                "skipped": baseline_skipped,
                "any_rate": baseline_any_rate,
            },
            "clip_proxy_image_only": {
                "errors": proxy_errors,
                "skipped": proxy_skipped,
                "any_rate": proxy_any_rate,
            },
        },
        "any_rate_delta_proxy_minus_baseline": delta,
    }


class ClipABReadinessTests(unittest.TestCase):
    def test_evaluate_report_passes_when_thresholds_are_met(self) -> None:
        evaluation = _evaluate_report(
            path=Path("clip-ab-sample.json"),
            payload=_report_payload(
                run_id="20260312-101010",
                timestamp_unix=100,
                cases_count=4,
                proxy_any_rate=1.0,
                delta=0.75,
            ),
            min_cases=4,
            min_proxy_any_rate=0.9,
            min_delta=0.5,
        )

        self.assertTrue(evaluation.passed)
        self.assertEqual(evaluation.reasons, ())

    def test_evaluate_report_collects_all_failure_reasons(self) -> None:
        evaluation = _evaluate_report(
            path=Path("clip-ab-sample.json"),
            payload=_report_payload(
                run_id="20260312-101010",
                timestamp_unix=100,
                cases_count=3,
                proxy_any_rate=0.6,
                delta=0.2,
                proxy_skipped=1,
            ),
            min_cases=4,
            min_proxy_any_rate=0.9,
            min_delta=0.5,
        )

        self.assertFalse(evaluation.passed)
        self.assertIn("cases_count 3 < 4", evaluation.reasons)
        self.assertIn("proxy any_rate 0.600 < 0.900", evaluation.reasons)
        self.assertIn("delta +0.200 < +0.500", evaluation.reasons)
        self.assertIn("clip_proxy_image_only skipped 1 != 0", evaluation.reasons)

    def test_load_evaluations_sorts_by_report_timestamp(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            early = root / "clip-ab-20260310-123934.json"
            late = root / "clip-ab-20260310-125230.json"
            early.write_text(
                json.dumps(
                    _report_payload(
                        run_id="20260310-123934",
                        timestamp_unix=10,
                        cases_count=4,
                        proxy_any_rate=1.0,
                        delta=1.0,
                    )
                ),
                encoding="utf-8",
            )
            late.write_text(
                json.dumps(
                    _report_payload(
                        run_id="20260310-125230",
                        timestamp_unix=20,
                        cases_count=4,
                        proxy_any_rate=1.0,
                        delta=1.0,
                    )
                ),
                encoding="utf-8",
            )

            evaluations = _load_evaluations(
                report_glob=str(root / "clip-ab-*.json"),
                min_cases=4,
                min_proxy_any_rate=0.9,
                min_delta=0.5,
            )

            self.assertEqual([item.run_id for item in evaluations], ["20260310-123934", "20260310-125230"])

    def test_cli_returns_go_for_two_consecutive_passing_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for run_id, timestamp in (("20260310-123934", 10), ("20260310-125230", 20)):
                report_path = root / f"clip-ab-{run_id}.json"
                report_path.write_text(
                    json.dumps(
                        _report_payload(
                            run_id=run_id,
                            timestamp_unix=timestamp,
                            cases_count=4,
                            proxy_any_rate=1.0,
                            delta=1.0,
                        )
                    ),
                    encoding="utf-8",
                )

            result = subprocess.run(
                [
                    "python3",
                    "tools/eval_clip_ab_readiness.py",
                    "--report-glob",
                    str(root / "clip-ab-*.json"),
                ],
                cwd=Path(__file__).resolve().parents[1],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("GO", result.stdout)
            self.assertIn("20260310-123934", result.stdout)
            self.assertIn("20260310-125230", result.stdout)

    def test_cli_returns_no_go_when_latest_two_are_not_both_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report_specs = [
                ("20260310-101010", 10, 4, 1.0, 1.0),
                ("20260310-111111", 20, 3, 1.0, 1.0),
                ("20260310-121212", 30, 4, 1.0, 1.0),
            ]
            for run_id, timestamp, cases_count, proxy_any_rate, delta in report_specs:
                report_path = root / f"clip-ab-{run_id}.json"
                report_path.write_text(
                    json.dumps(
                        _report_payload(
                            run_id=run_id,
                            timestamp_unix=timestamp,
                            cases_count=cases_count,
                            proxy_any_rate=proxy_any_rate,
                            delta=delta,
                        )
                    ),
                    encoding="utf-8",
                )

            result = subprocess.run(
                [
                    "python3",
                    "tools/eval_clip_ab_readiness.py",
                    "--report-glob",
                    str(root / "clip-ab-*.json"),
                ],
                cwd=Path(__file__).resolve().parents[1],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 1, msg=result.stderr)
            self.assertIn("NO-GO", result.stdout)
            self.assertIn("20260310-111111", result.stdout)
            self.assertIn("cases_count 3 < 4", result.stdout)


if __name__ == "__main__":
    unittest.main()
