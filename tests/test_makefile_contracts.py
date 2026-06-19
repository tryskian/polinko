import os
import re
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MAKEFILE = REPO_ROOT / "Makefile"
MAKE_CONFIG = REPO_ROOT / "makefiles" / "config.mk"
MAKE_EVALS = REPO_ROOT / "makefiles" / "evals.mk"
OCR_WORKFLOW_SCRIPT = REPO_ROOT / "tools" / "run_ocr_workflow.sh"
CAFFEINATE_SCRIPT = REPO_ROOT / "tools" / "manage_caffeinate.sh"
OPENAI_ACCOUNT_SCRIPT = REPO_ROOT / "tools" / "openai_account_summary.py"
SERVER_DAEMON_SCRIPT = REPO_ROOT / "tools" / "run_server_daemon.sh"
EVAL_SERVER_DAEMON_SCRIPT = REPO_ROOT / "tools" / "ensure_eval_server_daemon.sh"
EVAL_CASE_GUARD_SCRIPT = REPO_ROOT / "tools" / "eval_case_guard.sh"
OCR_WORKFLOW_COMMON_SCRIPT = REPO_ROOT / "tools" / "ocr_workflow_common.sh"
OCR_GUARDED_CASE_RUNNER_SCRIPT = REPO_ROOT / "tools" / "run_guarded_ocr_case_eval.sh"
OCR_BASE_TRANSCRIPT_WORKFLOW_SCRIPT = (
    REPO_ROOT / "tools" / "run_ocr_base_transcript_workflow.sh"
)
OCR_TRANSCRIPT_LANE_WORKFLOW_SCRIPT = (
    REPO_ROOT / "tools" / "run_ocr_transcript_lane_workflow.sh"
)
OCR_FOCUS_STABILITY_WORKFLOW_SCRIPT = (
    REPO_ROOT / "tools" / "run_ocr_focus_stability_workflow.sh"
)
OCR_GROWTH_STABILITY_WORKFLOW_SCRIPT = (
    REPO_ROOT / "tools" / "run_ocr_growth_stability_workflow.sh"
)
EVAL_REPORT_RUNNER_SCRIPT = REPO_ROOT / "tools" / "run_eval_report.sh"
EVAL_REPORTS_PARALLEL_RUNNER_SCRIPT = (
    REPO_ROOT / "tools" / "run_eval_reports_parallel.sh"
)
EVAL_SIDECAR_START_SCRIPT = REPO_ROOT / "tools" / "run_eval_sidecar_start.sh"
LOCAL_EVAL_GATE_RUNNER_SCRIPT = REPO_ROOT / "tools" / "run_local_eval_gate.sh"
OCR_EVAL_RUNNER_SCRIPT = REPO_ROOT / "tools" / "run_eval_ocr_cases.sh"
OCR_HANDWRITING_EVAL_RUNNER_SCRIPT = REPO_ROOT / "tools" / "run_eval_ocr_handwriting.sh"
OCR_STABILITY_RUNNER_SCRIPT = REPO_ROOT / "tools" / "run_eval_ocr_stability.sh"
OCR_GROWTH_EVAL_RUNNER_SCRIPT = REPO_ROOT / "tools" / "run_eval_ocr_growth_cases.sh"
OCR_GROWTH_BATCH_RUNNER_SCRIPT = REPO_ROOT / "tools" / "run_eval_ocr_growth_batched.sh"
OCR_GROWTH_CASE_WORKFLOW_SCRIPT = (
    REPO_ROOT / "tools" / "run_ocr_growth_case_workflow.sh"
)
OCR_GROWTH_STABILITY_RUNNER_SCRIPT = (
    REPO_ROOT / "tools" / "run_eval_ocr_growth_stability.sh"
)
OCR_REPORT_BUILDER_SCRIPT = REPO_ROOT / "tools" / "run_ocr_report_builder.sh"
OCR_REPORT_WORKFLOW_SCRIPT = REPO_ROOT / "tools" / "run_ocr_report_workflow.sh"
OCR_LANE_INVENTORY_SCRIPT = REPO_ROOT / "tools" / "report_ocr_lane_inventory.py"
OCR_INTAKE_WORKFLOW_SCRIPT = REPO_ROOT / "tools" / "run_ocr_intake_workflow.sh"
SHELL_SCRIPT_CONTRACT_SCRIPT = REPO_ROOT / "tools" / "check_shell_scripts.py"


def _makefile_text() -> str:
    return MAKEFILE.read_text(encoding="utf-8")


def _makefile_source_text(path: Path, seen: set[Path] | None = None) -> str:
    if seen is None:
        seen = set()
    resolved_path = path.resolve()
    if resolved_path in seen:
        return ""
    seen.add(resolved_path)

    text = path.read_text(encoding="utf-8")
    source_texts = [text]
    for match in re.finditer(r"^include\s+(.+)$", text, re.MULTILINE):
        for include_path in match.group(1).split():
            source_texts.append(_makefile_source_text(REPO_ROOT / include_path, seen))
    return "\n".join(source_texts)


