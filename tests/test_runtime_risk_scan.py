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


def _make_contract_text(
    *,
    ci_docs_deps: tuple[str, ...] | None = None,
    build_hygiene_deps: tuple[str, ...] | None = None,
    omit_targets: set[str] | None = None,
    extra_lines: tuple[str, ...] = (),
) -> str:
    omit = omit_targets or set()
    lines = [
        f"{target}:"
        for target in check_runtime_risk_scan.REQUIRED_MAKE_TARGETS
        if target not in omit
    ]
    lines.append(
        "ci-docs: "
        + " ".join(ci_docs_deps or check_runtime_risk_scan.REQUIRED_CI_DOCS_DEPS)
    )
    lines.append(
        "build-hygiene: "
        + " ".join(
            build_hygiene_deps or check_runtime_risk_scan.REQUIRED_BUILD_HYGIENE_DEPS
        )
    )
    lines.extend(extra_lines)
    return "\n".join(lines)


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
            _make_contract_text(
                ci_docs_deps=("path-leak-check", "scripts-check", "lint-docs")
            )
        )

        self.assertIn("ci-docs: missing dependency 'risk-scan'", failures)

    def test_duplicate_eod_target_is_reported(self) -> None:
        failures = check_runtime_risk_scan.check_make_contracts(
            _make_contract_text(extra_lines=("eod:",))
        )

        self.assertIn(
            "make target 'eod': deprecated target is active",
            failures,
        )

    def test_deprecated_eod_stop_target_is_reported(self) -> None:
        failures = check_runtime_risk_scan.check_make_contracts(
            _make_contract_text(extra_lines=("eod-stop:",))
        )

        self.assertIn(
            "make target 'eod-stop': deprecated target is active",
            failures,
        )

    def test_retired_eval_shortcut_include_path_is_reported(self) -> None:
        failures = check_runtime_risk_scan.check_make_contracts(
            _make_contract_text(
                extra_lines=("include makefiles/evals/aliases/ocr-runs.mk",)
            )
        )

        self.assertIn(
            "Make surface: retired include token 'makefiles/evals/aliases' is active",
            failures,
        )

    def test_missing_session_status_target_is_reported(self) -> None:
        failures = check_runtime_risk_scan.check_make_contracts(
            _make_contract_text(omit_targets={"session-status"})
        )

        self.assertIn(
            "make target 'session-status': missing from Make surface",
            failures,
        )

    def test_missing_operator_command_dependency_is_reported(self) -> None:
        failures = check_runtime_risk_scan.check_make_contracts(
            _make_contract_text(
                ci_docs_deps=(
                    "path-leak-check",
                    "scripts-check",
                    "risk-scan",
                    "lint-docs",
                )
            )
        )

        self.assertIn(
            "ci-docs: missing dependency 'operator-command-check'",
            failures,
        )

    def test_missing_local_runtime_config_dependency_is_reported(self) -> None:
        failures = check_runtime_risk_scan.check_make_contracts(
            _make_contract_text(
                ci_docs_deps=(
                    "path-leak-check",
                    "scripts-check",
                    "risk-scan",
                    "operator-command-check",
                    "startup-contracts-check",
                    "lint-docs",
                )
            )
        )

        self.assertIn(
            "ci-docs: missing dependency 'local-runtime-config-check'",
            failures,
        )

    def test_missing_startup_contracts_dependency_is_reported(self) -> None:
        failures = check_runtime_risk_scan.check_make_contracts(
            _make_contract_text(
                ci_docs_deps=(
                    "path-leak-check",
                    "scripts-check",
                    "risk-scan",
                    "operator-command-check",
                    "lint-docs",
                )
            )
        )

        self.assertIn(
            "ci-docs: missing dependency 'startup-contracts-check'",
            failures,
        )

    def test_missing_build_hygiene_dependency_is_reported(self) -> None:
        failures = check_runtime_risk_scan.check_make_contracts(
            _make_contract_text(build_hygiene_deps=("transcript-check", "ci"))
        )

        self.assertIn(
            "build-hygiene: missing dependency 'doctor-env'",
            failures,
        )

    def test_missing_precommit_local_hook_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_precommit(
                root,
                """
                exclude: ^docs/peanut/
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
                exclude: ^docs/peanut/
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
                exclude: ^docs/peanut/
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

    def test_dependency_pin_literal_in_tests_is_reported(self) -> None:
        httpx2_pin = "httpx2==" + "2.5.0"
        pyright_version = "1.1." + "411"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tests_dir = root / "tests"
            tests_dir.mkdir()
            (root / "requirements.in").write_text(f"{httpx2_pin}\n", encoding="utf-8")
            (root / "package.json").write_text(
                f'{{"devDependencies": {{"pyright": "{pyright_version}"}}}}',
                encoding="utf-8",
            )
            (tests_dir / "test_dependency_contract.py").write_text(
                f'self.assertIn("{httpx2_pin}", requirements_input)\n',
                encoding="utf-8",
            )

            failures = check_runtime_risk_scan.check_dependency_test_contracts(root)

        self.assertEqual(
            failures,
            [
                "tests/test_dependency_contract.py: dependency test contract "
                f"hard-codes live dependency version {httpx2_pin!r}; derive it "
                "from the dependency source file instead"
            ],
        )

    def test_node_dependency_version_literal_in_tests_is_reported(self) -> None:
        pyright_version = "1.1." + "411"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tests_dir = root / "tests"
            tests_dir.mkdir()
            (root / "requirements.in").write_text("", encoding="utf-8")
            (root / "package.json").write_text(
                f'{{"devDependencies": {{"pyright": "{pyright_version}"}}}}',
                encoding="utf-8",
            )
            (tests_dir / "test_typecheck_contract.py").write_text(
                "self.assertEqual("
                f'package["devDependencies"]["pyright"], "{pyright_version}")\n',
                encoding="utf-8",
            )

            failures = check_runtime_risk_scan.check_dependency_test_contracts(root)

        self.assertEqual(
            failures,
            [
                "tests/test_typecheck_contract.py: dependency test contract "
                f"hard-codes live dependency version {pyright_version!r}; "
                "derive it from the dependency source file instead"
            ],
        )


if __name__ == "__main__":
    unittest.main()
