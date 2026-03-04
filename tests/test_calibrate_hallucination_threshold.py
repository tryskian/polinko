import json
import subprocess
import tempfile
import unittest
from pathlib import Path


class CalibrateHallucinationThresholdTests(unittest.TestCase):
    def test_calibration_generates_recommendation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports = root / "reports"
            reports.mkdir(parents=True)

            report_path = reports / "hallucination-sample.json"
            report_path.write_text(
                json.dumps(
                    {
                        "cases": [
                            {"id": "a", "pass": True, "score": 92, "risk": "low"},
                            {"id": "b", "pass": True, "score": 80, "risk": "medium"},
                            {"id": "c", "pass": False, "score": 45, "risk": "low"},
                            {"id": "d", "pass": False, "score": 85, "risk": "high"},
                        ]
                    }
                ),
                encoding="utf-8",
            )

            out_json = root / "calibration.json"
            result = subprocess.run(
                [
                    "python3",
                    "tools/calibrate_hallucination_threshold.py",
                    "--report-glob",
                    str(reports / "hallucination-*.json"),
                    "--out-json",
                    str(out_json),
                ],
                cwd=Path(__file__).resolve().parents[1],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            payload = json.loads(out_json.read_text(encoding="utf-8"))
            self.assertIn("recommended_min_acceptable_score", payload)
            self.assertGreaterEqual(payload["recommended_min_acceptable_score"], 0)
            self.assertLessEqual(payload["recommended_min_acceptable_score"], 100)
            self.assertEqual(payload["report_count"], 1)
            self.assertEqual(payload["case_count"], 4)


if __name__ == "__main__":
    unittest.main()
