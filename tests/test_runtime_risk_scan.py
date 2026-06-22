from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools import check_runtime_risk_scan


REPO_ROOT = Path(__file__).resolve().parents[1]


class RuntimeRiskScanTests(unittest.TestCase):
    def test_current_repo_passes_runtime_risk_scan(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "tools.check_runtime_risk_scan"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("[ok] runtime risk scan passed", result.stdout)

    def test_missing_runtime_surface_map_token_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            map_path = root / "docs" / "runtime" / "RUNTIME_SURFACE_MAP.md"
            map_path.parent.mkdir(parents=True)
            map_path.write_text("make start\n", encoding="utf-8")

            failures = check_runtime_risk_scan.check_runtime_surface_map(root)

        self.assertIn(
            "docs/runtime/RUNTIME_SURFACE_MAP.md: startup omits "
            "'tools/start_of_day_routine.sh'",
            failures,
        )

    def test_missing_ci_docs_dependency_is_reported(self) -> None:
        failures = check_runtime_risk_scan.check_make_contracts(
            "\n".join(
                [
                    "ci-docs: path-leak-check scripts-check lint-docs",
                    "risk-scan:",
                ]
            )
        )

        self.assertIn("ci-docs: missing dependency 'risk-scan'", failures)


if __name__ == "__main__":
    unittest.main()