def _makefile_contract_text() -> str:
    return _makefile_source_text(MAKEFILE)


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

    def test_eval_targets_are_extracted_through_role_includes(self) -> None:
        evals_entry_text = MAKE_EVALS.read_text(encoding="utf-8")

        self.assertIn("include makefiles/evals/aliases.mk", evals_entry_text)
        self.assertIn("include makefiles/evals/core.mk", evals_entry_text)
        self.assertIn("include makefiles/evals/gates.mk", evals_entry_text)
        self.assertIn("include makefiles/evals/ocr-intake.mk", evals_entry_text)
        self.assertIn("include makefiles/evals/ocr-runs.mk", evals_entry_text)
        self.assertIn("ocrkernel:", _makefile_contract_text())
        self.assertIn(
            "eval-ocr-transcript-stability-growth:", _makefile_contract_text()
        )

    def test_shared_config_is_extracted_before_target_families(self) -> None:
        root_text = _makefile_text()
        config_entry_text = MAKE_CONFIG.read_text(encoding="utf-8")
        config_text = _makefile_contract_text()

        self.assertLess(
            root_text.index("include makefiles/config.mk"),
            root_text.index("include makefiles/build.mk"),
        )
        self.assertIsNone(re.search(r"(?m)^[A-Z][A-Z0-9_]*\s*(?:\?=|:=|=)", root_text))
        self.assertIsNone(
            re.search(r"(?m)^[A-Z][A-Z0-9_]*\s*(?:\?=|:=|=)", config_entry_text)
        )
        self.assertIn("include makefiles/config/base.mk", config_entry_text)
        self.assertIn("include makefiles/config/runtime.mk", config_entry_text)
        self.assertIn("include makefiles/config/surfaces.mk", config_entry_text)
        self.assertIn("include makefiles/config/evals.mk", config_entry_text)
        self.assertIn("include makefiles/config/ops.mk", config_entry_text)
        self.assertIn("include makefiles/config/build.mk", config_entry_text)
        self.assertIn("PYTHON ?=", config_text)
        self.assertIn("CLI_ENTRYPOINT ?= -m polinko.cli", config_text)
        self.assertIn("ASGI_APP ?= server:app", config_text)
        self.assertIn("LOCAL_BROWSER_LAUNCH ?= none", config_text)
        self.assertIn(
            "OPENAI_ACCOUNT_SCRIPT ?= ./tools/openai_account_summary.py", config_text
        )
        self.assertIn("OPENAI_ACCOUNT_ENV =", config_text)
        self.assertIn("CAFFEINATE_SCRIPT ?= ./tools/manage_caffeinate.sh", config_text)
        self.assertIn("CAFFEINATE_LAUNCHER_PYTHON ?= $(PYTHON)", config_text)
        self.assertIn("CAFFEINATE_ENV =", config_text)
        self.assertIn(
            "SERVER_DAEMON_SCRIPT ?= ./tools/run_server_daemon.sh", config_text
        )
        self.assertIn("SERVER_LAUNCHER_PYTHON ?= $(PYTHON)", config_text)
        self.assertIn("SERVER_DAEMON_ENV =", config_text)
        self.assertIn("PORTFOLIO_APP_DIR ?= apps/portfolio", config_text)
        self.assertIn("PORTFOLIO_APP_DIR ?= $(FRONTEND_DIR)", config_text)
        self.assertIn("FRONTEND_DIR ?= $(PORTFOLIO_APP_DIR)", config_text)
        self.assertIn("PIP_AUDIT_IGNORED_VULNS ?= PYSEC-2025-183", config_text)
        self.assertIn(
            "PIP_AUDIT_ARGS = $(foreach vuln,$(PIP_AUDIT_IGNORED_VULNS),--ignore-vuln $(vuln))",
            config_text,
        )
        self.assertIn("OCR_WORKFLOW_SCRIPT ?= ./tools/run_ocr_workflow.sh", config_text)
        self.assertIn(
            "OCR_INTAKE_WORKFLOW_SCRIPT ?= ./tools/run_ocr_intake_workflow.sh",
            config_text,
        )
        self.assertIn("OCR_INTAKE_WORKFLOW_ENV =", config_text)
        self.assertIn(
            "EVAL_SERVER_DAEMON_SCRIPT ?= ./tools/ensure_eval_server_daemon.sh",
            config_text,
        )
        self.assertIn(
            "EVAL_CASE_GUARD_SCRIPT ?= ./tools/eval_case_guard.sh", config_text
        )
        self.assertIn(
            "OCR_GUARDED_CASE_RUNNER_SCRIPT ?= ./tools/run_guarded_ocr_case_eval.sh",
            config_text,
        )
        self.assertIn("OCR_GUARDED_CASE_RUNNER_ENV =", config_text)
        self.assertIn(
            "OCR_BASE_TRANSCRIPT_WORKFLOW_SCRIPT ?= ./tools/run_ocr_base_transcript_workflow.sh",
            config_text,
        )
        self.assertIn("OCR_BASE_TRANSCRIPT_WORKFLOW_ENV =", config_text)
        self.assertIn(
            "OCR_TRANSCRIPT_LANE_WORKFLOW_SCRIPT ?= ./tools/run_ocr_transcript_lane_workflow.sh",
            config_text,
        )
        self.assertIn("OCR_TRANSCRIPT_LANE_WORKFLOW_ENV =", config_text)
        self.assertIn(
            "OCR_FOCUS_STABILITY_WORKFLOW_SCRIPT ?= ./tools/run_ocr_focus_stability_workflow.sh",
            config_text,
        )
        self.assertIn("OCR_FOCUS_STABILITY_WORKFLOW_ENV =", config_text)
        self.assertIn(
            "OCR_GROWTH_STABILITY_WORKFLOW_SCRIPT ?= ./tools/run_ocr_growth_stability_workflow.sh",
            config_text,
        )
        self.assertIn("OCR_GROWTH_STABILITY_WORKFLOW_ENV =", config_text)
        self.assertIn(
            "EVAL_REPORT_RUNNER_SCRIPT ?= ./tools/run_eval_report.sh", config_text
        )
        self.assertIn("EVAL_REPORT_RUNNER_ENV =", config_text)
        self.assertIn(
            "EVAL_REPORTS_PARALLEL_RUNNER_SCRIPT ?= ./tools/run_eval_reports_parallel.sh",
            config_text,
        )
        self.assertIn("EVAL_REPORTS_PARALLEL_RUNNER_ENV =", config_text)
        self.assertIn(
            "EVAL_SIDECAR_START_SCRIPT ?= ./tools/run_eval_sidecar_start.sh",
            config_text,
        )
        self.assertIn("EVAL_SIDECAR_LAUNCHER_PYTHON ?= $(PYTHON)", config_text)
        self.assertIn("EVAL_SIDECAR_START_ENV =", config_text)
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
            "OCR_HANDWRITING_EVAL_RUNNER_SCRIPT ?= ./tools/run_eval_ocr_handwriting.sh",
            config_text,
        )
        self.assertIn("OCR_HANDWRITING_EVAL_RUNNER_ENV =", config_text)
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
        self.assertIn(
            "OCR_GROWTH_CASE_WORKFLOW_SCRIPT ?= ./tools/run_ocr_growth_case_workflow.sh",
            config_text,
        )
        self.assertIn("OCR_GROWTH_CASE_WORKFLOW_ENV =", config_text)
        self.assertIn(
            "OCR_REPORT_BUILDER_SCRIPT ?= ./tools/run_ocr_report_builder.sh",
            config_text,
        )
        self.assertIn("OCR_REPORT_BUILDER_ENV =", config_text)
        self.assertIn(
            "OCR_REPORT_WORKFLOW_SCRIPT ?= ./tools/run_ocr_report_workflow.sh",
            config_text,
        )
        self.assertIn("OCR_REPORT_WORKFLOW_ENV =", config_text)
        self.assertIn(
            "OCR_LANE_INVENTORY_SCRIPT ?= ./tools/report_ocr_lane_inventory.py",
            config_text,
        )
        self.assertIn("OCR_LANE_INVENTORY_ARGS ?= $(ARGS)", config_text)
        self.assertIn(
            "OCR_LANE_INVENTORY_FRESHNESS_DAYS ?= $(FRESHNESS_DAYS)",
            config_text,
        )

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
        self.assertTrue(any("-m polinko.cli" in line for line in lines), lines)

    def test_phony_targets_are_unique(self) -> None:
        targets = _phony_targets()

        self.assertEqual(sorted(targets), sorted(set(targets)))

    def test_chat_and_manual_eval_entrypoints_stay_phony(self) -> None:
        targets = set(_phony_targets())

        self.assertIn("ci", targets)
        self.assertIn("ci-package", targets)
        self.assertIn("ci-python-style", targets)
        self.assertIn("package-install-check", targets)
        self.assertIn("chat", targets)
        self.assertIn("server-daemon", targets)
        self.assertIn("caffeinate", targets)
        self.assertIn("openai-account-summary", targets)
        self.assertIn("openai-costs", targets)
        self.assertIn("openai-usage", targets)
        self.assertIn("openai-limits", targets)
        self.assertIn("manual-evals-db", targets)
        self.assertIn("manualdb", targets)
        self.assertIn("manual-evals-db-refresh", targets)
        self.assertIn("manualdb-refresh", targets)
        self.assertIn("manual-evals-db-status", targets)
        self.assertIn("manualdb-status", targets)
        self.assertIn("manual-evals-db-health", targets)
        self.assertIn("manualdb-health", targets)
        self.assertIn("manual-evals-feedback-actionables", targets)
        self.assertIn("manualdb-feedback-actionables", targets)
        self.assertIn("manual-evals-feedback-cohorts", targets)
        self.assertIn("manualdb-feedback-cohorts", targets)
        self.assertIn("manual-evals-feedback-source-context", targets)
        self.assertIn("manualdb-feedback-source-context", targets)
        self.assertIn("manual-evals-feedback-decision-draft", targets)
        self.assertIn("manualdb-feedback-decision-draft", targets)
        self.assertIn("manual-evals-feedback-decision-preview", targets)
        self.assertIn("manualdb-feedback-decision-preview", targets)
        self.assertIn("manual-evals-overlay-comparison-readiness", targets)
        self.assertIn("manualdb-overlay-comparison-readiness", targets)
        self.assertIn("manual-evals-ocr-retry-candidates", targets)
        self.assertIn("manualdb-ocr-retry-candidates", targets)
        self.assertIn("manual-evals-ocr-retry-source-verification", targets)
        self.assertIn("manualdb-ocr-retry-source-verification", targets)
        self.assertIn("manual-evals-ocr-retry-source-provenance", targets)
        self.assertIn("manualdb-ocr-retry-source-provenance", targets)
        self.assertIn("manual-evals-ocr-retry-input-packet", targets)
        self.assertIn("manualdb-ocr-retry-input-packet", targets)
        self.assertIn("manual-evals-ocr-retry-rerun-manifest", targets)
        self.assertIn("manualdb-ocr-retry-rerun-manifest", targets)
        self.assertIn("manual-evals-ocr-retry-rerun-plan", targets)
        self.assertIn("manualdb-ocr-retry-rerun-plan", targets)
        self.assertIn("manual-evals-ocr-retry-selection-review", targets)
        self.assertIn("manualdb-ocr-retry-selection-review", targets)
        self.assertIn("manual-evals-ocr-retry-selection-template", targets)
        self.assertIn("manualdb-ocr-retry-selection-template", targets)
        self.assertIn("manual-evals-ocr-retry-selection-validate", targets)
        self.assertIn("manualdb-ocr-retry-selection-validate", targets)
        self.assertIn("manual-evals-ocr-retry-selection-apply-preview", targets)
        self.assertIn("manualdb-ocr-retry-selection-apply-preview", targets)
        self.assertIn("manual-evals-ocr-retry-execution-readiness", targets)
        self.assertIn("manualdb-ocr-retry-execution-readiness", targets)
        self.assertIn("manual-evals-ocr-retry-execute", targets)
        self.assertIn("manualdb-ocr-retry-execute", targets)
        self.assertIn("manual-evals-ocr-retry-execution-report", targets)
        self.assertIn("manualdb-ocr-retry-execution-report", targets)
        self.assertIn("manual-evals-ocr-retry-feedback-closure-preview", targets)
        self.assertIn("manualdb-ocr-retry-feedback-closure-preview", targets)
        self.assertIn("manual-evals-no-context-reclassify-preview", targets)
        self.assertIn("manualdb-no-context-reclassify-preview", targets)
        self.assertIn("manual-evals-no-context-reclassify-apply", targets)
        self.assertIn("manualdb-no-context-reclassify-apply", targets)
        self.assertIn("manual-evals-feedback-reclassify-preview", targets)
        self.assertIn("manualdb-feedback-reclassify-preview", targets)
        self.assertIn("manual-evals-feedback-reclassify-apply", targets)
        self.assertIn("manualdb-feedback-reclassify-apply", targets)
        self.assertIn("portfolio", targets)
        self.assertIn("portfolio-mockups", targets)
        self.assertIn("pwcli", targets)

    def test_manual_eval_db_targets_are_terminal_native_and_backup_first(
        self,
    ) -> None:
        text = _makefile_contract_text()

        self.assertRegex(
            text,
            r"(?m)^manual-evals-db manualdb manual-evals-db-refresh manualdb-refresh:$",
        )
        self.assertIn("--backup-existing", text)
        self.assertIn("--status-summary", text)
        self.assertRegex(text, r"(?m)^manual-evals-db-status manualdb-status:$")
        self.assertIn("$(PYTHON) -m tools.manual_evals_db_status", text)
        self.assertRegex(text, r"(?m)^manual-evals-db-health manualdb-health:$")
        self.assertIn("$(PYTHON) -m tools.manual_evals_db_health", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-feedback-actionables manualdb-feedback-actionables:$",
        )
        self.assertIn("--open-feedback-actionables", text)
        self.assertIn("MANUAL_EVALS_FEEDBACK_COHORT ?= $(COHORT)", text)
        self.assertIn("MANUAL_EVALS_FEEDBACK_OUTCOME ?= $(OUTCOME)", text)
        self.assertIn("MANUAL_EVALS_FEEDBACK_LIMIT ?= $(LIMIT)", text)
        self.assertIn(
            "MANUAL_EVALS_OVERLAY_SOURCE_INDEX_PATH ?= $(OVERLAY_SOURCE_INDEX_PATH)",
            text,
        )
        self.assertIn(
            "MANUAL_EVALS_OVERLAY_SOURCE_INDEX_DRAFT_PATH ?= $(DRAFT_PATH)",
            text,
        )
        self.assertIn(
            "MANUAL_EVALS_OVERLAY_SOURCE_INDEX_DRAFT_FORCE ?= $(FORCE)",
            text,
        )
        self.assertIn("$(MANUAL_EVALS_FEEDBACK_ACTIONABLE_ARGS)", text)
        self.assertIn("$(MANUAL_EVALS_OVERLAY_COMPARISON_ARGS)", text)
        self.assertIn("$(MANUAL_EVALS_OVERLAY_SOURCE_INDEX_DRAFT_ARGS)", text)
        self.assertIn("$(MANUAL_EVALS_OVERLAY_SOURCE_INDEX_VALIDATE_ARGS)", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-feedback-cohorts manualdb-feedback-cohorts:$",
        )
        self.assertIn("--open-feedback-cohorts", text)
        self.assertIn("--cohort", text)
        self.assertIn("$(MANUAL_EVALS_FEEDBACK_FILTER_ARGS)", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-feedback-source-context "
            r"manualdb-feedback-source-context:$",
        )
        self.assertIn("--feedback-source-context", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-feedback-decision-draft "
            r"manualdb-feedback-decision-draft:$",
        )
        self.assertIn("--feedback-decision-draft", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-feedback-decision-preview "
            r"manualdb-feedback-decision-preview:$",
        )
        self.assertIn("--feedback-decision-preview", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-overlay-comparison-readiness "
            r"manualdb-overlay-comparison-readiness:$",
        )
        self.assertIn("--overlay-ocr-comparison-readiness", text)
        self.assertIn("--overlay-source-index", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-overlay-source-index-draft "
            r"manualdb-overlay-source-index-draft:$",
        )
        self.assertIn("--overlay-source-index-draft", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-overlay-source-index-validate "
            r"manualdb-overlay-source-index-validate:$",
        )
        self.assertIn("--overlay-source-index-validate", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-candidates manualdb-ocr-retry-candidates:$",
        )
        self.assertIn("--ocr-retry-candidates", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-source-verification "
            r"manualdb-ocr-retry-source-verification:$",
        )
        self.assertIn("--ocr-retry-source-verification", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-source-provenance "
            r"manualdb-ocr-retry-source-provenance:$",
        )
        self.assertIn("--ocr-retry-source-provenance", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-input-packet "
            r"manualdb-ocr-retry-input-packet:$",
        )
        self.assertIn("--ocr-retry-input-packet", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-rerun-manifest "
            r"manualdb-ocr-retry-rerun-manifest:$",
        )
        self.assertIn("--ocr-retry-rerun-manifest", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-rerun-plan "
            r"manualdb-ocr-retry-rerun-plan:$",
        )
        self.assertIn("--ocr-retry-rerun-plan", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-selection-review "
            r"manualdb-ocr-retry-selection-review:$",
        )
        self.assertIn("--ocr-retry-selection-review", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-selection-template "
            r"manualdb-ocr-retry-selection-template:$",
        )
        self.assertIn("--ocr-retry-selection-template", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-selection-draft "
            r"manualdb-ocr-retry-selection-draft:$",
        )
        self.assertIn("--ocr-retry-selection-draft", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-selection-validate "
            r"manualdb-ocr-retry-selection-validate:$",
        )
        self.assertIn("--ocr-retry-selection-validate", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-selection-apply-preview "
            r"manualdb-ocr-retry-selection-apply-preview:$",
        )
        self.assertIn("--ocr-retry-selection-apply-preview", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-execution-readiness "
            r"manualdb-ocr-retry-execution-readiness:$",
        )
        self.assertIn("--ocr-retry-execution-readiness", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-execute "
            r"manualdb-ocr-retry-execute:$",
        )
        self.assertIn("--ocr-retry-execute", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-execution-report "
            r"manualdb-ocr-retry-execution-report:$",
        )
        self.assertIn("--ocr-retry-execution-report", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-feedback-closure-preview "
            r"manualdb-ocr-retry-feedback-closure-preview:$",
        )
        self.assertIn("--ocr-retry-feedback-closure-preview", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-feedback-closure-restore-preview "
            r"manualdb-ocr-retry-feedback-closure-restore-preview:$",
        )
        self.assertIn("--ocr-retry-feedback-closure-restore-preview", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-feedback-closure-restore "
            r"manualdb-ocr-retry-feedback-closure-restore:$",
        )
        self.assertIn("--ocr-retry-feedback-closure-restore", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-no-context-reclassify-preview "
            r"manualdb-no-context-reclassify-preview:$",
        )
        self.assertIn("--no-context-feedback-reclassify-preview", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-no-context-reclassify-apply "
            r"manualdb-no-context-reclassify-apply:$",
        )
        self.assertIn("--no-context-feedback-reclassify-apply", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-feedback-reclassify-preview "
            r"manualdb-feedback-reclassify-preview:$",
        )
        self.assertIn("--feedback-reclassify-preview", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-feedback-reclassify-apply "
            r"manualdb-feedback-reclassify-apply:$",
        )
        self.assertIn("--feedback-reclassify-apply", text)
        self.assertIn("MANUAL_EVALS_OCR_RETRY_CONFIRM ?= $(CONFIRM)", text)
        self.assertIn("MANUAL_EVALS_OCR_RETRY_EXECUTION_DIR ?= $(EXECUTION_DIR)", text)
        self.assertIn("MANUAL_EVALS_OCR_RETRY_RUN_DIR ?= $(RUN_DIR)", text)
        self.assertIn("MANUAL_EVALS_OCR_RETRY_BACKUP_DIR ?= $(BACKUP_DIR)", text)
        self.assertIn("MANUAL_EVALS_OCR_RETRY_RESTORE_ROOT ?= $(RESTORE_ROOT)", text)
        self.assertIn("$(MANUAL_EVALS_OCR_RETRY_EXECUTE_ARGS)", text)
        self.assertIn("$(MANUAL_EVALS_OCR_RETRY_EXECUTION_REPORT_ARGS)", text)
        self.assertIn("$(MANUAL_EVALS_OCR_RETRY_FEEDBACK_CLOSURE_PREVIEW_ARGS)", text)
        self.assertIn("$(MANUAL_EVALS_OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_ARGS)", text)
        self.assertIn("$(MANUAL_EVALS_NO_CONTEXT_RECLASSIFY_ARGS)", text)
        self.assertIn(
            "MANUAL_EVALS_FEEDBACK_RECLASSIFY_PLAN_PATH ?= $(PLAN_PATH)", text
        )
        self.assertIn("MANUAL_EVALS_FEEDBACK_DECISION_PATH ?= $(DECISION_PATH)", text)
        self.assertIn(
            "MANUAL_EVALS_FEEDBACK_DECISION_DRAFT_PATH ?= $(DRAFT_PATH)", text
        )
        self.assertIn("MANUAL_EVALS_FEEDBACK_DECISION_DRAFT_FORCE ?= $(FORCE)", text)
        self.assertIn("$(MANUAL_EVALS_FEEDBACK_DECISION_ARGS)", text)
        self.assertIn("$(MANUAL_EVALS_FEEDBACK_DECISION_DRAFT_ARGS)", text)
        self.assertIn("$(MANUAL_EVALS_FEEDBACK_RECLASSIFY_ARGS)", text)
        self.assertIn("$(MANUAL_EVALS_FEEDBACK_RECLASSIFY_APPLY_ARGS)", text)
        self.assertIn("MANUAL_EVALS_OCR_RETRY_ARTIFACT_IDS ?= $(ARTIFACT_IDS)", text)
        self.assertIn(
            "MANUAL_EVALS_OCR_RETRY_SELECTION_PATH ?= $(SELECTION_PATH)", text
        )
        self.assertIn(
            "MANUAL_EVALS_OCR_RETRY_SELECTION_DRAFT_PATH ?= $(DRAFT_PATH)", text
        )
        self.assertIn("MANUAL_EVALS_OCR_RETRY_SELECTION_DRAFT_FORCE ?= $(FORCE)", text)
        self.assertIn("$(MANUAL_EVALS_OCR_RETRY_PLAN_ARGS)", text)
        self.assertIn("$(MANUAL_EVALS_OCR_RETRY_SELECTION_DRAFT_ARGS)", text)
        self.assertIn("$(MANUAL_EVALS_OCR_RETRY_SELECTION_VALIDATE_ARGS)", text)

    def test_lifecycle_aliases_delegate_to_canonical_targets(self) -> None:
        text = _makefile_contract_text()

        self.assertRegex(text, r"(?m)^eod:\s*end$")
        self.assertIn("end-preflight:", text)
        self.assertIn("END_SKIP_GIT_CHECK=1 END_SKIP_STOP=1", text)
        self.assertRegex(
            text,
            r"(?m)^eod-stop:\s*server-daemon-stop caffeinate-off-all session-status$",
        )
        self.assertRegex(text, r"(?m)^caffeinate-on:\s*caffeinate$")
        self.assertRegex(text, r"(?m)^caffeinate-off:\s*decaffeinate$")
        self.assertRegex(text, r"(?m)^caffeinate-off-all:\s*caffeinate-off$")
        self.assertRegex(text, r"(?m)^decaffeinate-status:\s*caffeinate-status$")

    def test_shell_script_contract_check_is_named_and_closeout_visible(self) -> None:
        text = _makefile_contract_text()
        closeout_text = (REPO_ROOT / "tools" / "end_of_day_routine.sh").read_text(
            encoding="utf-8"
        )

        self.assertIn("scripts-check", _phony_targets())
        self.assertRegex(text, r"(?m)^scripts-check:$")
        self.assertIn("$(PYTHON) -m tools.check_shell_scripts", text)
        self.assertRegex(
            text,
            r"(?m)^ci-docs:\s*path-leak-check scripts-check lint-docs$",
        )
        self.assertIn(
            'run_step "scripts-check" make --no-print-directory scripts-check',
            closeout_text,
        )
        self.assertGreater(
            closeout_text.index('run_step "scripts-check"'),
            closeout_text.index('run_step "doctor-env"'),
        )
        self.assertLess(
            closeout_text.index('run_step "scripts-check"'),
            closeout_text.index('run_step "ci-python-style"'),
        )

    def test_shell_script_contract_checker_accepts_tracked_scripts(self) -> None:
        self.assertTrue(SHELL_SCRIPT_CONTRACT_SCRIPT.exists())

        result = subprocess.run(
            [sys.executable, "-m", "tools.check_shell_scripts"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("shell-script-contracts: PASS", result.stdout)
        self.assertIn("scripts checked", result.stdout)

    def test_operator_wrappers_use_dependency_edges_for_internal_chains(self) -> None:
        text = _makefile_contract_text()

        self.assertRegex(
            text,
            r"(?m)^backend-gate:\s*backend-gate-start doctor-env test quality-gate-deterministic$",
        )
        self.assertRegex(text, r"(?m)^docs:\s*open-api-docs$")
        self.assertRegex(text, r"(?m)^open-api-docs:\s*server-daemon$")
        self.assertRegex(
            text, r"(?m)^docs-open open-api-docs-browser:\s*server-daemon$"
        )
        self.assertRegex(text, r"(?m)^open-limits:\s*openai-limits$")
        self.assertRegex(text, r"(?m)^open-usage:\s*openai-usage$")
        self.assertRegex(text, r"(?m)^open-billing:\s*openai-costs$")
        self.assertRegex(text, r"(?m)^open-cost-console:\s*openai-account-summary$")
        self.assertRegex(text, r"(?m)^viz:\s*server-daemon$")
        self.assertRegex(text, r"(?m)^viz-open open-viz:\s*server-daemon$")
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
        self.assertRegex(
            text,
            r"(?m)^quality-gate-deterministic:\s*HALLUCINATION_CHAT_HARNESS_MODE\s*=\s*fixture$",
        )
        self.assertRegex(
            text,
            r"(?m)^quality-gate-deterministic:\s*STYLE_EVAL_MODE\s*=\s*deterministic$",
        )
        self.assertRegex(
            text,
            r"(?m)^quality-gate-deterministic:\s*STYLE_CHAT_HARNESS_MODE\s*=\s*fixture$",
        )
        self.assertRegex(
            text,
            r"(?m)^quality-gate-deterministic:\s*RESPONSE_BEHAVIOUR_CHAT_HARNESS_MODE\s*=\s*fixture$",
        )
        self.assertRegex(
            text,
            r"(?m)^quality-gate-deterministic:\s*RETRIEVAL_CHAT_HARNESS_MODE\s*=\s*fixture$",
        )
        self.assertRegex(
            text,
            r"(?m)^quality-gate-deterministic:\s*GATE_VECTOR_EMBEDDING_PROVIDER\s*=\s*local$",
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
        text = _makefile_source_text(MAKE_EVALS)
        config_text = _makefile_contract_text()
        guard_text = EVAL_CASE_GUARD_SCRIPT.read_text(encoding="utf-8")
        common_text = OCR_WORKFLOW_COMMON_SCRIPT.read_text(encoding="utf-8")
        guarded_runner_text = OCR_GUARDED_CASE_RUNNER_SCRIPT.read_text(encoding="utf-8")
        lane_workflow_text = OCR_TRANSCRIPT_LANE_WORKFLOW_SCRIPT.read_text(
            encoding="utf-8"
        )
        growth_case_workflow_text = OCR_GROWTH_CASE_WORKFLOW_SCRIPT.read_text(
            encoding="utf-8"
        )
        focus_workflow_text = OCR_FOCUS_STABILITY_WORKFLOW_SCRIPT.read_text(
            encoding="utf-8"
        )
        growth_workflow_text = OCR_GROWTH_STABILITY_WORKFLOW_SCRIPT.read_text(
            encoding="utf-8"
        )

        self.assertNotIn("$(MAKE)", text)
        self.assertNotIn("import json,pathlib", text)
        self.assertNotIn("CASE_COUNT=", text)
        self.assertIn("tools.count_eval_cases", guard_text)
        self.assertIn("EVAL_CASE_GUARD_SCRIPT", common_text)
        self.assertIn("eval_case_guard.sh", common_text)
        self.assertIn("ocr_workflow_use_eval_case_guard", guarded_runner_text)
        self.assertIn("eval_case_guard_or_exit", guarded_runner_text)
        self.assertIn("OCR_GUARDED_CASE_RUNNER_SCRIPT", lane_workflow_text)
        self.assertIn("OCR_EVAL_RUNNER_SCRIPT", lane_workflow_text)
        self.assertIn("OCR_STABILITY_RUNNER_SCRIPT", lane_workflow_text)
        self.assertIn("eval_case_guard_or_exit", growth_case_workflow_text)
        self.assertIn("OCR_GROWTH_EVAL_RUNNER_SCRIPT", growth_case_workflow_text)
        self.assertIn("OCR_GROWTH_BATCH_RUNNER_SCRIPT", growth_case_workflow_text)
        self.assertIn("eval_case_guard_or_exit", focus_workflow_text)
        self.assertIn("eval_case_guard_or_exit", growth_workflow_text)
        self.assertIn('bash "$(OCR_INTAKE_WORKFLOW_SCRIPT)"', text)
        self.assertIn("OCR_WORKFLOW_COMMON_SCRIPT", config_text)
        self.assertNotIn('bash "$(OCR_GUARDED_CASE_RUNNER_SCRIPT)"', text)
        self.assertIn('bash "$(OCR_TRANSCRIPT_LANE_WORKFLOW_SCRIPT)"', text)
        self.assertIn('bash "$(OCR_GROWTH_CASE_WORKFLOW_SCRIPT)"', text)
        self.assertIn('bash "$(OCR_FOCUS_STABILITY_WORKFLOW_SCRIPT)"', text)
        self.assertIn('bash "$(OCR_GROWTH_STABILITY_WORKFLOW_SCRIPT)"', text)
        self.assertIn('bash "$(OCR_HANDWRITING_EVAL_RUNNER_SCRIPT)" run', text)
        self.assertIn('bash "$(OCR_HANDWRITING_EVAL_RUNNER_SCRIPT)" report', text)
        self.assertIn(
            'bash "$(EVAL_REPORTS_PARALLEL_RUNNER_SCRIPT)"',
            text,
        )
        self.assertIn('bash "$(EVAL_SIDECAR_START_SCRIPT)"', text)
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
        self.assertNotIn("eval_case_guard_or_exit", text)
        self.assertNotIn("OCR_FOCUS_SKIP_RECENT_RATE_LIMIT", text)
        self.assertNotIn("OUTPUT_JSON=", text)
        for moved_cases in (
            "OCR_TRANSCRIPT_CASES",
            "OCR_TRANSCRIPT_CASES_HANDWRITING",
            "OCR_TRANSCRIPT_CASES_HANDWRITING_BENCHMARK",
            "OCR_TRANSCRIPT_CASES_TYPED",
            "OCR_TRANSCRIPT_CASES_TYPED_BENCHMARK",
            "OCR_TRANSCRIPT_CASES_ILLUSTRATION",
            "OCR_TRANSCRIPT_CASES_ILLUSTRATION_BENCHMARK",
        ):
            self.assertNotIn(f'eval_case_guard_or_exit "$({moved_cases})"', text)
        self.assertIn('bash "$(OCR_BASE_TRANSCRIPT_WORKFLOW_SCRIPT)" cases', text)
        self.assertIn(
            'bash "$(OCR_TRANSCRIPT_LANE_WORKFLOW_SCRIPT)" case handwriting',
            text,
        )
        self.assertIn(
            'bash "$(OCR_BASE_TRANSCRIPT_WORKFLOW_SCRIPT)" stability',
            text,
        )
        self.assertIn(
            'bash "$(OCR_TRANSCRIPT_LANE_WORKFLOW_SCRIPT)" stability handwriting-benchmark',
            text,
        )
        self.assertIn(
            'bash "$(OCR_GROWTH_CASE_WORKFLOW_SCRIPT)" eval',
            text,
        )
        self.assertIn(
            'bash "$(OCR_GROWTH_CASE_WORKFLOW_SCRIPT)" batched',
            text,
        )
        self.assertNotIn(
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
                f'bash "$(OCR_REPORT_WORKFLOW_SCRIPT)" {suite}',
                text,
            )
        for suite in (
            "export-index",
            "cases-from-export-build",
            "generalization-review",
            "transcript-delta",
        ):
            self.assertIn(
                f'bash "$(OCR_INTAKE_WORKFLOW_SCRIPT)" {suite}',
                text,
            )
        for lane in ("handwriting", "typed", "illustration"):
            self.assertIn(
                f'bash "$(OCR_INTAKE_WORKFLOW_SCRIPT)" benchmark {lane}',
                text,
            )
        self.assertNotIn(
            '$(PYTHON) -m tools.eval_ocr --timeout "$(OCR_EVAL_TIMEOUT)" --cases "$(OCR_TRANSCRIPT_CASES_HANDWRITING)" --strict',
            text,
        )
        self.assertNotIn(
            'bash "$(OCR_EVAL_RUNNER_SCRIPT)" "$(OCR_TRANSCRIPT_CASES_HANDWRITING)"',
            text,
        )
        self.assertNotIn(
            'bash "$(OCR_STABILITY_RUNNER_SCRIPT)" "$(OCR_TRANSCRIPT_CASES_HANDWRITING_BENCHMARK)"',
            text,
        )
        self.assertNotIn(
            'PYTHONUNBUFFERED=1 $(PYTHON) -m tools.eval_ocr --timeout "$(OCR_EVAL_TIMEOUT)" --cases "$(OCR_TRANSCRIPT_CASES_GROWTH)"',
            text,
        )
        self.assertNotIn(
            'bash "$(OCR_GROWTH_EVAL_RUNNER_SCRIPT)" "$(OCR_TRANSCRIPT_CASES_GROWTH)"',
            text,
        )
        self.assertNotIn(
            'bash "$(OCR_GROWTH_BATCH_RUNNER_SCRIPT)" "$(OCR_TRANSCRIPT_CASES_GROWTH)"',
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
        self.assertNotIn("eval_reports/ocr-handwriting-$$RUN_ID.json", text)
        self.assertNotIn("eval_reports/ocr-recovery-$$RUN_ID.json", text)
        self.assertNotIn("eval_reports/clip-ab-$$RUN_ID.json", text)
        self.assertNotIn("tools.eval_parallel_orchestrator", text)
        self.assertNotIn("nohup $(PYTHON) -m tools.eval_sidecar run", text)
        self.assertNotIn("PID=$$!", text)
        self.assertNotIn("nohup $(PYTHON) -m uvicorn $(ASGI_APP)", text)
        self.assertNotIn("$(PYTHON) -m tools.eval_ocr_growth_metrics", text)
        self.assertNotIn("$(PYTHON) -m tools.build_ocr_growth_fail_cohort", text)
        self.assertNotIn("$(PYTHON) -m tools.build_ocr_focus_cases", text)
        self.assertNotIn("$(PYTHON) -m tools.report_ocr_focus_fail_patterns", text)
        self.assertNotIn("$(PYTHON) -m tools.index_cgpt_export", text)
        self.assertNotIn("$(PYTHON) -m tools.build_ocr_cases_from_export", text)
        self.assertNotIn("$(PYTHON) -m tools.build_handwriting_benchmark_cases", text)
        self.assertNotIn("$(PYTHON) -m tools.build_ocr_generalization_review", text)
        self.assertNotIn("$(PYTHON) -m tools.report_ocr_case_mining_delta", text)
        self.assertNotIn("FAIL_COHORT_ARGS=", text)
        self.assertNotIn("FOCUS_ARGS=", text)
        self.assertNotIn("$(PYTHON) -m uvicorn $(ASGI_APP)", text)
        self.assertNotIn('curl -fsS "$$BASE_URL/health"', text)
        self.assertNotIn("SERVER_PID=$$!", text)
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
        self.assertRegex(
            text,
            r"(?m)^ocr-inventory:\n\t@\$\(PYTHON\) \"\$\(OCR_LANE_INVENTORY_SCRIPT\)\" \$\(strip \$\(OCR_LANE_INVENTORY_ARGS\)\) \$\(if \$\(strip \$\(OCR_LANE_INVENTORY_FRESHNESS_DAYS\)\),--freshness-days \"\$\(OCR_LANE_INVENTORY_FRESHNESS_DAYS\)\"\)$",
        )
        self.assertRegex(
            text,
            r"(?m)^ocr-inventory-json: OCR_LANE_INVENTORY_ARGS = --json\nocr-inventory-json: ocr-inventory$",
        )
        self.assertNotIn('bash "$(EVAL_SERVER_DAEMON_SCRIPT)"', text)

    def test_runtime_helper_scripts_are_named_for_their_roles(self) -> None:
        text = _makefile_contract_text()

        self.assertTrue(CAFFEINATE_SCRIPT.is_file())
        self.assertTrue(OPENAI_ACCOUNT_SCRIPT.is_file())
        self.assertTrue(SERVER_DAEMON_SCRIPT.is_file())
        self.assertTrue(os.access(CAFFEINATE_SCRIPT, os.X_OK))
        self.assertTrue(os.access(SERVER_DAEMON_SCRIPT, os.X_OK))
        caffeinate_script_text = CAFFEINATE_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("start_new_session=True", caffeinate_script_text)
        self.assertNotIn("nohup $caffeinate_cmd", caffeinate_script_text)
        self.assertIn('"$(PYTHON)" "$(OPENAI_ACCOUNT_SCRIPT)" summary', text)
        self.assertIn('"$(PYTHON)" "$(OPENAI_ACCOUNT_SCRIPT)" costs', text)
        self.assertIn('"$(PYTHON)" "$(OPENAI_ACCOUNT_SCRIPT)" usage', text)
        self.assertIn('"$(PYTHON)" "$(OPENAI_ACCOUNT_SCRIPT)" limits', text)
        self.assertIn('bash "$(CAFFEINATE_SCRIPT)" start', text)
        self.assertIn('bash "$(CAFFEINATE_SCRIPT)" stop', text)
        self.assertIn('bash "$(CAFFEINATE_SCRIPT)" stop-all', text)
        self.assertIn('bash "$(CAFFEINATE_SCRIPT)" status', text)
        self.assertIn('bash "$(SERVER_DAEMON_SCRIPT)" start', text)
        self.assertIn('bash "$(SERVER_DAEMON_SCRIPT)" stop', text)
        self.assertIn('bash "$(SERVER_DAEMON_SCRIPT)" status', text)
        self.assertNotIn('rm -f "$(SERVER_PID_FILE)"', text)
        server_daemon_script_text = SERVER_DAEMON_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("start_new_session=True", server_daemon_script_text)
        self.assertNotIn("nohup", server_daemon_script_text)
        self.assertNotIn("nohup $(CAFFEINATE_CMD)", text)
        self.assertNotIn('pgrep -f "^/usr/bin/caffeinate -d -i -m', text)
        self.assertNotIn("/usr/bin/pmset -g assertions", text)

    def test_eval_helper_scripts_are_named_for_their_roles(self) -> None:
        self.assertTrue(OCR_WORKFLOW_SCRIPT.is_file())
        self.assertTrue(EVAL_SERVER_DAEMON_SCRIPT.is_file())
        self.assertTrue(EVAL_CASE_GUARD_SCRIPT.is_file())
        self.assertTrue(OCR_WORKFLOW_COMMON_SCRIPT.is_file())
        self.assertTrue(OCR_GUARDED_CASE_RUNNER_SCRIPT.is_file())
        self.assertTrue(OCR_BASE_TRANSCRIPT_WORKFLOW_SCRIPT.is_file())
        self.assertTrue(OCR_TRANSCRIPT_LANE_WORKFLOW_SCRIPT.is_file())
        self.assertTrue(OCR_FOCUS_STABILITY_WORKFLOW_SCRIPT.is_file())
        self.assertTrue(OCR_GROWTH_STABILITY_WORKFLOW_SCRIPT.is_file())
        self.assertTrue(EVAL_REPORT_RUNNER_SCRIPT.is_file())
        self.assertTrue(EVAL_REPORTS_PARALLEL_RUNNER_SCRIPT.is_file())
        self.assertTrue(EVAL_SIDECAR_START_SCRIPT.is_file())
        self.assertTrue(LOCAL_EVAL_GATE_RUNNER_SCRIPT.is_file())
        self.assertTrue(OCR_EVAL_RUNNER_SCRIPT.is_file())
        self.assertTrue(OCR_HANDWRITING_EVAL_RUNNER_SCRIPT.is_file())
        self.assertTrue(OCR_STABILITY_RUNNER_SCRIPT.is_file())
        self.assertTrue(OCR_GROWTH_EVAL_RUNNER_SCRIPT.is_file())
        self.assertTrue(OCR_GROWTH_BATCH_RUNNER_SCRIPT.is_file())
        self.assertTrue(OCR_GROWTH_CASE_WORKFLOW_SCRIPT.is_file())
        self.assertTrue(OCR_GROWTH_STABILITY_RUNNER_SCRIPT.is_file())
        self.assertTrue(OCR_REPORT_BUILDER_SCRIPT.is_file())
        self.assertTrue(OCR_REPORT_WORKFLOW_SCRIPT.is_file())
        self.assertTrue(OCR_LANE_INVENTORY_SCRIPT.is_file())
        self.assertTrue(OCR_INTAKE_WORKFLOW_SCRIPT.is_file())
        self.assertTrue(os.access(OCR_WORKFLOW_SCRIPT, os.X_OK))
        self.assertTrue(os.access(OCR_INTAKE_WORKFLOW_SCRIPT, os.X_OK))
        self.assertTrue(os.access(EVAL_SERVER_DAEMON_SCRIPT, os.X_OK))
        self.assertTrue(os.access(EVAL_CASE_GUARD_SCRIPT, os.X_OK))
        self.assertTrue(os.access(OCR_WORKFLOW_COMMON_SCRIPT, os.X_OK))
        self.assertTrue(os.access(OCR_GUARDED_CASE_RUNNER_SCRIPT, os.X_OK))
        self.assertTrue(os.access(OCR_BASE_TRANSCRIPT_WORKFLOW_SCRIPT, os.X_OK))
        self.assertTrue(os.access(OCR_TRANSCRIPT_LANE_WORKFLOW_SCRIPT, os.X_OK))
        self.assertTrue(os.access(OCR_FOCUS_STABILITY_WORKFLOW_SCRIPT, os.X_OK))
        self.assertTrue(os.access(OCR_GROWTH_STABILITY_WORKFLOW_SCRIPT, os.X_OK))
        self.assertTrue(os.access(EVAL_REPORT_RUNNER_SCRIPT, os.X_OK))
        self.assertTrue(os.access(EVAL_REPORTS_PARALLEL_RUNNER_SCRIPT, os.X_OK))
        self.assertTrue(os.access(EVAL_SIDECAR_START_SCRIPT, os.X_OK))
        self.assertTrue(os.access(LOCAL_EVAL_GATE_RUNNER_SCRIPT, os.X_OK))
        self.assertTrue(os.access(OCR_EVAL_RUNNER_SCRIPT, os.X_OK))
        self.assertTrue(os.access(OCR_HANDWRITING_EVAL_RUNNER_SCRIPT, os.X_OK))
        self.assertTrue(os.access(OCR_STABILITY_RUNNER_SCRIPT, os.X_OK))
        self.assertTrue(os.access(OCR_GROWTH_EVAL_RUNNER_SCRIPT, os.X_OK))
        self.assertTrue(os.access(OCR_GROWTH_BATCH_RUNNER_SCRIPT, os.X_OK))
        self.assertTrue(os.access(OCR_GROWTH_CASE_WORKFLOW_SCRIPT, os.X_OK))
        self.assertTrue(os.access(OCR_GROWTH_STABILITY_RUNNER_SCRIPT, os.X_OK))
        self.assertTrue(os.access(OCR_REPORT_BUILDER_SCRIPT, os.X_OK))
        self.assertTrue(os.access(OCR_REPORT_WORKFLOW_SCRIPT, os.X_OK))
        text = _makefile_contract_text()
        self.assertIn('bash "$(EVAL_SIDECAR_START_SCRIPT)" start', text)
        self.assertIn('bash "$(EVAL_SIDECAR_START_SCRIPT)" status', text)
        self.assertIn('bash "$(EVAL_SIDECAR_START_SCRIPT)" stop', text)
        sidecar_script_text = EVAL_SIDECAR_START_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("start_new_session=True", sidecar_script_text)
        self.assertNotIn("nohup", sidecar_script_text)
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
        guarded_runner_text = OCR_GUARDED_CASE_RUNNER_SCRIPT.read_text(encoding="utf-8")
        common_text = OCR_WORKFLOW_COMMON_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("EVAL_CASE_GUARD_SCRIPT", common_text)
        self.assertIn("eval_case_guard.sh", common_text)
        self.assertIn("OCR_WORKFLOW_COMMON_SCRIPT", guarded_runner_text)
        self.assertIn("ocr_workflow_use_eval_case_guard", guarded_runner_text)
        self.assertIn('exec "$@"', guarded_runner_text)
        base_transcript_workflow_text = OCR_BASE_TRANSCRIPT_WORKFLOW_SCRIPT.read_text(
            encoding="utf-8"
        )
        self.assertIn("OCR_EVAL_RUNNER_SCRIPT", base_transcript_workflow_text)
        self.assertIn("OCR_STABILITY_RUNNER_SCRIPT", base_transcript_workflow_text)
        self.assertIn('exec bash "$eval_runner_script"', base_transcript_workflow_text)
        lane_workflow_text = OCR_TRANSCRIPT_LANE_WORKFLOW_SCRIPT.read_text(
            encoding="utf-8"
        )
        self.assertIn("OCR_GUARDED_CASE_RUNNER_SCRIPT", lane_workflow_text)
        self.assertIn("OCR_EVAL_RUNNER_SCRIPT", lane_workflow_text)
        self.assertIn("OCR_STABILITY_RUNNER_SCRIPT", lane_workflow_text)
        self.assertIn('exec bash "$guarded_case_runner_script"', lane_workflow_text)
        growth_case_workflow_text = OCR_GROWTH_CASE_WORKFLOW_SCRIPT.read_text(
            encoding="utf-8"
        )
        self.assertIn("OCR_WORKFLOW_COMMON_SCRIPT", growth_case_workflow_text)
        self.assertIn("OCR_GROWTH_EVAL_RUNNER_SCRIPT", growth_case_workflow_text)
        self.assertIn("OCR_GROWTH_BATCH_RUNNER_SCRIPT", growth_case_workflow_text)
        self.assertIn("eval_case_guard_or_exit", growth_case_workflow_text)
        report_workflow_text = OCR_REPORT_WORKFLOW_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("OCR_REPORT_BUILDER_SCRIPT", report_workflow_text)
        self.assertIn('exec bash "$report_builder_script"', report_workflow_text)
        intake_workflow_text = OCR_INTAKE_WORKFLOW_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("tools.build_ocr_cases_from_export", intake_workflow_text)
        self.assertIn("tools.build_handwriting_benchmark_cases", intake_workflow_text)
        self.assertIn("tools.build_ocr_generalization_review", intake_workflow_text)
        self.assertIn("tools.report_ocr_case_mining_delta", intake_workflow_text)
        for script in (
            OCR_FOCUS_STABILITY_WORKFLOW_SCRIPT,
            OCR_GROWTH_STABILITY_WORKFLOW_SCRIPT,
        ):
            script_text = script.read_text(encoding="utf-8")
            self.assertIn("OCR_WORKFLOW_COMMON_SCRIPT", script_text)
            self.assertIn("ocr_workflow_use_eval_case_guard", script_text)
            self.assertIn('exec bash "', script_text)
        self.assertFalse((REPO_ROOT / "tools" / "ocr_workflow.sh").exists())
        self.assertFalse((REPO_ROOT / "tools" / "ensure_server_daemon.sh").exists())

    def test_frontend_surface_names_are_legacy_portfolio_aliases(self) -> None:
        text = _makefile_contract_text()

        self.assertRegex(
            text,
            (
                r"(?m)^portfolio-app-install frontend-install:"
                r"\s*portfolio-install\n"
                r"\t@echo \"Legacy alias: use make portfolio-install\.\"$"
            ),
        )
        self.assertRegex(
            text,
            (
                r"(?m)^frontend-build:\s*portfolio-build\n"
                r"\t@echo \"Legacy alias: use make portfolio-build\.\"$"
            ),
        )

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

    def test_local_url_targets_do_not_launch_a_browser_by_default(self) -> None:
        for target, expected_label in (
            ("docs", "API docs URL"),
            ("viz", "PASS/FAIL viz URL"),
        ):
            with self.subTest(target=target):
                result = subprocess.run(
                    ["make", "-n", target],
                    cwd=REPO_ROOT,
                    check=True,
                    capture_output=True,
                    text=True,
                )

                self.assertIn(expected_label, result.stdout)
                self.assertNotIn('open "$URL"', result.stdout)
                self.assertNotIn("xdg-open", result.stdout)

    def test_local_url_targets_require_explicit_browser_launch(self) -> None:
        cases = (
            (["docs-open"], "docs-open"),
            (["viz-open"], "viz-open"),
            (["docs", "LOCAL_BROWSER_LAUNCH=system"], "docs with launch override"),
            (["viz", "LOCAL_BROWSER_LAUNCH=system"], "viz with launch override"),
        )
        for args, label in cases:
            with self.subTest(target=label):
                result = subprocess.run(
                    ["make", "-n", *args],
                    cwd=REPO_ROOT,
                    check=True,
                    capture_output=True,
                    text=True,
                )

                self.assertIn('open "$URL"', result.stdout)
                self.assertIn("xdg-open", result.stdout)

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
            "open-api-docs-browser",
            "docs-open",
            "viz",
            "viz-open",
            "open-viz",
            "openai-account-summary",
            "openai-costs",
            "openai-usage",
            "openai-limits",
            "open-cost-console",
            "open-usage",
            "open-billing",
            "open-limits",
            "caffeinate",
            "scripts-check",
            "caffeinate-status",
            "caffeinate-off-all",
            "eod-stop",
            "backend-gate",
            "cgpt-export-index",
            "ocr-cases-from-export-build",
            "ocrminehand",
            "ocr-handwriting-benchmark-cases",
            "ocr-generalization-review",
            "ocr-transcript-delta",
            "ocrkernel",
            "ocr-inventory",
            "ocr-inventory-json",
            "ocr-data",
            "ocr-notebook-workflow",
            "eval-ocr-transcript-cases",
            "eval-ocr-transcript-cases-growth",
            "eval-ocr-transcript-cases-growth-batched",
            "eval-ocr-transcript-cases-handwriting",
            "eval-ocr-transcript-cases-typed-benchmark",
            "eval-ocr-transcript-stability",
            "eval-ocr-transcript-stability-handwriting-benchmark",
            "eval-ocr-transcript-growth",
            "eval-ocr-growth-fail-cohort",
            "eval-ocr-focus-cases",
            "eval-ocr-focus-stability",
            "eval-ocr-focus-fail-patterns",
            "ci-python-style",
            "ci-python-type-check",
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

    def test_ci_gate_includes_ruff_style_checks(self) -> None:
        text = _makefile_contract_text()
        workflow_text = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(
            encoding="utf-8"
        )

        self.assertRegex(
            text,
            r"(?m)^ci:\s*ci-docs ci-python-style ci-python-type-check ci-package ci-test ci-python-security ci-node-security$",
        )
        self.assertRegex(
            text,
            r"(?m)^ci-python-style:\s*ruff-check ruff-format-check$",
        )
        self.assertRegex(text, r"(?m)^ci-python-type-check:\s*type-check$")
        self.assertIn("python-style:", workflow_text)
        self.assertIn("make ci-python-style PYTHON=python", workflow_text)
        self.assertIn("python-type-check:", workflow_text)
        self.assertIn("make ci-python-type-check PYTHON=python", workflow_text)

    def test_python_security_gate_keeps_narrow_no_fix_audit_exception(self) -> None:
        text = _makefile_contract_text()

        self.assertIn('$(PYTHON) -m pip_audit -r "$(REQUIREMENTS_LOCK)"', text)
        self.assertIn("$(PIP_AUDIT_ARGS)", text)
        self.assertIn("PYSEC-2025-183 / CVE-2025-45768", text)
        self.assertNotIn("--ignore-vuln CVE-", text)

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
        self.assertIn("ocr-inventory", targets)
        self.assertIn("ocr-inventory-json", targets)
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
