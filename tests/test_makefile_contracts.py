import os
import re
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MAKEFILE = REPO_ROOT / "Makefile"
MAKE_CONFIG = REPO_ROOT / "makefiles" / "config.mk"
MAKE_EVALS = REPO_ROOT / "makefiles" / "evals.mk"
OCR_WORKFLOW_SCRIPT = REPO_ROOT / "tools" / "run_ocr_workflow.sh"
EVAL_SERVER_DAEMON_SCRIPT = REPO_ROOT / "tools" / "ensure_eval_server_daemon.sh"
EVAL_CASE_GUARD_SCRIPT = REPO_ROOT / "tools" / "eval_case_guard.sh"
EVAL_REPORT_RUNNER_SCRIPT = REPO_ROOT / "tools" / "run_eval_report.sh"
LOCAL_EVAL_GATE_RUNNER_SCRIPT = REPO_ROOT / "tools" / "run_local_eval_gate.sh"
OCR_EVAL_RUNNER_SCRIPT = REPO_ROOT / "tools" / "run_eval_ocr_cases.sh"
OCR_STABILITY_RUNNER_SCRIPT = REPO_ROOT / "tools" / "run_eval_ocr_stability.sh"
OCR_GROWTH_EVAL_RUNNER_SCRIPT = REPO_ROOT / "tools" / "run_eval_ocr_growth_cases.sh"
OCR_GROWTH_BATCH_RUNNER_SCRIPT = REPO_ROOT / "tools" / "run_eval_ocr_growth_batched.sh"
OCR_GROWTH_STABILITY_RUNNER_SCRIPT = (
    REPO_ROOT / "tools" / "run_eval_ocr_growth_stability.sh"
)
OCR_REPORT_BUILDER_SCRIPT = REPO_ROOT / "tools" / "run_ocr_report_builder.sh"


def _makefile_text() -> str:
    return MAKEFILE.read_text(encoding="utf-8")


def _makefile_contract_text() -> str:
    root_text = _makefile_text()
    source_texts = [root_text]
    for match in re.finditer(r"^include\s+(.+)$", root_text, re.MULTILINE):
        for include_path in match.group(1).split():
            source_texts.append((REPO_ROOT / include_path).read_text(encoding="utf-8"))
    return "\n".join(source_texts)


def _phony_targets() -> list[str]:
    targets: list[str] = []
    for match in re.finditer(
        r"^\.PHONY:\s*(.*)$",
        _makefile_contract_text(),
        re.MULTILINE,
    ):
        targets.extend(match.group(1).split())
    return targets


