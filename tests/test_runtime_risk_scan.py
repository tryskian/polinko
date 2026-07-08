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
    build_hygiene_core_deps: tuple[str, ...] | None = None,
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
        "build-hygiene-core: "
        + " ".join(
            build_hygiene_core_deps
            or check_runtime_risk_scan.REQUIRED_BUILD_HYGIENE_CORE_DEPS
        )
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

    def test_non_current_runtime_map_token_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            map_path = root / "docs" / "runtime" / "RUNTIME_SURFACE_MAP.md"
            map_path.parent.mkdir(parents=True)
            map_path.write_text("Startup and workspace bootstrap\n", encoding="utf-8")

            failures = check_runtime_risk_scan.check_runtime_surface_map(root)

        self.assertIn(
            "docs/runtime/RUNTIME_SURFACE_MAP.md: non-current runtime map token "
            "'Startup and workspace bootstrap' is active",
            failures,
        )

    def test_current_operator_docs_use_canonical_lifecycle_names(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs_path = root / "docs" / "runtime" / "START_END_REFERENCE.md"
            docs_path.parent.mkdir(parents=True)
            docs_path.write_text("Use `make eod` for closeout.\n", encoding="utf-8")

            failures = check_runtime_risk_scan.check_current_lifecycle_doc_names(root)

        self.assertIn(
            "docs/runtime/START_END_REFERENCE.md: use canonical lifecycle command "
            "'make end'",
            failures,
        )

    def test_decision_log_can_retain_lifecycle_history(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            decisions_path = root / "docs" / "governance" / "DECISIONS.md"
            decisions_path.parent.mkdir(parents=True)
            decisions_path.write_text(
                "Historical note: `make eod`.\n", encoding="utf-8"
            )

            failures = check_runtime_risk_scan.check_current_lifecycle_doc_names(root)

        self.assertEqual([], failures)

    def test_missing_ci_docs_dependency_is_reported(self) -> None:
        failures = check_runtime_risk_scan.check_make_contracts(
            _make_contract_text(
                ci_docs_deps=("path-leak-check", "scripts-check", "lint-docs")
            )
        )

        self.assertIn("ci-docs: missing dependency 'risk-scan'", failures)

    def test_missing_python_runtime_resolver_token_is_reported(self) -> None:
        failures = check_runtime_risk_scan.check_make_contracts(_make_contract_text())

        self.assertIn(
            "Make surface: missing runtime token "
            '\'VENV="$(VENV)" . ./tools/python_runtime.sh; '
            "polinko_default_python_bin'",
            failures,
        )

    def test_missing_local_url_contract_token_is_reported(self) -> None:
        make_text = "\n".join(
            (
                _make_contract_text(),
                *check_runtime_risk_scan.REQUIRED_MAKE_RUNTIME_TOKENS,
                *check_runtime_risk_scan.REQUIRED_GITHUB_HEALTH_TOKENS,
                *(
                    token
                    for token in check_runtime_risk_scan.REQUIRED_LOCAL_URL_TOKENS
                    if token != "LOCAL_BROWSER_LAUNCH ?= none"
                ),
            )
        )

        failures = check_runtime_risk_scan.check_make_contracts(make_text)

        self.assertIn(
            "Make surface: missing local URL token 'LOCAL_BROWSER_LAUNCH ?= none'",
            failures,
        )

    def test_missing_github_health_contract_token_is_reported(self) -> None:
        omitted_token = '--pr-limit "$(GITHUB_HEALTH_PR_LIMIT)"'
        make_text = "\n".join(
            (
                _make_contract_text(),
                *check_runtime_risk_scan.REQUIRED_MAKE_RUNTIME_TOKENS,
                *check_runtime_risk_scan.REQUIRED_LOCAL_URL_TOKENS,
                *(
                    token
                    for token in check_runtime_risk_scan.REQUIRED_GITHUB_HEALTH_TOKENS
                    if token != omitted_token
                ),
            )
        )

        failures = check_runtime_risk_scan.check_make_contracts(make_text)

        self.assertIn(
            f"Make surface: missing GitHub health token {omitted_token!r}",
            failures,
        )

    def test_duplicate_eod_target_is_reported(self) -> None:
        failures = check_runtime_risk_scan.check_make_contracts(
            _make_contract_text(extra_lines=("eod:",))
        )

        self.assertIn(
            "make target 'eod': non-canonical target is active",
            failures,
        )

    def test_non_canonical_eod_stop_target_is_reported(self) -> None:
        failures = check_runtime_risk_scan.check_make_contracts(
            _make_contract_text(extra_lines=("eod-stop:",))
        )

        self.assertIn(
            "make target 'eod-stop': non-canonical target is active",
            failures,
        )

    def test_non_current_eval_shortcut_include_path_is_reported(self) -> None:
        failures = check_runtime_risk_scan.check_make_contracts(
            _make_contract_text(
                extra_lines=("include makefiles/evals/aliases/ocr-runs.mk",)
            )
        )

        self.assertIn(
            "Make surface: non-current include token "
            "'makefiles/evals/aliases' is active",
            failures,
        )

    def test_stale_handwriting_cases_flag_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tool_path = root / "tools" / "build_handwriting_benchmark_cases.py"
            tool_path.parent.mkdir(parents=True)
            tool_path.write_text('"--handwriting-cases"\n', encoding="utf-8")

            failures = check_runtime_risk_scan.check_non_current_tool_tokens(root)

        self.assertIn(
            "tools/build_handwriting_benchmark_cases.py: stale operator flag "
            "'--handwriting-cases' is active",
            failures,
        )

    def test_direct_command_probe_outside_shared_helpers_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tool_path = root / "tools" / "custom_wrapper.sh"
            tool_path.parent.mkdir(parents=True)
            tool_path.write_text("command -v gh >/dev/null 2>&1\n", encoding="utf-8")

            failures = check_runtime_risk_scan.check_direct_command_probes(root)

        self.assertEqual(
            failures,
            [
                "tools/custom_wrapper.sh:1: route command availability probe "
                "'command -v' through tools/shell_command_common.sh or "
                "tools/python_runtime.sh"
            ],
        )

    def test_command_probe_helpers_are_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tools_dir = root / "tools"
            tools_dir.mkdir()
            (tools_dir / "shell_command_common.sh").write_text(
                'command -v "$tool" >/dev/null 2>&1\n', encoding="utf-8"
            )
            (tools_dir / "python_runtime.sh").write_text(
                "command -v python3 >/dev/null 2>&1\n", encoding="utf-8"
            )

            failures = check_runtime_risk_scan.check_direct_command_probes(root)

        self.assertEqual([], failures)

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
                    "runtime-tool-reference-check",
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

    def test_missing_runtime_tool_reference_dependency_is_reported(self) -> None:
        failures = check_runtime_risk_scan.check_make_contracts(
            _make_contract_text(
                ci_docs_deps=(
                    "path-leak-check",
                    "scripts-check",
                    "local-runtime-config-check",
                    "risk-scan",
                    "operator-command-check",
                    "startup-contracts-check",
                    "lint-docs",
                )
            )
        )

        self.assertIn(
            "ci-docs: missing dependency 'runtime-tool-reference-check'",
            failures,
        )

    def test_missing_startup_contracts_dependency_is_reported(self) -> None:
        failures = check_runtime_risk_scan.check_make_contracts(
            _make_contract_text(
                ci_docs_deps=(
                    "path-leak-check",
                    "scripts-check",
                    "risk-scan",
                    "runtime-tool-reference-check",
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
            _make_contract_text(build_hygiene_core_deps=("transcript-check",))
        )

        self.assertIn(
            "build-hygiene-core: missing dependency 'doctor-env'",
            failures,
        )

        failures = check_runtime_risk_scan.check_make_contracts(
            _make_contract_text(build_hygiene_deps=("ci",))
        )

        self.assertIn(
            "build-hygiene: missing dependency 'build-hygiene-core'",
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

    def test_non_current_precommit_hook_token_is_reported(self) -> None:
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
            ".pre-commit-config.yaml: non-current hook token 'isort' is active",
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
