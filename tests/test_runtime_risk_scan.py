from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools import check_runtime_risk_scan


REPO_ROOT = Path(__file__).resolve().parents[1]


def _write_precommit(root: Path, text: str) -> None:
    path = root / ".pre-commit-config.yaml"
    path.write_text(text, encoding="utf-8")


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

    def test_retired_runtime_map_token_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            map_path = root / "docs" / "runtime" / "RUNTIME_SURFACE_MAP.md"
            map_path.parent.mkdir(parents=True)
            map_path.write_text("Startup and workspace bootstrap\n", encoding="utf-8")

            failures = check_runtime_risk_scan.check_runtime_surface_map(root)

        self.assertIn(
            "docs/runtime/RUNTIME_SURFACE_MAP.md: retired runtime map token "
            "'Startup and workspace bootstrap' is active",
            failures,
        )

    def test_missing_ci_docs_dependency_is_reported(self) -> None:
        failures = check_runtime_risk_scan.check_make_contracts(
            "\n".join(
                [
                    "ci-docs: path-leak-check scripts-check lint-docs",
                    "local-runtime-config-check:",
                    "risk-scan:",
                    "operator-alias-check:",
                ]
            )
        )

        self.assertIn("ci-docs: missing dependency 'risk-scan'", failures)

    def test_deprecated_eod_stop_target_is_reported(self) -> None:
        failures = check_runtime_risk_scan.check_make_contracts("eod-stop:\n")

        self.assertIn(
            "make target 'eod-stop': deprecated target is active",
            failures,
        )

    def test_missing_session_status_target_is_reported(self) -> None:
        make_lines = [
            f"{target}:"
            for target in check_runtime_risk_scan.REQUIRED_MAKE_TARGETS
            if target != "session-status"
        ]
        make_lines.append(
            "ci-docs: " + " ".join(check_runtime_risk_scan.REQUIRED_CI_DOCS_DEPS)
        )

        failures = check_runtime_risk_scan.check_make_contracts("\n".join(make_lines))

        self.assertIn(
            "make target 'session-status': missing from Make surface",
            failures,
        )

    def test_missing_operator_alias_dependency_is_reported(self) -> None:
        failures = check_runtime_risk_scan.check_make_contracts(
            "\n".join(
                [
                    "ci-docs: path-leak-check scripts-check risk-scan lint-docs",
                    "local-runtime-config-check:",
                    "risk-scan:",
                    "operator-alias-check:",
                ]
            )
        )

        self.assertIn(
            "ci-docs: missing dependency 'operator-alias-check'",
            failures,
        )

    def test_missing_local_runtime_config_dependency_is_reported(self) -> None:
        failures = check_runtime_risk_scan.check_make_contracts(
            "\n".join(
                [
                    "ci-docs: path-leak-check scripts-check risk-scan "
                    "operator-alias-check startup-contracts-check lint-docs",
                    "local-runtime-config-check:",
                    "risk-scan:",
                    "operator-alias-check:",
                    "startup-contracts-check:",
                ]
            )
        )

        self.assertIn(
            "ci-docs: missing dependency 'local-runtime-config-check'",
            failures,
        )

    def test_missing_startup_contracts_dependency_is_reported(self) -> None:
        failures = check_runtime_risk_scan.check_make_contracts(
            "\n".join(
                [
                    "ci-docs: path-leak-check scripts-check risk-scan "
                    "operator-alias-check lint-docs",
                    "local-runtime-config-check:",
                    "risk-scan:",
                    "operator-alias-check:",
                    "startup-contracts-check:",
                ]
            )
        )

        self.assertIn(
            "ci-docs: missing dependency 'startup-contracts-check'",
            failures,
        )

    def test_missing_precommit_local_hook_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_precommit(
                root,
                """
                exclude: ^(docs/peanut/|public/portfolio/assets/)
                repos:
                  - repo: local
                    hooks:
                      - id: polinko-ruff-check
                        entry: make ruff-check
                        language: system
                        pass_filenames: false
                        stages: [pre-commit, manual]
                      - id: polinko-ruff-format-check
                        entry: make ruff-format-check
                        language: system
                        pass_filenames: false
                        stages: [pre-commit, manual]
                """,
            )

            failures = check_runtime_risk_scan.check_precommit_config(root)

        self.assertIn(
            ".pre-commit-config.yaml: missing local hook 'polinko-markdownlint-docs'",
            failures,
        )

    def test_precommit_entry_drift_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_precommit(
                root,
                """
                exclude: ^(docs/peanut/|public/portfolio/assets/)
                repos:
                  - repo: local
                    hooks:
                      - id: polinko-ruff-check
                        entry: ruff check .
                        language: system
                        pass_filenames: false
                        stages: [pre-commit, manual]
                      - id: polinko-ruff-format-check
                        entry: make ruff-format-check
                        language: system
                        pass_filenames: false
                        stages: [pre-commit, manual]
                      - id: polinko-markdownlint-docs
                        entry: make lint-docs
                        language: system
                        pass_filenames: false
                        stages: [pre-commit, manual]
                """,
            )

            failures = check_runtime_risk_scan.check_precommit_config(root)

        self.assertIn(
            ".pre-commit-config.yaml: 'polinko-ruff-check' entry must be "
            "'make ruff-check'",
            failures,
        )

    def test_retired_precommit_hook_token_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_precommit(
                root,
                """
                exclude: ^(docs/peanut/|public/portfolio/assets/)
                repos:
                  - repo: local
                    hooks:
                      - id: polinko-isort
                        entry: isort .
                        language: system
                        pass_filenames: false
                        stages: [pre-commit, manual]
                """,
            )

            failures = check_runtime_risk_scan.check_precommit_config(root)

        self.assertIn(
            ".pre-commit-config.yaml: retired hook token 'isort' is active",
            failures,
        )


if __name__ == "__main__":
    unittest.main()
