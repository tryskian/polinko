from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.eval_sidecar import _extract_failure_signals
from tools.eval_sidecar import _failure_counter
from tools.eval_sidecar import _render_status


class EvalSidecarTests(unittest.TestCase):
    def test_extract_failure_signals_reads_fail_lines(self) -> None:
        text = "\n".join(
            [
                "[PASS] one_case attempt=1/3 score=9",
                "[FAIL] nonperformative_working_style_contract attempt=1/3 score=9",
                "[FAIL] uncertainty_required_no_relationship_motive_guess score=0",
            ]
        )
        self.assertEqual(
            _extract_failure_signals(text),
            [
                "nonperformative_working_style_contract",
                "uncertainty_required_no_relationship_motive_guess",
            ],
        )

    def test_failure_counter_aggregates_across_cycles(self) -> None:
        failures = [
            "[FAIL] nonperformative_working_style_contract attempt=1/3 score=9\n",
            "\n".join(
                [
                    "[FAIL] nonperformative_working_style_contract attempt=2/3 score=9",
                    "[FAIL] uncertainty_required_no_relationship_motive_guess score=0",
                ]
            ),
        ]
        self.assertEqual(
            _failure_counter(failures),
            [
                {"signal": "nonperformative_working_style_contract", "count": 2},
                {"signal": "uncertainty_required_no_relationship_motive_guess", "count": 1},
            ],
        )

    def test_render_status_includes_recent_failure_signals(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            pid_file = Path(tmpdir) / "sidecar.pid"
            pid_file.write_text("12345", encoding="utf-8")
            status = {
                "state": "running",
                "run_id": "20260509-130000",
                "target": "quality-gate-deterministic",
                "run_dir": ".local/eval_runs/eval-sidecar-20260509-130000",
                "started_at": "2026-05-09T17:00:00Z",
                "elapsed_seconds": 120,
                "min_seconds": 3600,
                "cycles_completed": 2,
                "pass_cycles": 1,
                "fail_cycles": 1,
                "current_cycle": 3,
                "last_cycle_status": "fail",
                "stop_requested": False,
                "recent_failure_signals": [
                    {"signal": "nonperformative_working_style_contract", "count": 1}
                ],
            }
            text = _render_status(status, pid_file)
            self.assertIn("eval-sidecar: RUNNING", text)
            self.assertIn("pass_cycles: 1", text)
            self.assertIn("- nonperformative_working_style_contract: 1", text)
            self.assertIn("pid: 12345", text)


if __name__ == "__main__":
    unittest.main()
