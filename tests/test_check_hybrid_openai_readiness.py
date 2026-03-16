from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools import check_hybrid_openai_readiness as readiness


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


class HybridReadinessTests(unittest.TestCase):
    def test_run_passes_when_all_gates_are_green(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            reports = Path(tmp)
            _write_json(
                reports / "style-strict-20260316-100000.json",
                {"summary": {"total": 11, "passed": 11, "failed": 0}},
            )
            _write_json(
                reports / "file-search-20260316-100001.json",
                {
                    "summary": {
                        "total": 5,
                        "passed": 5,
                        "failed": 0,
                        "errors": 0,
                        "skipped": 0,
                    }
                },
            )
            clip_payload = {
                "cases_count": 4,
                "any_rate_delta_proxy_minus_baseline": 1.0,
                "summary": {
                    "baseline_mixed": {"errors": 0, "skipped": 0},
                    "clip_proxy_image_only": {"errors": 0, "skipped": 0, "any_rate": 1.0},
                },
            }
            _write_json(reports / "clip-ab-20260316-100002.json", clip_payload)
            _write_json(reports / "clip-ab-20260316-100003.json", clip_payload)

            overall, gate_results = readiness._run(
                reports_dir=reports,
                required_consecutive=2,
                min_cases=4,
                min_any_rate=0.90,
                min_delta=0.50,
            )

            self.assertTrue(overall)
            self.assertTrue(all(item.passed for item in gate_results))

    def test_run_fails_when_clip_delta_is_below_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            reports = Path(tmp)
            _write_json(
                reports / "style-strict-20260316-100000.json",
                {"summary": {"total": 11, "passed": 11, "failed": 0}},
            )
            _write_json(
                reports / "file-search-20260316-100001.json",
                {
                    "summary": {
                        "total": 5,
                        "passed": 5,
                        "failed": 0,
                        "errors": 0,
                        "skipped": 0,
                    }
                },
            )
            clip_payload_bad = {
                "cases_count": 4,
                "any_rate_delta_proxy_minus_baseline": 0.1,
                "summary": {
                    "baseline_mixed": {"errors": 0, "skipped": 0},
                    "clip_proxy_image_only": {"errors": 0, "skipped": 0, "any_rate": 1.0},
                },
            }
            _write_json(reports / "clip-ab-20260316-100002.json", clip_payload_bad)
            _write_json(reports / "clip-ab-20260316-100003.json", clip_payload_bad)

            overall, gate_results = readiness._run(
                reports_dir=reports,
                required_consecutive=2,
                min_cases=4,
                min_any_rate=0.90,
                min_delta=0.50,
            )

            self.assertFalse(overall)
            self.assertEqual(gate_results[0].name, "style_strict")
            self.assertEqual(gate_results[1].name, "file_search")
            self.assertEqual(gate_results[2].name, "clip_readiness_sequence")
            self.assertFalse(gate_results[2].passed)


if __name__ == "__main__":
    unittest.main()