class MakefileContractTests(unittest.TestCase):
    def test_default_goal_is_chat(self) -> None:
        self.assertRegex(_makefile_text(), r"(?m)^\.DEFAULT_GOAL\s*:=\s*chat$")

    def test_target_families_are_extracted_through_includes(self) -> None:
        self.assertRegex(_makefile_text(), r"(?m)^include\s+makefiles/build\.mk$")
        self.assertRegex(_makefile_text(), r"(?m)^include\s+makefiles/checks\.mk$")
        self.assertRegex(_makefile_text(), r"(?m)^include\s+makefiles/runtime\.mk$")
        self.assertRegex(_makefile_text(), r"(?m)^include\s+makefiles/surfaces\.mk$")
        self.assertRegex(_makefile_text(), r"(?m)^include\s+makefiles/evals\.mk$")
        self.assertRegex(_makefile_text(), r"(?m)^include\s+makefiles/ops\.mk$")

    def test_shared_config_is_extracted_before_target_families(self) -> None:
        root_text = _makefile_text()
        config_text = MAKE_CONFIG.read_text(encoding="utf-8")

        self.assertLess(
            root_text.index("include makefiles/config.mk"),
            root_text.index("include makefiles/build.mk"),
        )
        self.assertIsNone(re.search(r"(?m)^[A-Z][A-Z0-9_]*\s*(?:\?=|:=|=)", root_text))
        self.assertIn("PYTHON ?=", config_text)
        self.assertIn("CLI_ENTRYPOINT ?= main.py", config_text)
        self.assertIn("ASGI_APP ?= server:app", config_text)
        self.assertIn("PORTFOLIO_APP_DIR ?= apps/portfolio", config_text)
        self.assertIn("PORTFOLIO_APP_DIR ?= $(FRONTEND_DIR)", config_text)
        self.assertIn("FRONTEND_DIR ?= $(PORTFOLIO_APP_DIR)", config_text)
        self.assertIn("OCR_WORKFLOW_SCRIPT ?= ./tools/run_ocr_workflow.sh", config_text)
        self.assertIn(
            "EVAL_SERVER_DAEMON_SCRIPT ?= ./tools/ensure_eval_server_daemon.sh",
            config_text,
        )
        self.assertIn(
            "EVAL_CASE_GUARD_SCRIPT ?= ./tools/eval_case_guard.sh", config_text
        )
        self.assertIn(
            "EVAL_REPORT_RUNNER_SCRIPT ?= ./tools/run_eval_report.sh", config_text
        )
        self.assertIn("EVAL_REPORT_RUNNER_ENV =", config_text)
        self.assertIn(
            "LOCAL_EVAL_GATE_RUNNER_SCRIPT ?= ./tools/run_local_eval_gate.sh",
            config_text,
        )
        self.assertIn("LOCAL_EVAL_GATE_RUNNER_ENV =", config_text)
        self.assertIn(
            "OCR_EVAL_RUNNER_SCRIPT ?= ./tools/run_eval_ocr_cases.sh", config_text
        )
        self.assertIn("OCR_EVAL_RUNNER_ENV =", config_text)
        self.assertIn(
            "OCR_STABILITY_RUNNER_SCRIPT ?= ./tools/run_eval_ocr_stability.sh",
            config_text,
        )
        self.assertIn("OCR_STABILITY_RUNNER_ENV =", config_text)
        self.assertIn(
            "OCR_GROWTH_EVAL_RUNNER_SCRIPT ?= ./tools/run_eval_ocr_growth_cases.sh",
            config_text,
        )
        self.assertIn(
            "OCR_GROWTH_BATCH_RUNNER_SCRIPT ?= ./tools/run_eval_ocr_growth_batched.sh",
            config_text,
        )
        self.assertIn(
            "OCR_GROWTH_STABILITY_RUNNER_SCRIPT ?= ./tools/run_eval_ocr_growth_stability.sh",
            config_text,
        )
        self.assertIn("OCR_GROWTH_RUNNER_ENV =", config_text)
        self.assertIn(
            "OCR_REPORT_BUILDER_SCRIPT ?= ./tools/run_ocr_report_builder.sh",
            config_text,
        )
        self.assertIn("OCR_REPORT_BUILDER_ENV =", config_text)

    def test_no_argument_make_still_launches_chat_entrypoint(self) -> None:
        result = subprocess.run(
            ["make", "-n"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        lines = result.stdout.splitlines()
        self.assertTrue(lines)
        self.assertTrue(any("main.py" in line for line in lines), lines)

    def test_phony_targets_are_unique(self) -> None:
        targets = _phony_targets()

        self.assertEqual(sorted(targets), sorted(set(targets)))

    def test_chat_and_manual_eval_entrypoints_stay_phony(self) -> None:
        targets = set(_phony_targets())

        self.assertIn("ci", targets)
        self.assertIn("chat", targets)
        self.assertIn("server-daemon", targets)
        self.assertIn("caffeinate", targets)
        self.assertIn("manual-evals-db", targets)
        self.assertIn("manualdb", targets)
        self.assertIn("portfolio", targets)
        self.assertIn("portfolio-mockups", targets)
        self.assertIn("pwcli", targets)

    def test_lifecycle_aliases_delegate_to_canonical_targets(self) -> None:
        text = _makefile_contract_text()

        self.assertRegex(text, r"(?m)^eod end-preflight:\s*end$")
        self.assertRegex(
            text,
            r"(?m)^eod-stop:\s*server-daemon-stop caffeinate-off-all session-status$",
        )
        self.assertRegex(text, r"(?m)^caffeinate-on:\s*caffeinate$")
        self.assertRegex(text, r"(?m)^caffeinate-off:\s*decaffeinate$")
        self.assertRegex(text, r"(?m)^caffeinate-off-all:\s*caffeinate-off$")
        self.assertRegex(text, r"(?m)^decaffeinate-status:\s*caffeinate-status$")

    def test_operator_wrappers_use_dependency_edges_for_internal_chains(self) -> None:
        text = _makefile_contract_text()

        self.assertRegex(
            text,
            r"(?m)^backend-gate:\s*backend-gate-start doctor-env test quality-gate-deterministic$",
        )
        self.assertRegex(text, r"(?m)^docs:\s*open-api-docs$")
        self.assertRegex(text, r"(?m)^open-api-docs:\s*server-daemon$")
        self.assertRegex(
            text, r"(?m)^open-cost-console:\s*open-limits open-usage open-billing$"
        )
        self.assertRegex(text, r"(?m)^viz:\s*server-daemon$")
        self.assertRegex(
            text, r"(?m)^portfolio:\s*portfolio-build server-daemon-stop server-daemon$"
        )
        self.assertRegex(
            text, r"(?m)^portfolio-playwright:\s*PORTFOLIO_LAUNCH\s*=\s*playwright$"
        )
        self.assertRegex(text, r"(?m)^portfolio-playwright:\s*portfolio$")
        self.assertRegex(
            text,
            r"(?m)^eval-reports:\s*eval-retrieval-report eval-file-search-report eval-ocr-report eval-style-report eval-response-behaviour-report eval-ocr-safety-report eval-hallucination-report$",
        )
        self.assertRegex(
            text,
            r"(?m)^quality-gate-deterministic:\s*HALLUCINATION_EVAL_MODE\s*=\s*deterministic$",
        )
        self.assertRegex(text, r"(?m)^quality-gate-deterministic:\s*quality-gate$")
        self.assertRegex(
            text,
            r"(?m)^ocr-cases-from-export:\s*ocr-cases-from-export-build ocr-handwriting-benchmark-cases ocr-typed-benchmark-cases ocr-illustration-benchmark-cases ocr-transcript-delta$",
        )
        self.assertRegex(
            text,
            r"(?m)^ocrminehand:\s*OCR_CASES_FROM_EXPORT_ARGS\s*=\s*--include-lanes handwriting$",
        )
        self.assertRegex(text, r"(?m)^ocrminehand:\s*ocr-cases-from-export$")

    def test_eval_workflow_orchestration_delegates_to_scripts(self) -> None:
        text = MAKE_EVALS.read_text(encoding="utf-8")
        guard_text = EVAL_CASE_GUARD_SCRIPT.read_text(encoding="utf-8")

        self.assertNotIn("$(MAKE)", text)
        self.assertNotIn("import json,pathlib", text)
        self.assertNotIn("CASE_COUNT=", text)
        self.assertIn("tools.count_eval_cases", guard_text)
        for suite in (
            "retrieval",
            "file-search",
            "hallucination",
            "style",
            "response-behaviour",
            "ocr-safety",
            "ocr",
            "ocr-recovery",
            "clip-ab",
        ):
            self.assertIn(
                f'bash "$(EVAL_REPORT_RUNNER_SCRIPT)" {suite}',
                text,
            )
        self.assertIn('eval_case_guard_or_exit "$(OCR_TRANSCRIPT_CASES_GROWTH)"', text)
        self.assertIn('eval_case_guard_or_exit "$(OCR_FOCUS_CASES_JSON)"', text)
        self.assertIn(
            'bash "$(OCR_EVAL_RUNNER_SCRIPT)" "$(OCR_TRANSCRIPT_CASES)"', text
        )
        self.assertIn(
            'bash "$(OCR_EVAL_RUNNER_SCRIPT)" "$(OCR_TRANSCRIPT_CASES_HANDWRITING)"',
            text,
        )
        self.assertIn(
            'bash "$(OCR_STABILITY_RUNNER_SCRIPT)" "$(OCR_TRANSCRIPT_CASES)"',
            text,
        )
        self.assertIn(
            'bash "$(OCR_STABILITY_RUNNER_SCRIPT)" "$(OCR_FOCUS_CASES_JSON)"',
            text,
        )
        self.assertIn(
            'bash "$(OCR_STABILITY_RUNNER_SCRIPT)" "$(OCR_TRANSCRIPT_CASES_HANDWRITING_BENCHMARK)"',
            text,
        )
        self.assertIn(
            'bash "$(OCR_GROWTH_EVAL_RUNNER_SCRIPT)" "$(OCR_TRANSCRIPT_CASES_GROWTH)"',
            text,
        )
        self.assertIn(
            'bash "$(OCR_GROWTH_BATCH_RUNNER_SCRIPT)" "$(OCR_TRANSCRIPT_CASES_GROWTH)"',
            text,
        )
        self.assertIn(
            'bash "$(OCR_GROWTH_STABILITY_RUNNER_SCRIPT)" "$(OCR_TRANSCRIPT_CASES_GROWTH)"',
            text,
        )
        for suite in (
            "api-smoke",
            "eval-smoke",
            "hallucination-gate",
            "quality-gate",
        ):
            self.assertIn(
                f'bash "$(LOCAL_EVAL_GATE_RUNNER_SCRIPT)" {suite}',
                text,
            )
        for suite in (
            "growth-metrics",
            "growth-fail-cohort",
            "focus-cases",
            "focus-fail-patterns",
        ):
            self.assertIn(
                f'bash "$(OCR_REPORT_BUILDER_SCRIPT)" {suite}',
                text,
            )
        self.assertNotIn(
            '$(PYTHON) -m tools.eval_ocr --timeout "$(OCR_EVAL_TIMEOUT)" --cases "$(OCR_TRANSCRIPT_CASES_HANDWRITING)" --strict',
            text,
        )
        self.assertNotIn(
            'PYTHONUNBUFFERED=1 $(PYTHON) -m tools.eval_ocr --timeout "$(OCR_EVAL_TIMEOUT)" --cases "$(OCR_TRANSCRIPT_CASES_GROWTH)"',
            text,
        )
        self.assertNotIn("$(PYTHON) -m tools.eval_ocr_batched", text)
        self.assertNotIn(
            '$(PYTHON) -m tools.eval_ocr_stability \\\n\t\t\t\t--base-url "http://127.0.0.1:8000" \\\n\t\t\t\t--cases "$(OCR_TRANSCRIPT_CASES_HANDWRITING_BENCHMARK)"',
            text,
        )
        self.assertNotIn("eval_reports/retrieval-$$RUN_ID.json", text)
        self.assertNotIn("eval_reports/file-search-$$RUN_ID.json", text)
        self.assertNotIn("eval_reports/hallucination-$$RUN_ID.json", text)
        self.assertNotIn("eval_reports/style-$$RUN_ID.json", text)
        self.assertNotIn("eval_reports/response-behaviour-$$RUN_ID.json", text)
        self.assertNotIn("eval_reports/ocr-safety-$$RUN_ID.json", text)
        self.assertNotIn("eval_reports/ocr-$$RUN_ID.json", text)
        self.assertNotIn("eval_reports/ocr-recovery-$$RUN_ID.json", text)
        self.assertNotIn("eval_reports/clip-ab-$$RUN_ID.json", text)
        self.assertNotIn("$(PYTHON) -m tools.eval_ocr_growth_metrics", text)
        self.assertNotIn("$(PYTHON) -m tools.build_ocr_growth_fail_cohort", text)
        self.assertNotIn("$(PYTHON) -m tools.build_ocr_focus_cases", text)
        self.assertNotIn("$(PYTHON) -m tools.report_ocr_focus_fail_patterns", text)
        self.assertNotIn("FAIL_COHORT_ARGS=", text)
        self.assertNotIn("FOCUS_ARGS=", text)
        evals_text = MAKE_EVALS.read_text(encoding="utf-8")
        self.assertNotIn("$(PYTHON) -m uvicorn $(ASGI_APP)", evals_text)
        self.assertNotIn('curl -fsS "$$BASE_URL/health"', evals_text)
        self.assertNotIn("SERVER_PID=$$!", evals_text)
        self.assertRegex(
            text,
            r"(?m)^ocrkernel:\n\t@CGPT_EXPORT_ROOT=\"\$\(CGPT_EXPORT_ROOT\)\" \\\n\t\tCGPT_EXPORT_ROOT_DEFAULT=\"\$\(CGPT_EXPORT_ROOT_DEFAULT\)\" \\\n\t\tbash \"\$\(OCR_WORKFLOW_SCRIPT\)\" ocrkernel$",
        )
        self.assertRegex(
            text,
            r"(?m)^ocr-data:\n\t@CGPT_EXPORT_ROOT=\"\$\(CGPT_EXPORT_ROOT\)\" \\\n\t\tCGPT_EXPORT_ROOT_DEFAULT=\"\$\(CGPT_EXPORT_ROOT_DEFAULT\)\" \\\n\t\tbash \"\$\(OCR_WORKFLOW_SCRIPT\)\" ocr-data$",
        )
        self.assertRegex(
            text,
            r"(?m)^ocr-notebook-workflow:\n\t@CGPT_EXPORT_ROOT=\"\$\(CGPT_EXPORT_ROOT\)\" \\\n\t\tbash \"\$\(OCR_WORKFLOW_SCRIPT\)\" ocr-notebook-workflow$",
        )
        self.assertNotIn('bash "$(EVAL_SERVER_DAEMON_SCRIPT)"', text)

    def test_eval_helper_scripts_are_named_for_their_roles(self) -> None:
        self.assertTrue(OCR_WORKFLOW_SCRIPT.is_file())
        self.assertTrue(EVAL_SERVER_DAEMON_SCRIPT.is_file())
        self.assertTrue(EVAL_CASE_GUARD_SCRIPT.is_file())
        self.assertTrue(EVAL_REPORT_RUNNER_SCRIPT.is_file())
        self.assertTrue(LOCAL_EVAL_GATE_RUNNER_SCRIPT.is_file())
        self.assertTrue(OCR_EVAL_RUNNER_SCRIPT.is_file())
        self.assertTrue(OCR_STABILITY_RUNNER_SCRIPT.is_file())
        self.assertTrue(OCR_GROWTH_EVAL_RUNNER_SCRIPT.is_file())
        self.assertTrue(OCR_GROWTH_BATCH_RUNNER_SCRIPT.is_file())
        self.assertTrue(OCR_GROWTH_STABILITY_RUNNER_SCRIPT.is_file())
        self.assertTrue(OCR_REPORT_BUILDER_SCRIPT.is_file())
        self.assertTrue(os.access(OCR_WORKFLOW_SCRIPT, os.X_OK))
        self.assertTrue(os.access(EVAL_SERVER_DAEMON_SCRIPT, os.X_OK))
        self.assertTrue(os.access(EVAL_CASE_GUARD_SCRIPT, os.X_OK))
        self.assertTrue(os.access(EVAL_REPORT_RUNNER_SCRIPT, os.X_OK))
        self.assertTrue(os.access(LOCAL_EVAL_GATE_RUNNER_SCRIPT, os.X_OK))
        self.assertTrue(os.access(OCR_EVAL_RUNNER_SCRIPT, os.X_OK))
        self.assertTrue(os.access(OCR_STABILITY_RUNNER_SCRIPT, os.X_OK))
        self.assertTrue(os.access(OCR_GROWTH_EVAL_RUNNER_SCRIPT, os.X_OK))
        self.assertTrue(os.access(OCR_GROWTH_BATCH_RUNNER_SCRIPT, os.X_OK))
        self.assertTrue(os.access(OCR_GROWTH_STABILITY_RUNNER_SCRIPT, os.X_OK))
        self.assertTrue(os.access(OCR_REPORT_BUILDER_SCRIPT, os.X_OK))
        for script in (
            OCR_EVAL_RUNNER_SCRIPT,
            OCR_STABILITY_RUNNER_SCRIPT,
            OCR_GROWTH_EVAL_RUNNER_SCRIPT,
            OCR_GROWTH_BATCH_RUNNER_SCRIPT,
            OCR_GROWTH_STABILITY_RUNNER_SCRIPT,
        ):
            script_text = script.read_text(encoding="utf-8")
            self.assertIn("EVAL_SERVER_DAEMON_SCRIPT", script_text)
            self.assertIn('bash "$server_daemon_script"', script_text)
        self.assertFalse((REPO_ROOT / "tools" / "ocr_workflow.sh").exists())
        self.assertFalse((REPO_ROOT / "tools" / "ensure_server_daemon.sh").exists())

    def test_frontend_surface_names_are_aliases_for_portfolio_targets(self) -> None:
        text = _makefile_contract_text()

        self.assertRegex(
            text, r"(?m)^portfolio-app-install frontend-install:\s*portfolio-install$"
        )
        self.assertRegex(text, r"(?m)^frontend-build:\s*portfolio-build$")

    def test_portfolio_app_dir_is_canonical_but_legacy_frontend_override_still_works(
        self,
    ) -> None:
        legacy_result = subprocess.run(
            ["make", "-n", "portfolio-build", "FRONTEND_DIR=legacy-app"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        canonical_result = subprocess.run(
            [
                "make",
                "-n",
                "portfolio-build",
                "FRONTEND_DIR=legacy-app",
                "PORTFOLIO_APP_DIR=canonical-app",
            ],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("legacy-app/package.json", legacy_result.stdout)
        self.assertIn('npm --prefix "legacy-app"', legacy_result.stdout)
        self.assertIn("canonical-app/package.json", canonical_result.stdout)
        self.assertIn('npm --prefix "canonical-app"', canonical_result.stdout)
        self.assertNotIn("legacy-app/package.json", canonical_result.stdout)

    def test_portfolio_build_dry_run_does_not_execute_vite_build(self) -> None:
        result = subprocess.run(
            ["make", "-n", "portfolio-build"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn('npm --prefix "apps/portfolio" run build', result.stdout)
        self.assertNotIn("vite v", result.stdout + result.stderr)
        self.assertNotIn("built in", result.stdout + result.stderr)

    def test_operator_wrapper_dry_runs_resolve_without_recursive_variable_errors(
        self,
    ) -> None:
        for target in (
            "portfolio",
            "portfolio-playwright",
            "open-api-docs",
            "viz",
            "caffeinate-off-all",
            "eod-stop",
            "backend-gate",
            "ocrminehand",
            "ocrkernel",
            "ocr-data",
            "ocr-notebook-workflow",
            "eval-ocr-transcript-cases",
            "eval-ocr-transcript-stability",
            "eval-ocr-focus-stability",
        ):
            with self.subTest(target=target):
                result = subprocess.run(
                    ["make", "-n", target],
                    cwd=REPO_ROOT,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                combined_output = result.stdout + result.stderr

                self.assertNotIn("Recursive variable", combined_output)
                self.assertNotIn("vite v", combined_output)
                self.assertNotIn("built in", combined_output)

    def test_ocr_workflow_script_preserves_export_root_guard(self) -> None:
        env = os.environ.copy()
        env["CGPT_EXPORT_ROOT"] = ""
        env["CGPT_EXPORT_ROOT_DEFAULT"] = ""

        result = subprocess.run(
            ["bash", str(OCR_WORKFLOW_SCRIPT.relative_to(REPO_ROOT)), "ocr-data"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            env=env,
            text=True,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("CGPT_EXPORT_ROOT is required.", result.stdout)
        self.assertIn(
            "make ocr-data CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT",
            result.stdout,
        )

    def test_eval_entrypoints_stay_phony(self) -> None:
        targets = set(_phony_targets())

        self.assertIn("api-smoke", targets)
        self.assertIn("eval-smoke", targets)
        self.assertIn("quality-gate", targets)
        self.assertIn("quality-gate-deterministic", targets)
        self.assertIn("ocrmine", targets)
        self.assertIn("ocrkernel", targets)
        self.assertIn("eval-sidecar-start", targets)
        self.assertIn("eval-ocr-transcript-cases-growth-batched", targets)

    def test_external_check_entrypoints_stay_phony(self) -> None:
        targets = set(_phony_targets())

        self.assertIn("k6-chat-smoke", targets)
        self.assertIn("trivy-fs", targets)
        self.assertIn("trivy-image", targets)
        self.assertIn("docker-build", targets)
        self.assertIn("docker-run", targets)


if __name__ == "__main__":
    unittest.main()
