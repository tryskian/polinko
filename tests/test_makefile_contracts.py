import os
import re
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MAKEFILE = REPO_ROOT / "Makefile"
MAKE_BUILD = REPO_ROOT / "makefiles" / "build.mk"
MAKE_BUILD_DEPENDENCIES = REPO_ROOT / "makefiles" / "build" / "dependencies.mk"
MAKE_BUILD_DEPENDENCIES_LOCKFILE = (
    REPO_ROOT / "makefiles" / "build" / "dependencies" / "lockfile.mk"
)
MAKE_CONFIG = REPO_ROOT / "makefiles" / "config.mk"
MAKE_CONFIG_OPS = REPO_ROOT / "makefiles" / "config" / "ops.mk"
MAKE_CONFIG_OPS_GITHUB = REPO_ROOT / "makefiles" / "config" / "ops" / "github.mk"
MAKE_CONFIG_OPS_K6 = REPO_ROOT / "makefiles" / "config" / "ops" / "k6.mk"
MAKE_CONFIG_OPS_TRIVY = REPO_ROOT / "makefiles" / "config" / "ops" / "trivy.mk"
MAKE_CONFIG_RUNTIME = REPO_ROOT / "makefiles" / "config" / "runtime.mk"
MAKE_CONFIG_RUNTIME_OPENAI_ACCOUNT = (
    REPO_ROOT / "makefiles" / "config" / "runtime" / "openai-account.mk"
)
MAKE_CONFIG_RUNTIME_CAFFEINATE = (
    REPO_ROOT / "makefiles" / "config" / "runtime" / "caffeinate.mk"
)
MAKE_CONFIG_EVALS = REPO_ROOT / "makefiles" / "config" / "evals.mk"
MAKE_CONFIG_EVALS_GATES = REPO_ROOT / "makefiles" / "config" / "evals" / "gates.mk"
MAKE_CONFIG_EVALS_GATES_RUNNER = (
    REPO_ROOT / "makefiles" / "config" / "evals" / "gates" / "runner.mk"
)
MAKE_CONFIG_EVALS_OCR_CASES = (
    REPO_ROOT / "makefiles" / "config" / "evals" / "ocr-cases.mk"
)
MAKE_CONFIG_EVALS_OCR_CASES_INTAKE_WORKFLOW = (
    REPO_ROOT / "makefiles" / "config" / "evals" / "ocr-cases" / "intake-workflow.mk"
)
MAKE_CONFIG_EVALS_SIDECAR = REPO_ROOT / "makefiles" / "config" / "evals" / "sidecar.mk"
MAKE_CONFIG_EVALS_OCR_RUNS = (
    REPO_ROOT / "makefiles" / "config" / "evals" / "ocr-runs.mk"
)
MAKE_CONFIG_EVALS_OCR_RUNS_FOCUS = (
    REPO_ROOT / "makefiles" / "config" / "evals" / "ocr-runs" / "focus.mk"
)
MAKE_CONFIG_EVALS_OCR_RUNS_DIRECT_RUNNERS = (
    REPO_ROOT / "makefiles" / "config" / "evals" / "ocr-runs" / "direct-runners.mk"
)
MAKE_CONFIG_EVALS_OCR_RUNS_TRANSCRIPT_LANES = (
    REPO_ROOT / "makefiles" / "config" / "evals" / "ocr-runs" / "transcript-lanes.mk"
)
MAKE_CONFIG_EVALS_OCR_RUNS_TRANSCRIPT_LANES_LANE_WORKFLOW = (
    REPO_ROOT
    / "makefiles"
    / "config"
    / "evals"
    / "ocr-runs"
    / "transcript-lanes"
    / "lane-workflow.mk"
)
MAKE_CONFIG_EVALS_OCR_RUNS_GROWTH = (
    REPO_ROOT / "makefiles" / "config" / "evals" / "ocr-runs" / "growth.mk"
)
MAKE_CONFIG_EVALS_OCR_RUNS_GROWTH_STABILITY_WORKFLOW = (
    REPO_ROOT
    / "makefiles"
    / "config"
    / "evals"
    / "ocr-runs"
    / "growth"
    / "stability-workflow.mk"
)
MAKE_CONFIG_EVALS_OCR_RUNS_GROWTH_CASE_WORKFLOW = (
    REPO_ROOT
    / "makefiles"
    / "config"
    / "evals"
    / "ocr-runs"
    / "growth"
    / "case-workflow.mk"
)
MAKE_CONFIG_EVALS_OCR_RUNS_DEFAULTS = (
    REPO_ROOT / "makefiles" / "config" / "evals" / "ocr-runs" / "defaults.mk"
)
MAKE_CONFIG_EVALS_REPORTS = REPO_ROOT / "makefiles" / "config" / "evals" / "reports.mk"
MAKE_CONFIG_EVALS_REPORTS_RUNNER = (
    REPO_ROOT / "makefiles" / "config" / "evals" / "reports" / "runner.mk"
)
MAKE_CONFIG_EVALS_REPORTS_PARALLEL_RUNNER = (
    REPO_ROOT / "makefiles" / "config" / "evals" / "reports" / "parallel-runner.mk"
)
MAKE_CONFIG_EVALS_REPORTS_OCR_BUILDER = (
    REPO_ROOT / "makefiles" / "config" / "evals" / "reports" / "ocr-builder.mk"
)
MAKE_CONFIG_SURFACES = REPO_ROOT / "makefiles" / "config" / "surfaces.mk"
MAKE_CONFIG_SURFACES_MANUAL_EVALS = (
    REPO_ROOT / "makefiles" / "config" / "surfaces" / "manual-evals.mk"
)
MAKE_CONFIG_SURFACES_MANUAL_EVALS_OCR_RETRY = (
    REPO_ROOT / "makefiles" / "config" / "surfaces" / "manual-evals" / "ocr-retry.mk"
)
MAKE_CHECKS = REPO_ROOT / "makefiles" / "checks.mk"
MAKE_CHECKS_TESTS = REPO_ROOT / "makefiles" / "checks" / "tests.mk"
MAKE_CHECKS_PYTHON = REPO_ROOT / "makefiles" / "checks" / "python.mk"
MAKE_CHECKS_DOCS = REPO_ROOT / "makefiles" / "checks" / "docs.mk"
MAKE_CHECKS_DOCS_DIAGRAMS = REPO_ROOT / "makefiles" / "checks" / "docs" / "diagrams.mk"
MAKE_CHECKS_DOCS_TRANSCRIPTS = (
    REPO_ROOT / "makefiles" / "checks" / "docs" / "transcripts.mk"
)
MAKE_CHECKS_RUNTIME_AUDITS = REPO_ROOT / "makefiles" / "checks" / "runtime-audits.mk"
MAKE_CHECKS_RUNTIME_AUDITS_DOCTOR_ENV = (
    REPO_ROOT / "makefiles" / "checks" / "runtime-audits" / "doctor-env.mk"
)
MAKE_CHECKS_DEV_TOOLS = REPO_ROOT / "makefiles" / "checks" / "dev-tools.mk"
MAKE_CHECKS_DEV_TOOLS_GITHUB = (
    REPO_ROOT / "makefiles" / "checks" / "dev-tools" / "github.mk"
)
MAKE_CHECKS_DEV_TOOLS_ACT = REPO_ROOT / "makefiles" / "checks" / "dev-tools" / "act.mk"
MAKE_CHECKS_DEV_TOOLS_PRECOMMIT = (
    REPO_ROOT / "makefiles" / "checks" / "dev-tools" / "precommit.mk"
)
MAKE_SURFACES = REPO_ROOT / "makefiles" / "surfaces.mk"
MAKE_SURFACES_LOCAL_BROWSER = REPO_ROOT / "makefiles" / "surfaces" / "local-browser.mk"
MAKE_SURFACES_NOTEBOOKS = REPO_ROOT / "makefiles" / "surfaces" / "notebooks.mk"
MAKE_SURFACES_MANUAL_EVALS = REPO_ROOT / "makefiles" / "surfaces" / "manual-evals.mk"
MAKE_SURFACES_MANUAL_EVALS_FEEDBACK = (
    REPO_ROOT / "makefiles" / "surfaces" / "manual-evals" / "feedback.mk"
)
MAKE_SURFACES_MANUAL_EVALS_OCR_RETRY = (
    REPO_ROOT / "makefiles" / "surfaces" / "manual-evals" / "ocr-retry.mk"
)
MAKE_EVALS = REPO_ROOT / "makefiles" / "evals.mk"
MAKE_EVALS_SHORTCUTS = REPO_ROOT / "makefiles" / "evals" / "shortcuts.mk"
MAKE_EVALS_SHORTCUTS_OCR_INTAKE = (
    REPO_ROOT / "makefiles" / "evals" / "shortcuts" / "ocr-intake.mk"
)
MAKE_EVALS_SHORTCUTS_OCR_RUNS = (
    REPO_ROOT / "makefiles" / "evals" / "shortcuts" / "ocr-runs.mk"
)
MAKE_EVALS_SHORTCUTS_UTILITIES = (
    REPO_ROOT / "makefiles" / "evals" / "shortcuts" / "utilities.mk"
)
MAKE_EVALS_CORE = REPO_ROOT / "makefiles" / "evals" / "core.mk"
MAKE_EVALS_CORE_QUALITY = REPO_ROOT / "makefiles" / "evals" / "core" / "quality.mk"
MAKE_EVALS_CORE_OCR = REPO_ROOT / "makefiles" / "evals" / "core" / "ocr.mk"
MAKE_EVALS_GATES = REPO_ROOT / "makefiles" / "evals" / "gates.mk"
MAKE_EVALS_OCR_INTAKE = REPO_ROOT / "makefiles" / "evals" / "ocr-intake.mk"
MAKE_EVALS_OCR_RUNS = REPO_ROOT / "makefiles" / "evals" / "ocr-runs.mk"
MAKE_EVALS_OCR_RUNS_LANES = REPO_ROOT / "makefiles" / "evals" / "ocr-runs" / "lanes.mk"
MAKE_OPS = REPO_ROOT / "makefiles" / "ops.mk"
MAKE_RUNTIME = REPO_ROOT / "makefiles" / "runtime.mk"
MAKE_RUNTIME_CORE = REPO_ROOT / "makefiles" / "runtime" / "core.mk"
MAKE_RUNTIME_LOCAL_URLS = REPO_ROOT / "makefiles" / "runtime" / "local-urls.mk"
OCR_WORKFLOW_SCRIPT = REPO_ROOT / "tools" / "run_ocr_workflow.sh"
CAFFEINATE_SCRIPT = REPO_ROOT / "tools" / "manage_caffeinate.sh"
OPENAI_ACCOUNT_SCRIPT = REPO_ROOT / "tools" / "openai_account_summary.py"
SERVER_DAEMON_SCRIPT = REPO_ROOT / "tools" / "run_server_daemon.sh"
LOCAL_URL_LAUNCHER_SCRIPT = REPO_ROOT / "tools" / "open_local_url.sh"
PWCLI_DAILY_SCRIPT = REPO_ROOT / "tools" / "pwcli_daily.sh"
PROCESS_LIFECYCLE_COMMON_SCRIPT = REPO_ROOT / "tools" / "process_lifecycle_common.sh"
DETACHED_PROCESS_LAUNCHER_SCRIPT = REPO_ROOT / "tools" / "launch_detached_process.py"
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
LOCAL_PRIVACY_GUARD_SCRIPT = REPO_ROOT / "tools" / "local_privacy_guard.sh"
END_GIT_CHECK_SCRIPT = REPO_ROOT / "tools" / "check_end_git_clean.sh"
SESSION_STATUS_SCRIPT = REPO_ROOT / "tools" / "session_status.sh"
MAKE_RUNTIME_SCRIPT = REPO_ROOT / "tools" / "make_runtime.sh"
SHELL_COMMAND_COMMON_SCRIPT = REPO_ROOT / "tools" / "shell_command_common.sh"
OPEN_VENV_SHELL_SCRIPT = REPO_ROOT / "tools" / "open_venv_shell.sh"


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

    def test_build_targets_are_extracted_through_role_includes(self) -> None:
        build_entry_text = MAKE_BUILD.read_text(encoding="utf-8")
        build_dependencies_entry_text = MAKE_BUILD_DEPENDENCIES.read_text(
            encoding="utf-8"
        )
        contract_text = _makefile_contract_text()

        self.assertIn("include makefiles/build/ci.mk", build_entry_text)
        self.assertIn("include makefiles/build/dependencies.mk", build_entry_text)
        self.assertIn("include makefiles/build/package.mk", build_entry_text)
        self.assertIn("include makefiles/build/security.mk", build_entry_text)
        self.assertNotRegex(
            build_dependencies_entry_text,
            r"(?m)^(?:\.PHONY|[A-Za-z0-9_.-]+(?:\s+[A-Za-z0-9_.-]+)*:)",
        )
        self.assertIn(
            "include makefiles/build/dependencies/install.mk",
            build_dependencies_entry_text,
        )
        self.assertIn(
            "include makefiles/build/dependencies/refresh.mk",
            build_dependencies_entry_text,
        )
        self.assertIn(
            "include makefiles/build/dependencies/lockfile.mk",
            build_dependencies_entry_text,
        )
        self.assertIn("pr-preflight:", contract_text)
        self.assertIn("ci:", contract_text)
        self.assertIn("deps-lock-check:", contract_text)
        self.assertIn("package-install-check:", contract_text)
        self.assertIn("python-security-check:", contract_text)
        self.assertIn("node-security-check:", contract_text)

    def test_dependency_lock_targets_use_helper_dispatch(self) -> None:
        lockfile_text = MAKE_BUILD_DEPENDENCIES_LOCKFILE.read_text(encoding="utf-8")

        self.assertRegex(lockfile_text, r"(?m)^deps-lock:$")
        self.assertRegex(lockfile_text, r"(?m)^deps-lock-check:$")
        self.assertEqual(lockfile_text.count("tools.run_dependency_lock"), 2)
        self.assertIn('--python "$(PYTHON)"', lockfile_text)
        self.assertIn('--requirements-in "$(REQUIREMENTS_IN)"', lockfile_text)
        self.assertIn('--requirements-lock "$(REQUIREMENTS_LOCK)"', lockfile_text)
        self.assertIn('--pip-tools-version "$(PIP_TOOLS_VERSION)"', lockfile_text)
        self.assertIn("--ensure-pip-tools", lockfile_text)
        self.assertIn("--check-lockfile", lockfile_text)
        self.assertNotIn("@set -eu", lockfile_text)
        self.assertNotIn("piptools --version", lockfile_text)
        self.assertNotIn("git diff --exit-code", lockfile_text)

    def test_check_targets_are_extracted_through_role_includes(self) -> None:
        checks_entry_text = MAKE_CHECKS.read_text(encoding="utf-8")
        tests_entry_text = MAKE_CHECKS_TESTS.read_text(encoding="utf-8")
        python_entry_text = MAKE_CHECKS_PYTHON.read_text(encoding="utf-8")
        docs_entry_text = MAKE_CHECKS_DOCS.read_text(encoding="utf-8")
        docs_diagrams_text = MAKE_CHECKS_DOCS_DIAGRAMS.read_text(encoding="utf-8")
        docs_transcripts_text = MAKE_CHECKS_DOCS_TRANSCRIPTS.read_text(encoding="utf-8")
        runtime_audits_entry_text = MAKE_CHECKS_RUNTIME_AUDITS.read_text(
            encoding="utf-8"
        )
        runtime_audits_doctor_env_entry_text = (
            MAKE_CHECKS_RUNTIME_AUDITS_DOCTOR_ENV.read_text(encoding="utf-8")
        )
        dev_tools_entry_text = MAKE_CHECKS_DEV_TOOLS.read_text(encoding="utf-8")
        dev_tools_github_text = MAKE_CHECKS_DEV_TOOLS_GITHUB.read_text(encoding="utf-8")
        dev_tools_act_text = MAKE_CHECKS_DEV_TOOLS_ACT.read_text(encoding="utf-8")
        dev_tools_precommit_text = MAKE_CHECKS_DEV_TOOLS_PRECOMMIT.read_text(
            encoding="utf-8"
        )
        contract_text = _makefile_contract_text()

        self.assertIn("include makefiles/checks/tests.mk", checks_entry_text)
        self.assertIn("include makefiles/checks/python.mk", checks_entry_text)
        self.assertIn("include makefiles/checks/docs.mk", checks_entry_text)
        self.assertIn(
            "include makefiles/checks/runtime-audits.mk",
            checks_entry_text,
        )
        self.assertIn("include makefiles/checks/dev-tools.mk", checks_entry_text)
        self.assertNotRegex(
            tests_entry_text,
            r"(?m)^(?:\.PHONY|[A-Za-z0-9_.-]+(?:\s+[A-Za-z0-9_.-]+)*:)",
        )
        self.assertIn(
            "include makefiles/checks/tests/unit.mk",
            tests_entry_text,
        )
        self.assertIn(
            "include makefiles/checks/tests/backend-gate.mk",
            tests_entry_text,
        )
        self.assertNotRegex(
            python_entry_text,
            r"(?m)^(?:\.PHONY|[A-Za-z0-9_.-]+(?:\s+[A-Za-z0-9_.-]+)*:)",
        )
        self.assertIn(
            "include makefiles/checks/python/compile.mk",
            python_entry_text,
        )
        self.assertIn(
            "include makefiles/checks/python/type.mk",
            python_entry_text,
        )
        self.assertIn(
            "include makefiles/checks/python/ruff.mk",
            python_entry_text,
        )
        self.assertNotRegex(
            docs_entry_text,
            r"(?m)^(?:\.PHONY|[A-Za-z0-9_.-]+(?:\s+[A-Za-z0-9_.-]+)*:)",
        )
        self.assertIn(
            "include makefiles/checks/docs/lint.mk",
            docs_entry_text,
        )
        self.assertIn(
            "include makefiles/checks/docs/diagrams.mk",
            docs_entry_text,
        )
        self.assertIn(
            "include makefiles/checks/docs/transcripts.mk",
            docs_entry_text,
        )
        self.assertIn(
            "include makefiles/checks/docs/closeout.mk",
            docs_entry_text,
        )
        self.assertIn(
            "@$(call repo_activity,make mermaid-render,mermaid-render)",
            docs_diagrams_text,
        )
        self.assertIn(
            "@$(call repo_activity,make d3-render,d3-render)",
            docs_diagrams_text,
        )
        self.assertIn(
            "@$(call repo_activity,make transcript-fix,transcript-fix)",
            docs_transcripts_text,
        )
        self.assertIn(
            "@$(call repo_activity,make transcript-check,transcript-check)",
            docs_transcripts_text,
        )
        self.assertNotRegex(
            dev_tools_entry_text,
            r"(?m)^(?:\.PHONY|[A-Za-z0-9_.-]+(?:\s+[A-Za-z0-9_.-]+)*:)",
        )
        self.assertIn(
            "include makefiles/checks/dev-tools/search.mk",
            dev_tools_entry_text,
        )
        self.assertIn(
            "include makefiles/checks/dev-tools/precommit.mk",
            dev_tools_entry_text,
        )
        self.assertIn(
            "include makefiles/checks/dev-tools/act.mk",
            dev_tools_entry_text,
        )
        self.assertIn(
            "include makefiles/checks/dev-tools/github.mk",
            dev_tools_entry_text,
        )
        self.assertIn("github-health:", dev_tools_github_text)
        self.assertIn(
            "@$(call repo_activity,make github-health,github-health)",
            dev_tools_github_text,
        )
        self.assertIn(
            "@$(call repo_activity,make act-list,act-list)", dev_tools_act_text
        )
        self.assertIn("@$(call repo_activity,make act-ci,act-ci)", dev_tools_act_text)
        self.assertIn(
            "@$(call repo_activity,make precommit-install,precommit-install)",
            dev_tools_precommit_text,
        )
        self.assertIn(
            "@$(call repo_activity,make precommit-run,precommit-run)",
            dev_tools_precommit_text,
        )
        self.assertIn(
            "$(PYTHON) -m pre_commit install --install-hooks --hook-type pre-commit",
            dev_tools_precommit_text,
        )
        self.assertIn(
            "$(PYTHON) -m pre_commit run --all-files",
            dev_tools_precommit_text,
        )
        self.assertIn('$(PYTHON) -m tools.github_health --gh "$(GH)"', contract_text)
        self.assertIn('--run-limit "$(GITHUB_HEALTH_RUN_LIMIT)"', contract_text)
        self.assertIn('--pr-limit "$(GITHUB_HEALTH_PR_LIMIT)"', contract_text)
        self.assertIn(
            '$(if $(strip $(GITHUB_HEALTH_REPO)),--repo "$(GITHUB_HEALTH_REPO)",)',
            contract_text,
        )
        self.assertIn(
            "include makefiles/checks/runtime-audits/shell.mk",
            runtime_audits_entry_text,
        )
        self.assertIn(
            "include makefiles/checks/runtime-audits/path-leaks.mk",
            runtime_audits_entry_text,
        )
        self.assertIn(
            "include makefiles/checks/runtime-audits/runtime-config.mk",
            runtime_audits_entry_text,
        )
        self.assertIn(
            "include makefiles/checks/runtime-audits/doctor-env.mk",
            runtime_audits_entry_text,
        )
        self.assertNotRegex(
            runtime_audits_doctor_env_entry_text,
            r"(?m)^(?:\.PHONY|[A-Za-z0-9_.-]+(?:\s+[A-Za-z0-9_.-]+)*:)",
        )
        self.assertIn(
            "include makefiles/checks/runtime-audits/doctor-env/target.mk",
            runtime_audits_doctor_env_entry_text,
        )
        self.assertNotIn("doctor-env/source.mk", runtime_audits_doctor_env_entry_text)
        self.assertNotIn("doctor-env/venv.mk", runtime_audits_doctor_env_entry_text)
        self.assertNotIn("doctor-env/runner.mk", runtime_audits_doctor_env_entry_text)
        self.assertRegex(contract_text, r"(?m)^test:$")
        self.assertRegex(contract_text, r"(?m)^backend-gate:")
        self.assertNotRegex(contract_text, r"(?m)^\tbackend-gate:")
        self.assertRegex(contract_text, r"(?m)^ruff-check:$")
        self.assertIn("lint-docs:", contract_text)
        self.assertIn("risk-scan:", contract_text)
        self.assertIn("github-health:", contract_text)
        self.assertIn("repo-search:", contract_text)

    def test_eval_targets_are_extracted_through_role_includes(self) -> None:
        evals_entry_text = MAKE_EVALS.read_text(encoding="utf-8")
        shortcuts_entry_text = MAKE_EVALS_SHORTCUTS.read_text(encoding="utf-8")
        shortcuts_ocr_intake_entry_text = MAKE_EVALS_SHORTCUTS_OCR_INTAKE.read_text(
            encoding="utf-8"
        )
        shortcuts_ocr_runs_entry_text = MAKE_EVALS_SHORTCUTS_OCR_RUNS.read_text(
            encoding="utf-8"
        )
        shortcuts_utilities_entry_text = MAKE_EVALS_SHORTCUTS_UTILITIES.read_text(
            encoding="utf-8"
        )
        core_entry_text = MAKE_EVALS_CORE.read_text(encoding="utf-8")
        core_quality_entry_text = MAKE_EVALS_CORE_QUALITY.read_text(encoding="utf-8")
        core_ocr_entry_text = MAKE_EVALS_CORE_OCR.read_text(encoding="utf-8")
        gates_entry_text = MAKE_EVALS_GATES.read_text(encoding="utf-8")
        ocr_intake_entry_text = MAKE_EVALS_OCR_INTAKE.read_text(encoding="utf-8")
        ocr_runs_entry_text = MAKE_EVALS_OCR_RUNS.read_text(encoding="utf-8")
        ocr_runs_lanes_entry_text = MAKE_EVALS_OCR_RUNS_LANES.read_text(
            encoding="utf-8"
        )
        contract_text = _makefile_contract_text()

        self.assertIn("include makefiles/evals/shortcuts.mk", evals_entry_text)
        self.assertIn("include makefiles/evals/core.mk", evals_entry_text)
        self.assertIn("include makefiles/evals/gates.mk", evals_entry_text)
        self.assertIn("include makefiles/evals/ocr-intake.mk", evals_entry_text)
        self.assertIn("include makefiles/evals/ocr-runs.mk", evals_entry_text)
        self.assertIn(
            "include makefiles/evals/shortcuts/ocr-intake.mk",
            shortcuts_entry_text,
        )
        self.assertIn(
            "include makefiles/evals/shortcuts/ocr-runs.mk",
            shortcuts_entry_text,
        )
        self.assertIn(
            "include makefiles/evals/shortcuts/utilities.mk",
            shortcuts_entry_text,
        )
        self.assertIsNone(
            re.search(
                r"(?m)^\.PHONY:|^[-a-zA-Z0-9_]+:",
                shortcuts_ocr_intake_entry_text,
            )
        )
        self.assertIn(
            "include makefiles/evals/shortcuts/ocr-intake/base.mk",
            shortcuts_ocr_intake_entry_text,
        )
        self.assertIn(
            "include makefiles/evals/shortcuts/ocr-intake/lanes.mk",
            shortcuts_ocr_intake_entry_text,
        )
        self.assertIn(
            "include makefiles/evals/shortcuts/ocr-intake/filters.mk",
            shortcuts_ocr_intake_entry_text,
        )
        self.assertIsNone(
            re.search(
                r"(?m)^\.PHONY:|^[-a-zA-Z0-9_]+:",
                shortcuts_utilities_entry_text,
            )
        )
        self.assertIn(
            "include makefiles/evals/shortcuts/utilities/runtime-null.mk",
            shortcuts_utilities_entry_text,
        )
        self.assertIn(
            "include makefiles/evals/shortcuts/utilities/ocr-inventory.mk",
            shortcuts_utilities_entry_text,
        )
        self.assertIn(
            "include makefiles/evals/shortcuts/utilities/ocr-workflows.mk",
            shortcuts_utilities_entry_text,
        )
        self.assertIsNone(
            re.search(
                r"(?m)^\.PHONY:|^[-a-zA-Z0-9_]+:",
                shortcuts_ocr_runs_entry_text,
            )
        )
        self.assertIn(
            "include makefiles/evals/shortcuts/ocr-runs/transcripts.mk",
            shortcuts_ocr_runs_entry_text,
        )
        self.assertIn(
            "include makefiles/evals/shortcuts/ocr-runs/modalities.mk",
            shortcuts_ocr_runs_entry_text,
        )
        self.assertIn(
            "include makefiles/evals/shortcuts/ocr-runs/focus.mk",
            shortcuts_ocr_runs_entry_text,
        )
        self.assertIn(
            "include makefiles/evals/shortcuts/ocr-runs/workflow.mk",
            shortcuts_ocr_runs_entry_text,
        )
        self.assertIn(
            "include makefiles/evals/shortcuts/ocr-runs/benchmarks.mk",
            shortcuts_ocr_runs_entry_text,
        )
        self.assertIn("include makefiles/evals/core/retrieval.mk", core_entry_text)
        self.assertIn("include makefiles/evals/core/quality.mk", core_entry_text)
        self.assertIn("include makefiles/evals/core/ocr.mk", core_entry_text)
        self.assertIn("include makefiles/evals/core/clip.mk", core_entry_text)
        self.assertIn("include makefiles/evals/core/reports.mk", core_entry_text)
        self.assertIn("include makefiles/evals/core/maintenance.mk", core_entry_text)
        self.assertIsNone(
            re.search(
                r"(?m)^\.PHONY:|^[-a-zA-Z0-9_]+:",
                core_quality_entry_text,
            )
        )
        self.assertIn(
            "include makefiles/evals/core/quality/hallucination.mk",
            core_quality_entry_text,
        )
        self.assertIn(
            "include makefiles/evals/core/quality/style.mk",
            core_quality_entry_text,
        )
        self.assertIn(
            "include makefiles/evals/core/quality/response-behaviour.mk",
            core_quality_entry_text,
        )
        self.assertIsNone(
            re.search(
                r"(?m)^\.PHONY:|^[-a-zA-Z0-9_]+:",
                core_ocr_entry_text,
            )
        )
        self.assertIn(
            "include makefiles/evals/core/ocr/safety.mk",
            core_ocr_entry_text,
        )
        self.assertIn(
            "include makefiles/evals/core/ocr/base.mk",
            core_ocr_entry_text,
        )
        self.assertIn(
            "include makefiles/evals/core/ocr/handwriting.mk",
            core_ocr_entry_text,
        )
        self.assertIn(
            "include makefiles/evals/core/ocr/recovery.mk",
            core_ocr_entry_text,
        )
        self.assertIsNone(
            re.search(
                r"(?m)^\.PHONY:|^[-a-zA-Z0-9_]+:",
                gates_entry_text,
            )
        )
        self.assertIn("include makefiles/evals/gates/smoke.mk", gates_entry_text)
        self.assertIn("include makefiles/evals/gates/sidecar.mk", gates_entry_text)
        self.assertIn("include makefiles/evals/gates/reports.mk", gates_entry_text)
        self.assertIn("include makefiles/evals/gates/quality.mk", gates_entry_text)
        self.assertIsNone(
            re.search(
                r"(?m)^\.PHONY:|^[-a-zA-Z0-9_]+:",
                ocr_intake_entry_text,
            )
        )
        self.assertIn(
            "include makefiles/evals/ocr-intake/export.mk",
            ocr_intake_entry_text,
        )
        self.assertIn(
            "include makefiles/evals/ocr-intake/benchmarks.mk",
            ocr_intake_entry_text,
        )
        self.assertIn(
            "include makefiles/evals/ocr-intake/review.mk",
            ocr_intake_entry_text,
        )
        self.assertIn(
            "include makefiles/evals/ocr-runs/transcripts.mk",
            ocr_runs_entry_text,
        )
        self.assertIn(
            "include makefiles/evals/ocr-runs/growth.mk",
            ocr_runs_entry_text,
        )
        self.assertIn(
            "include makefiles/evals/ocr-runs/lanes.mk",
            ocr_runs_entry_text,
        )
        self.assertIn(
            "include makefiles/evals/ocr-runs/reports.mk",
            ocr_runs_entry_text,
        )
        self.assertIn(
            "include makefiles/evals/ocr-runs/focus.mk",
            ocr_runs_entry_text,
        )
        self.assertIsNone(
            re.search(
                r"(?m)^\.PHONY:|^[-a-zA-Z0-9_]+:",
                ocr_runs_lanes_entry_text,
            )
        )
        self.assertIn(
            "include makefiles/evals/ocr-runs/lanes/cases.mk",
            ocr_runs_lanes_entry_text,
        )
        self.assertIn(
            "include makefiles/evals/ocr-runs/lanes/stability.mk",
            ocr_runs_lanes_entry_text,
        )
        self.assertIn("ocrkernel:", contract_text)
        self.assertIn("ocrminehand: OCR_CASES_FROM_EXPORT_ARGS =", contract_text)
        self.assertIn("ocrfocus:", contract_text)
        self.assertIn("runtime-null-audit:", contract_text)
        self.assertIn("eval-retrieval:", contract_text)
        self.assertIn("eval-hallucination:", contract_text)
        self.assertIn("eval-ocr:", contract_text)
        self.assertIn("eval-clip-ab:", contract_text)
        self.assertIn("eval-reports:", contract_text)
        self.assertIn("backfill-eval-traces:", contract_text)
        self.assertIn(
            "eval-ocr-transcript-stability-growth:",
            contract_text,
        )

    def test_runtime_targets_are_extracted_through_role_includes(self) -> None:
        runtime_entry_text = MAKE_RUNTIME.read_text(encoding="utf-8")
        runtime_core_entry_text = MAKE_RUNTIME_CORE.read_text(encoding="utf-8")
        runtime_local_urls_entry_text = MAKE_RUNTIME_LOCAL_URLS.read_text(
            encoding="utf-8"
        )
        contract_text = _makefile_contract_text()

        self.assertIn("include makefiles/runtime/core.mk", runtime_entry_text)
        self.assertIn("include makefiles/runtime/server.mk", runtime_entry_text)
        self.assertIn("include makefiles/runtime/local-urls.mk", runtime_entry_text)
        self.assertIn(
            "include makefiles/runtime/openai-account.mk",
            runtime_entry_text,
        )
        self.assertIn("include makefiles/runtime/caffeinate.mk", runtime_entry_text)
        self.assertIn("include makefiles/runtime/privacy.mk", runtime_entry_text)
        self.assertIn(
            "include makefiles/runtime/core/interactive.mk",
            runtime_core_entry_text,
        )
        self.assertIn(
            "include makefiles/runtime/core/lifecycle.mk",
            runtime_core_entry_text,
        )
        self.assertIn("include makefiles/runtime/core/git.mk", runtime_core_entry_text)
        self.assertIn(
            "include makefiles/runtime/core/status.mk",
            runtime_core_entry_text,
        )
        self.assertIsNone(
            re.search(
                r"(?m)^\.PHONY:|^[-a-zA-Z0-9_]+:",
                runtime_local_urls_entry_text,
            )
        )
        self.assertIn(
            "include makefiles/runtime/local-urls/docs.mk",
            runtime_local_urls_entry_text,
        )
        self.assertIn(
            "include makefiles/runtime/local-urls/viz.mk",
            runtime_local_urls_entry_text,
        )
        self.assertIn("chat:", contract_text)
        self.assertIn("start:", contract_text)
        self.assertIn("server-daemon:", contract_text)
        self.assertIn("docs: server-daemon", contract_text)
        self.assertIn("openai-account-summary:", contract_text)
        self.assertIn("caffeinate:", contract_text)
        self.assertIn("privacy-local-on:", contract_text)

    def test_eval_config_is_extracted_through_role_includes(self) -> None:
        config_evals_entry_text = MAKE_CONFIG_EVALS.read_text(encoding="utf-8")
        gates_entry_text = MAKE_CONFIG_EVALS_GATES.read_text(encoding="utf-8")
        gates_runner_entry_text = MAKE_CONFIG_EVALS_GATES_RUNNER.read_text(
            encoding="utf-8"
        )
        ocr_cases_entry_text = MAKE_CONFIG_EVALS_OCR_CASES.read_text(encoding="utf-8")
        ocr_cases_intake_workflow_entry_text = (
            MAKE_CONFIG_EVALS_OCR_CASES_INTAKE_WORKFLOW.read_text(encoding="utf-8")
        )
        sidecar_entry_text = MAKE_CONFIG_EVALS_SIDECAR.read_text(encoding="utf-8")
        ocr_runs_entry_text = MAKE_CONFIG_EVALS_OCR_RUNS.read_text(encoding="utf-8")
        ocr_runs_focus_entry_text = MAKE_CONFIG_EVALS_OCR_RUNS_FOCUS.read_text(
            encoding="utf-8"
        )
        ocr_runs_direct_runners_entry_text = (
            MAKE_CONFIG_EVALS_OCR_RUNS_DIRECT_RUNNERS.read_text(encoding="utf-8")
        )
        ocr_runs_transcript_lanes_entry_text = (
            MAKE_CONFIG_EVALS_OCR_RUNS_TRANSCRIPT_LANES.read_text(encoding="utf-8")
        )
        ocr_runs_transcript_lanes_lane_workflow_entry_text = (
            MAKE_CONFIG_EVALS_OCR_RUNS_TRANSCRIPT_LANES_LANE_WORKFLOW.read_text(
                encoding="utf-8"
            )
        )
        ocr_runs_growth_entry_text = MAKE_CONFIG_EVALS_OCR_RUNS_GROWTH.read_text(
            encoding="utf-8"
        )
        ocr_runs_growth_stability_workflow_entry_text = (
            MAKE_CONFIG_EVALS_OCR_RUNS_GROWTH_STABILITY_WORKFLOW.read_text(
                encoding="utf-8"
            )
        )
        ocr_runs_growth_case_workflow_entry_text = (
            MAKE_CONFIG_EVALS_OCR_RUNS_GROWTH_CASE_WORKFLOW.read_text(encoding="utf-8")
        )
        ocr_runs_defaults_entry_text = MAKE_CONFIG_EVALS_OCR_RUNS_DEFAULTS.read_text(
            encoding="utf-8"
        )
        reports_entry_text = MAKE_CONFIG_EVALS_REPORTS.read_text(encoding="utf-8")
        reports_ocr_builder_entry_text = (
            MAKE_CONFIG_EVALS_REPORTS_OCR_BUILDER.read_text(encoding="utf-8")
        )
        config_text = _makefile_contract_text()

        self.assertIsNone(
            re.search(
                r"(?m)^[A-Z][A-Z0-9_]*\s*(?:\?=|:=|=)",
                config_evals_entry_text,
            )
        )
        self.assertIsNone(
            re.search(
                r"(?m)^[A-Z][A-Z0-9_]*\s*(?:\?=|:=|=)",
                gates_entry_text,
            )
        )
        self.assertIsNone(
            re.search(
                r"(?m)^[A-Z][A-Z0-9_]*\s*(?:\?=|:=|=)",
                ocr_cases_entry_text,
            )
        )
        self.assertIsNone(
            re.search(
                r"(?m)^[A-Z][A-Z0-9_]*\s*(?:\?=|:=|=)",
                ocr_runs_entry_text,
            )
        )
        self.assertIsNone(
            re.search(
                r"(?m)^[A-Z][A-Z0-9_]*\s*(?:\?=|:=|=)",
                ocr_runs_transcript_lanes_entry_text,
            )
        )
        self.assertIsNone(
            re.search(
                r"(?m)^[A-Z][A-Z0-9_]*\s*(?:\?=|:=|=)",
                ocr_runs_growth_entry_text,
            )
        )
        self.assertIsNone(
            re.search(
                r"(?m)^[A-Z][A-Z0-9_]*\s*(?:\?=|:=|=)",
                reports_entry_text,
            )
        )
        self.assertIn(
            "include makefiles/config/evals/gates.mk",
            config_evals_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-cases.mk",
            config_evals_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/sidecar.mk",
            config_evals_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs.mk",
            config_evals_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/reports.mk",
            config_evals_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/gates/server.mk",
            gates_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/gates/smoke.mk",
            gates_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/gates/hallucination.mk",
            gates_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/gates/suites.mk",
            gates_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/gates/runner.mk",
            gates_entry_text,
        )
        self.assertIsNone(
            re.search(
                r"(?m)^[A-Z][A-Z0-9_]*\s*(?:\?=|:=|=|\+=)",
                gates_runner_entry_text,
            )
        )
        self.assertIn(
            "include makefiles/config/evals/gates/runner/base.mk",
            gates_runner_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/gates/runner/smoke.mk",
            gates_runner_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/gates/runner/gate.mk",
            gates_runner_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/gates/runner/retrieval-ocr.mk",
            gates_runner_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/gates/runner/behaviour.mk",
            gates_runner_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-cases/source-paths.mk",
            ocr_cases_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-cases/export.mk",
            ocr_cases_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-cases/transcript-paths.mk",
            ocr_cases_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-cases/review.mk",
            ocr_cases_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-cases/benchmarks.mk",
            ocr_cases_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-cases/intake-workflow.mk",
            ocr_cases_entry_text,
        )
        self.assertIsNone(
            re.search(
                r"(?m)^[A-Z][A-Z0-9_]*\s*(?:\?=|:=|=|\+=)",
                ocr_cases_intake_workflow_entry_text,
            )
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-cases/intake-workflow/base.mk",
            ocr_cases_intake_workflow_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-cases/intake-workflow/export.mk",
            ocr_cases_intake_workflow_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-cases/intake-workflow/transcript-cases.mk",
            ocr_cases_intake_workflow_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-cases/intake-workflow/transcript-review.mk",
            ocr_cases_intake_workflow_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-cases/intake-workflow/generalization.mk",
            ocr_cases_intake_workflow_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-cases/intake-workflow/growth.mk",
            ocr_cases_intake_workflow_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-cases/intake-workflow/benchmarks.mk",
            ocr_cases_intake_workflow_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/defaults.mk",
            ocr_runs_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/defaults/stability.mk",
            ocr_runs_defaults_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/defaults/growth.mk",
            ocr_runs_defaults_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/defaults/focus.mk",
            ocr_runs_defaults_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/defaults/growth-batches.mk",
            ocr_runs_defaults_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/defaults/benchmarks.mk",
            ocr_runs_defaults_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/common.mk",
            ocr_runs_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/direct-runners.mk",
            ocr_runs_entry_text,
        )
        self.assertIsNone(
            re.search(
                r"(?m)^[A-Z][A-Z0-9_]*\s*(?:\?=|:=|=|\+=)",
                ocr_runs_direct_runners_entry_text,
            )
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/direct-runners/handwriting.mk",
            ocr_runs_direct_runners_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/direct-runners/cases.mk",
            ocr_runs_direct_runners_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/direct-runners/stability.mk",
            ocr_runs_direct_runners_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/transcript-lanes.mk",
            ocr_runs_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/transcript-lanes/base.mk",
            ocr_runs_transcript_lanes_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/transcript-lanes/lane-workflow.mk",
            ocr_runs_transcript_lanes_entry_text,
        )
        self.assertIsNone(
            re.search(
                r"(?m)^[A-Z][A-Z0-9_]*\s*(?:\?=|:=|=|\+=)",
                ocr_runs_transcript_lanes_lane_workflow_entry_text,
            )
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/transcript-lanes/lane-workflow/base.mk",
            ocr_runs_transcript_lanes_lane_workflow_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/transcript-lanes/lane-workflow/cases.mk",
            ocr_runs_transcript_lanes_lane_workflow_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/transcript-lanes/lane-workflow/eval-runtime.mk",
            ocr_runs_transcript_lanes_lane_workflow_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/transcript-lanes/lane-workflow/stability.mk",
            ocr_runs_transcript_lanes_lane_workflow_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/transcript-lanes/lane-workflow/reports.mk",
            ocr_runs_transcript_lanes_lane_workflow_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/transcript-lanes/lane-workflow/env.mk",
            ocr_runs_transcript_lanes_lane_workflow_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/focus.mk",
            ocr_runs_entry_text,
        )
        self.assertIsNone(
            re.search(
                r"(?m)^[A-Z][A-Z0-9_]*\s*(?:\?=|:=|=|\+=)",
                ocr_runs_focus_entry_text,
            )
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/focus/scripts.mk",
            ocr_runs_focus_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/focus/runtime.mk",
            ocr_runs_focus_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/focus/runners.mk",
            ocr_runs_focus_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/focus/eval-guards.mk",
            ocr_runs_focus_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/focus/cases.mk",
            ocr_runs_focus_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/focus/run-controls.mk",
            ocr_runs_focus_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/focus/reports.mk",
            ocr_runs_focus_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/focus/backoff.mk",
            ocr_runs_focus_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/focus/fail-cohort.mk",
            ocr_runs_focus_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/focus/env.mk",
            ocr_runs_focus_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/growth.mk",
            ocr_runs_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/growth/stability-workflow.mk",
            ocr_runs_growth_entry_text,
        )
        self.assertIsNone(
            re.search(
                r"(?m)^[A-Z][A-Z0-9_]*\s*(?:\?=|:=|=|\+=)",
                ocr_runs_growth_stability_workflow_entry_text,
            )
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/growth/stability-workflow/scripts.mk",
            ocr_runs_growth_stability_workflow_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/growth/stability-workflow/runtime.mk",
            ocr_runs_growth_stability_workflow_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/growth/stability-workflow/runners.mk",
            ocr_runs_growth_stability_workflow_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/growth/stability-workflow/cases.mk",
            ocr_runs_growth_stability_workflow_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/growth/stability-workflow/run-controls.mk",
            ocr_runs_growth_stability_workflow_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/growth/stability-workflow/reports.mk",
            ocr_runs_growth_stability_workflow_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/growth/stability-workflow/env.mk",
            ocr_runs_growth_stability_workflow_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/growth/case-workflow.mk",
            ocr_runs_growth_entry_text,
        )
        self.assertIsNone(
            re.search(
                r"(?m)^[A-Z][A-Z0-9_]*\s*(?:\?=|:=|=|\+=)",
                ocr_runs_growth_case_workflow_entry_text,
            )
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/growth/case-workflow/scripts.mk",
            ocr_runs_growth_case_workflow_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/growth/case-workflow/runtime.mk",
            ocr_runs_growth_case_workflow_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/growth/case-workflow/runners.mk",
            ocr_runs_growth_case_workflow_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/growth/case-workflow/cases.mk",
            ocr_runs_growth_case_workflow_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/growth/case-workflow/batches.mk",
            ocr_runs_growth_case_workflow_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/growth/case-workflow/reports.mk",
            ocr_runs_growth_case_workflow_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/ocr-runs/growth/case-workflow/env.mk",
            ocr_runs_growth_case_workflow_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/reports/runner.mk",
            reports_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/reports/parallel-runner.mk",
            reports_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/reports/ocr-builder.mk",
            reports_entry_text,
        )
        self.assertIsNone(
            re.search(
                r"(?m)^[A-Z][A-Z0-9_]*\s*(?:\?=|:=|=|\+=)",
                reports_ocr_builder_entry_text,
            )
        )
        self.assertIn(
            "include makefiles/config/evals/reports/ocr-builder/base.mk",
            reports_ocr_builder_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/reports/ocr-builder/growth-metrics.mk",
            reports_ocr_builder_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/reports/ocr-builder/growth-fail-cohort.mk",
            reports_ocr_builder_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/reports/ocr-builder/focus-cases.mk",
            reports_ocr_builder_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/reports/ocr-builder/focus-fail-patterns.mk",
            reports_ocr_builder_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/reports/ocr-workflow.mk",
            reports_entry_text,
        )
        self.assertIn(
            "include makefiles/config/evals/reports/lane-inventory.mk",
            reports_entry_text,
        )
        self.assertIn(
            "EVAL_SIDECAR_REPO_SLUG ?= $(notdir $(CURDIR))",
            sidecar_entry_text,
        )
        self.assertIn(
            "EVAL_SIDECAR_RUNTIME_ROOT ?= /tmp/polinko-runtime",
            sidecar_entry_text,
        )
        self.assertIn(
            (
                "EVAL_SIDECAR_STATE_DIR ?= "
                "$(EVAL_SIDECAR_RUNTIME_ROOT)/$(EVAL_SIDECAR_REPO_SLUG)"
            ),
            sidecar_entry_text,
        )
        self.assertIn(
            "EVAL_SIDECAR_PID_FILE ?= $(EVAL_SIDECAR_STATE_DIR)/eval-sidecar.pid",
            sidecar_entry_text,
        )
        self.assertIn(
            "EVAL_SIDECAR_LOG ?= $(EVAL_SIDECAR_STATE_DIR)/eval-sidecar.log",
            sidecar_entry_text,
        )
        self.assertIn(
            'EVAL_SIDECAR_REPO_SLUG="$(EVAL_SIDECAR_REPO_SLUG)"',
            sidecar_entry_text,
        )
        self.assertIn(
            'EVAL_SIDECAR_RUNTIME_ROOT="$(EVAL_SIDECAR_RUNTIME_ROOT)"',
            sidecar_entry_text,
        )
        self.assertIn(
            'EVAL_SIDECAR_STATE_DIR="$(EVAL_SIDECAR_STATE_DIR)"',
            sidecar_entry_text,
        )
        self.assertNotIn("/tmp/polinko-eval-sidecar.pid", sidecar_entry_text)
        self.assertNotIn("/tmp/polinko-eval-sidecar.log", sidecar_entry_text)
        self.assertIn("LOCAL_EVAL_GATE_RUNNER_ENV =", config_text)
        self.assertIn("OCR_INTAKE_WORKFLOW_ENV =", config_text)
        self.assertIn("EVAL_SIDECAR_START_ENV =", config_text)
        self.assertIn("OCR_BASE_TRANSCRIPT_WORKFLOW_ENV =", config_text)
        self.assertIn("OCR_GROWTH_CASE_WORKFLOW_ENV =", config_text)
        self.assertIn("OCR_REPORT_WORKFLOW_ENV =", config_text)

    def test_ops_targets_are_extracted_through_tool_includes(self) -> None:
        ops_entry_text = MAKE_OPS.read_text(encoding="utf-8")
        contract_text = _makefile_contract_text()

        self.assertNotRegex(
            ops_entry_text,
            r"(?m)^(?:\.PHONY|[A-Za-z0-9_.-]+(?:\s+[A-Za-z0-9_.-]+)*:)",
        )
        self.assertIn("include makefiles/ops/k6.mk", ops_entry_text)
        self.assertIn("include makefiles/ops/trivy.mk", ops_entry_text)
        self.assertIn("include makefiles/ops/docker.mk", ops_entry_text)
        self.assertIn("k6-chat-smoke:", contract_text)
        self.assertIn("trivy-fs:", contract_text)
        self.assertIn("trivy-image:", contract_text)
        self.assertIn("docker-build:", contract_text)
        self.assertIn("docker-run:", contract_text)
        self.assertIn(
            "@$(call repo_activity,make k6-chat-smoke,k6-chat-smoke)",
            contract_text,
        )
        self.assertIn("@$(call repo_activity,make trivy-fs,trivy-fs)", contract_text)
        self.assertIn(
            "@$(call repo_activity,make trivy-image,trivy-image)",
            contract_text,
        )
        self.assertIn(
            "@$(call repo_activity,make docker-build,docker-build)",
            contract_text,
        )
        self.assertIn(
            "@$(call repo_activity,make docker-run,docker-run)", contract_text
        )
        self.assertIn(
            '$(PYTHON) -m tools.require_command --command "$(K6)" --label "k6 helper"',
            contract_text,
        )
        self.assertIn(
            '$(PYTHON) -m tools.require_command --command "$(TRIVY)" --label "trivy helper"',
            contract_text,
        )
        self.assertIn(
            '$(PYTHON) -m tools.require_command --command "$(DOCKER)" --label "trivy helper"',
            contract_text,
        )
        self.assertIn(
            '$(PYTHON) -m tools.require_command --command "$(DOCKER)" --label "docker helper"',
            contract_text,
        )
        self.assertNotIn('command -v "$(DOCKER)"', contract_text)
        self.assertNotIn('command -v "$(K6)"', contract_text)
        self.assertNotIn('command -v "$(TRIVY)"', contract_text)
        self.assertIn("$(K6) run tests/perf/chat_smoke.js", contract_text)
        self.assertIn('$(TRIVY) fs --severity "$(TRIVY_SEVERITY)"', contract_text)
        self.assertIn('$(TRIVY) image --severity "$(TRIVY_SEVERITY)"', contract_text)

    def test_surface_targets_are_extracted_through_role_includes(self) -> None:
        config_surfaces_entry_text = MAKE_CONFIG_SURFACES.read_text(encoding="utf-8")
        config_manual_evals_entry_text = MAKE_CONFIG_SURFACES_MANUAL_EVALS.read_text(
            encoding="utf-8"
        )
        config_manual_evals_ocr_retry_entry_text = (
            MAKE_CONFIG_SURFACES_MANUAL_EVALS_OCR_RETRY.read_text(encoding="utf-8")
        )
        surfaces_entry_text = MAKE_SURFACES.read_text(encoding="utf-8")
        manual_evals_entry_text = MAKE_SURFACES_MANUAL_EVALS.read_text(encoding="utf-8")
        manual_evals_feedback_entry_text = (
            MAKE_SURFACES_MANUAL_EVALS_FEEDBACK.read_text(encoding="utf-8")
        )
        manual_evals_ocr_retry_entry_text = (
            MAKE_SURFACES_MANUAL_EVALS_OCR_RETRY.read_text(encoding="utf-8")
        )
        contract_text = _makefile_contract_text()

        self.assertIn(
            "include makefiles/config/surfaces/notebooks.mk",
            config_surfaces_entry_text,
        )
        self.assertIn(
            "include makefiles/config/surfaces/manual-evals.mk",
            config_surfaces_entry_text,
        )
        self.assertIn(
            "include makefiles/config/surfaces/local-browser.mk",
            config_surfaces_entry_text,
        )
        self.assertNotIn(
            "include makefiles/config/surfaces/portfolio.mk",
            config_surfaces_entry_text,
        )
        self.assertIn(
            "include makefiles/config/surfaces/manual-evals/common.mk",
            config_manual_evals_entry_text,
        )
        self.assertIn(
            "include makefiles/config/surfaces/manual-evals/feedback.mk",
            config_manual_evals_entry_text,
        )
        self.assertIn(
            "include makefiles/config/surfaces/manual-evals/overlays.mk",
            config_manual_evals_entry_text,
        )
        self.assertIn(
            "include makefiles/config/surfaces/manual-evals/ocr-retry.mk",
            config_manual_evals_entry_text,
        )
        self.assertIsNone(
            re.search(
                r"(?m)^[A-Z][A-Z0-9_]*\s*(?:\?=|:=|=|\+=)",
                config_manual_evals_ocr_retry_entry_text,
            )
        )
        self.assertIn(
            "include makefiles/config/surfaces/manual-evals/ocr-retry/base.mk",
            config_manual_evals_ocr_retry_entry_text,
        )
        self.assertIn(
            "include makefiles/config/surfaces/manual-evals/ocr-retry/selection.mk",
            config_manual_evals_ocr_retry_entry_text,
        )
        self.assertIn(
            "include makefiles/config/surfaces/manual-evals/ocr-retry/execution.mk",
            config_manual_evals_ocr_retry_entry_text,
        )
        self.assertIn(
            "include makefiles/config/surfaces/manual-evals/ocr-retry/feedback-closure.mk",
            config_manual_evals_ocr_retry_entry_text,
        )
        self.assertIn("include makefiles/surfaces/notebooks.mk", surfaces_entry_text)
        self.assertIn("include makefiles/surfaces/manual-evals.mk", surfaces_entry_text)
        self.assertNotIn("include makefiles/surfaces/portfolio.mk", surfaces_entry_text)
        self.assertIn(
            "include makefiles/surfaces/local-browser.mk", surfaces_entry_text
        )
        self.assertIn(
            "include makefiles/surfaces/manual-evals/common.mk",
            manual_evals_entry_text,
        )
        self.assertIn(
            "include makefiles/surfaces/manual-evals/database.mk",
            manual_evals_entry_text,
        )
        self.assertIn(
            "include makefiles/surfaces/manual-evals/feedback.mk",
            manual_evals_entry_text,
        )
        self.assertNotRegex(
            manual_evals_feedback_entry_text,
            r"(?m)^(?:\.PHONY|[A-Za-z0-9_.-]+(?:\s+[A-Za-z0-9_.-]+)*:)",
        )
        self.assertIn(
            "include makefiles/surfaces/manual-evals/feedback/review.mk",
            manual_evals_feedback_entry_text,
        )
        self.assertIn(
            "include makefiles/surfaces/manual-evals/feedback/decisions.mk",
            manual_evals_feedback_entry_text,
        )
        self.assertIn(
            "include makefiles/surfaces/manual-evals/feedback/reclassify.mk",
            manual_evals_feedback_entry_text,
        )
        self.assertIn(
            "include makefiles/surfaces/manual-evals/overlays.mk",
            manual_evals_entry_text,
        )
        self.assertIn(
            "include makefiles/surfaces/manual-evals/ocr-retry.mk",
            manual_evals_entry_text,
        )
        self.assertIn(
            "include makefiles/surfaces/manual-evals/ocr-retry/packets.mk",
            manual_evals_ocr_retry_entry_text,
        )
        self.assertIn(
            "include makefiles/surfaces/manual-evals/ocr-retry/selection.mk",
            manual_evals_ocr_retry_entry_text,
        )
        self.assertIn(
            "include makefiles/surfaces/manual-evals/ocr-retry/execution.mk",
            manual_evals_ocr_retry_entry_text,
        )
        self.assertIn(
            "include makefiles/surfaces/manual-evals/ocr-retry/feedback-closure.mk",
            manual_evals_ocr_retry_entry_text,
        )
        self.assertIn("notebook nb notes:", contract_text)
        notebooks_text = MAKE_SURFACES_NOTEBOOKS.read_text(encoding="utf-8")
        self.assertIn(
            "@$(call repo_activity,make notebook-setup,notebook-setup)",
            notebooks_text,
        )
        self.assertIn("@$(call repo_activity,make $@,$@)", notebooks_text)
        self.assertIn(
            "notebook helper: missing requirements file: requirements.notebook.txt",
            notebooks_text,
        )
        self.assertIn(
            "notebook helper: missing Python module: jupyter (run make notebook-setup)",
            notebooks_text,
        )
        self.assertIn("manual-evals-ocr-retry-execute", contract_text)
        self.assertNotIn("portfolio-install:", contract_text)
        self.assertNotIn("portfolio-build:", contract_text)
        self.assertNotIn("portfolio-open:", contract_text)
        self.assertNotIn("portfolio-mockups:", contract_text)
        local_browser_text = MAKE_SURFACES_LOCAL_BROWSER.read_text(encoding="utf-8")
        self.assertIn("pwcli playwright-cli:", contract_text)
        self.assertIn(
            "@$(call repo_activity,make $@,$@)",
            local_browser_text,
        )
        self.assertIn(
            "@$(call repo_activity,make playwright-snapshot-dir,playwright-snapshot-dir)",
            local_browser_text,
        )
        self.assertIn(
            "local browser helper: missing executable: $(PWCLI_TOOL)",
            local_browser_text,
        )
        pwcli_daily_text = PWCLI_DAILY_SCRIPT.read_text(encoding="utf-8")
        self.assertIn('. "$script_dir/process_lifecycle_common.sh"', pwcli_daily_text)
        self.assertIn(
            'polinko_require_labeled_command "npx" "npx" "pwcli-daily"',
            pwcli_daily_text,
        )
        self.assertNotIn("command -v npx", pwcli_daily_text)
        self.assertIn("PLAYWRIGHT_SNAPSHOT_STAMP ?=", contract_text)
        self.assertIn(
            'PLAYWRIGHT_SNAPSHOT_STAMP="$(PLAYWRIGHT_SNAPSHOT_STAMP)"',
            contract_text,
        )

    def test_shared_config_is_extracted_before_target_families(self) -> None:
        root_text = _makefile_text()
        config_entry_text = MAKE_CONFIG.read_text(encoding="utf-8")
        config_ops_entry_text = MAKE_CONFIG_OPS.read_text(encoding="utf-8")
        config_ops_github_text = MAKE_CONFIG_OPS_GITHUB.read_text(encoding="utf-8")
        config_ops_k6_text = MAKE_CONFIG_OPS_K6.read_text(encoding="utf-8")
        config_ops_trivy_text = MAKE_CONFIG_OPS_TRIVY.read_text(encoding="utf-8")
        runtime_config_entry_text = MAKE_CONFIG_RUNTIME.read_text(encoding="utf-8")
        runtime_openai_account_entry_text = (
            MAKE_CONFIG_RUNTIME_OPENAI_ACCOUNT.read_text(encoding="utf-8")
        )
        runtime_caffeinate_entry_text = MAKE_CONFIG_RUNTIME_CAFFEINATE.read_text(
            encoding="utf-8"
        )
        reports_runner_entry_text = MAKE_CONFIG_EVALS_REPORTS_RUNNER.read_text(
            encoding="utf-8"
        )
        reports_parallel_runner_entry_text = (
            MAKE_CONFIG_EVALS_REPORTS_PARALLEL_RUNNER.read_text(encoding="utf-8")
        )
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
        self.assertIsNone(
            re.search(
                r"(?m)^[A-Z][A-Z0-9_]*\s*(?:\?=|:=|=|\+=)",
                config_ops_entry_text,
            )
        )
        self.assertIn("include makefiles/config/ops/act.mk", config_ops_entry_text)
        self.assertIn("include makefiles/config/ops/docker.mk", config_ops_entry_text)
        self.assertIn("include makefiles/config/ops/github.mk", config_ops_entry_text)
        self.assertIn("include makefiles/config/ops/k6.mk", config_ops_entry_text)
        self.assertIn("include makefiles/config/ops/trivy.mk", config_ops_entry_text)
        self.assertIn("GH ?= gh", config_ops_github_text)
        self.assertIn("GITHUB_HEALTH_REPO ?=", config_ops_github_text)
        self.assertIn("GITHUB_HEALTH_RUN_LIMIT ?= 20", config_ops_github_text)
        self.assertIn("GITHUB_HEALTH_PR_LIMIT ?= 20", config_ops_github_text)
        self.assertIn("K6 ?= k6", config_ops_k6_text)
        self.assertIn("TRIVY ?= trivy", config_ops_trivy_text)
        self.assertIn(
            "include makefiles/config/runtime/core.mk", runtime_config_entry_text
        )
        self.assertIn(
            "include makefiles/config/runtime/local-urls.mk",
            runtime_config_entry_text,
        )
        self.assertIn(
            "include makefiles/config/runtime/openai-account.mk",
            runtime_config_entry_text,
        )
        self.assertIn(
            "include makefiles/config/runtime/caffeinate.mk",
            runtime_config_entry_text,
        )
        self.assertIn(
            "include makefiles/config/runtime/server.mk", runtime_config_entry_text
        )
        self.assertIsNone(
            re.search(
                r"(?m)^[A-Z][A-Z0-9_]*\s*(?:\?=|:=|=|\+=)",
                runtime_openai_account_entry_text,
            )
        )
        self.assertIn(
            "include makefiles/config/runtime/openai-account/base.mk",
            runtime_openai_account_entry_text,
        )
        self.assertIn(
            "include makefiles/config/runtime/openai-account/costs.mk",
            runtime_openai_account_entry_text,
        )
        self.assertIn(
            "include makefiles/config/runtime/openai-account/usage.mk",
            runtime_openai_account_entry_text,
        )
        self.assertIn(
            "include makefiles/config/runtime/openai-account/limits.mk",
            runtime_openai_account_entry_text,
        )
        self.assertIn(
            "include makefiles/config/runtime/openai-account/env.mk",
            runtime_openai_account_entry_text,
        )
        self.assertIsNone(
            re.search(
                r"(?m)^[A-Za-z_][A-Za-z0-9_]*\s*(?:\?=|:=|=|\+=)",
                runtime_caffeinate_entry_text,
            )
        )
        self.assertIn(
            "include makefiles/config/runtime/caffeinate/state.mk",
            runtime_caffeinate_entry_text,
        )
        self.assertIn(
            "include makefiles/config/runtime/caffeinate/repo.mk",
            runtime_caffeinate_entry_text,
        )
        self.assertIn(
            "include makefiles/config/runtime/caffeinate/command.mk",
            runtime_caffeinate_entry_text,
        )
        self.assertIn(
            "include makefiles/config/runtime/caffeinate/runner.mk",
            runtime_caffeinate_entry_text,
        )
        self.assertIn(
            "include makefiles/config/runtime/caffeinate/env.mk",
            runtime_caffeinate_entry_text,
        )
        self.assertIn("PYTHON ?=", config_text)
        self.assertIn(
            'PYTHON ?= $(shell VENV="$(VENV)" . ./tools/python_runtime.sh; '
            "polinko_default_python_bin)",
            config_text,
        )
        self.assertIn("ACT ?= act", config_text)
        self.assertIn("CLI_ENTRYPOINT ?= -m polinko.cli", config_text)
        self.assertIn("ASGI_APP ?= server:app", config_text)
        self.assertIn("LOCAL_BROWSER_LAUNCH ?= none", config_text)
        self.assertIn(
            "LOCAL_URL_LAUNCHER_SCRIPT ?= ./tools/open_local_url.sh", config_text
        )
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
        self.assertNotIn("PORTFOLIO_APP_DIR", config_text)
        self.assertNotIn("PORTFOLIO_STATIC_DIR", config_text)
        self.assertNotIn("FRONTEND_DIR", config_text)
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
            'OCR_WORKFLOW_COMMON_SCRIPT="$(OCR_WORKFLOW_COMMON_SCRIPT)"',
            config_text,
        )
        self.assertIn('EVAL_CASE_GUARD_SCRIPT="$(EVAL_CASE_GUARD_SCRIPT)"', config_text)
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
            'EVAL_SERVER_DAEMON_SCRIPT="$(EVAL_SERVER_DAEMON_SCRIPT)"',
            reports_runner_entry_text,
        )
        self.assertIn(
            "EVAL_REPORTS_PARALLEL_RUNNER_SCRIPT ?= ./tools/run_eval_reports_parallel.sh",
            config_text,
        )
        self.assertIn("EVAL_REPORTS_PARALLEL_RUNNER_ENV =", config_text)
        self.assertIn(
            'EVAL_SERVER_DAEMON_SCRIPT="$(EVAL_SERVER_DAEMON_SCRIPT)"',
            reports_parallel_runner_entry_text,
        )
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
        self.assertIn("LOCAL_EVAL_GATE_TEMP_ROOT ?= /tmp", config_text)
        self.assertIn(
            'LOCAL_EVAL_GATE_TEMP_ROOT="$(LOCAL_EVAL_GATE_TEMP_ROOT)"',
            config_text,
        )
        self.assertIn(
            (
                "GATE_SESSION_DB ?= "
                "$(LOCAL_EVAL_GATE_TEMP_ROOT)/polinko-quality-gate-sessions.db"
            ),
            config_text,
        )
        self.assertIn(
            (
                "GATE_VECTOR_DB ?= "
                "$(LOCAL_EVAL_GATE_TEMP_ROOT)/polinko-quality-gate-vector.db"
            ),
            config_text,
        )
        self.assertIn("LOCAL_EVAL_GATE_START_ATTEMPTS ?= 100", config_text)
        self.assertIn("LOCAL_EVAL_GATE_START_SLEEP_SECONDS ?= 0.2", config_text)
        self.assertIn("LOCAL_EVAL_GATE_RUNNER_ENV =", config_text)
        self.assertIn(
            'LOCAL_EVAL_GATE_START_ATTEMPTS="$(LOCAL_EVAL_GATE_START_ATTEMPTS)"',
            config_text,
        )
        self.assertIn(
            'LOCAL_EVAL_GATE_START_SLEEP_SECONDS="$(LOCAL_EVAL_GATE_START_SLEEP_SECONDS)"',
            config_text,
        )
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
            'EVAL_SERVER_DAEMON_SCRIPT="$(EVAL_SERVER_DAEMON_SCRIPT)"',
            config_text,
        )
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

    def test_doctor_env_passes_interpreter_source_to_python_doctor(self) -> None:
        text = _makefile_contract_text()

        self.assertRegex(text, r"(?m)^doctor-env:$")
        self.assertIn(
            '$(PYTHON) -m tools.run_doctor_env --python "$(PYTHON)"',
            text,
        )
        self.assertIn('--python-origin "$(origin PYTHON)"', text)
        self.assertNotIn("POLINKO_DOCTOR_INTERPRETER_SOURCE", text)
        self.assertNotIn("doctor_env_interpreter_source", text)

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

    def test_venv_entrypoint_delegates_to_helper(self) -> None:
        text = _makefile_contract_text()
        script = OPEN_VENV_SHELL_SCRIPT.read_text(encoding="utf-8")

        self.assertRegex(text, r"(?m)^venv:$")
        self.assertIn("@$(call repo_activity,make $@,$@)", text)
        self.assertIn("bash ./tools/open_venv_shell.sh", text)
        self.assertNotIn('exec "$$SHELL" -i', text)
        self.assertIn('activate_path="./.venv/bin/activate"', script)
        self.assertIn(
            "No local activation script found (checked $activate_path).", script
        )
        self.assertIn(
            'echo "Opening shell with virtual environment: $activate_path"', script
        )
        self.assertIn('. "$activate_path"', script)
        self.assertIn('exec "$SHELL" -i', script)

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
        self.assertIn("manual-evals-db-refresh", targets)
        self.assertIn("manual-evals-db-status", targets)
        self.assertIn("manual-evals-db-health", targets)
        self.assertIn("manual-evals-feedback-actionables", targets)
        self.assertIn("manual-evals-feedback-cohorts", targets)
        self.assertIn("manual-evals-feedback-source-context", targets)
        self.assertIn("manual-evals-feedback-decision-draft", targets)
        self.assertIn("manual-evals-feedback-decision-preview", targets)
        self.assertIn("manual-evals-overlay-comparison-readiness", targets)
        self.assertIn("manual-evals-overlay-source-index-draft", targets)
        self.assertIn("manual-evals-overlay-source-index-validate", targets)
        self.assertIn("manual-evals-ocr-retry-candidates", targets)
        self.assertIn("manual-evals-ocr-retry-source-verification", targets)
        self.assertIn("manual-evals-ocr-retry-source-provenance", targets)
        self.assertIn("manual-evals-ocr-retry-input-packet", targets)
        self.assertIn("manual-evals-ocr-retry-rerun-manifest", targets)
        self.assertIn("manual-evals-ocr-retry-rerun-plan", targets)
        self.assertIn("manual-evals-ocr-retry-selection-review", targets)
        self.assertIn("manual-evals-ocr-retry-selection-template", targets)
        self.assertIn("manual-evals-ocr-retry-selection-validate", targets)
        self.assertIn("manual-evals-ocr-retry-selection-apply-preview", targets)
        self.assertIn("manual-evals-ocr-retry-execution-readiness", targets)
        self.assertIn("manual-evals-ocr-retry-execute", targets)
        self.assertIn("manual-evals-ocr-retry-execution-report", targets)
        self.assertIn("manual-evals-ocr-retry-feedback-closure-preview", targets)
        self.assertIn("manual-evals-ocr-retry-feedback-closure-apply", targets)
        self.assertIn("manual-evals-ocr-retry-feedback-closure-apply-report", targets)
        self.assertIn("manual-evals-no-context-reclassify-preview", targets)
        self.assertIn("manual-evals-no-context-reclassify-apply", targets)
        self.assertIn("manual-evals-feedback-reclassify-preview", targets)
        self.assertIn("manual-evals-feedback-reclassify-apply", targets)
        self.assertFalse(any(target.startswith("manualdb") for target in targets))
        self.assertNotIn("portfolio", targets)
        self.assertNotIn("portfolio-mockups", targets)
        self.assertNotIn("portfolio-mockups-status", targets)
        self.assertIn("pwcli", targets)
        self.assertIn("repo-search", targets)
        self.assertIn("repo-search-full", targets)

    def test_pycheck_uses_configured_python_interpreter(self) -> None:
        result = subprocess.run(
            [
                "make",
                "-n",
                "pycheck",
                "FILES=tools/check_shell_scripts.py",
                "PYTHON=/tmp/polinko-python",
            ],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn(
            "/tmp/polinko-python -m tools.validate_make_variable",
            result.stdout,
        )
        self.assertIn(
            "/tmp/polinko-python -m py_compile tools/check_shell_scripts.py",
            result.stdout,
        )
        self.assertIn(
            'CAFFEINATE_ACTIVITY_LABEL="make pycheck"',
            result.stdout,
        )
        self.assertNotIn("python3 -m py_compile", result.stdout)

    def test_simple_make_argument_validation_delegates_to_helper(self) -> None:
        text = _makefile_contract_text()

        self.assertNotIn('if [ -z "$(TEST)" ]', text)
        self.assertNotIn('if [ -z "$(TESTS)" ]', text)
        self.assertNotIn('if [ -z "$(FILES)" ]', text)
        self.assertIn(
            '@$(PYTHON) -m tools.validate_make_variable --value "$(TEST)"',
            text,
        )
        self.assertIn(
            '@$(PYTHON) -m tools.validate_make_variable --value "$(TESTS)"',
            text,
        )
        self.assertIn(
            '@$(PYTHON) -m tools.validate_make_variable --value "$(FILES)"',
            text,
        )

    def test_repo_search_targets_keep_routine_and_full_modes_explicit(self) -> None:
        text = _makefile_contract_text()

        self.assertRegex(text, r"(?m)^repo-search:$")
        self.assertRegex(text, r"(?m)^repo-search-full:$")
        self.assertNotIn('if [ -z "$(Q)" ]', text)
        self.assertIn(
            '@$(PYTHON) -m tools.repo_search --check-query --make-target repo-search --query "$(Q)"',
            text,
        )
        self.assertIn(
            '@$(PYTHON) -m tools.repo_search --check-query --make-target repo-search-full --query "$(Q)"',
            text,
        )
        self.assertIn("@$(call repo_activity,make repo-search,repo-search)", text)
        self.assertIn(
            "@$(call repo_activity,make repo-search-full,repo-search-full)",
            text,
        )
        self.assertIn('$(PYTHON) -m tools.repo_search --query "$(Q)"', text)
        self.assertIn(
            '$(PYTHON) -m tools.repo_search --mode full --query "$(Q)"',
            text,
        )

    def test_act_targets_report_missing_cli_before_running(self) -> None:
        text = _makefile_contract_text()

        self.assertRegex(text, r"(?m)^act-list:$")
        self.assertRegex(text, r"(?m)^act-ci:$")
        self.assertIn(
            '$(PYTHON) -m tools.require_command --command "$(ACT)" --label "act helper"',
            text,
        )
        self.assertNotIn('command -v "$(ACT)"', text)
        self.assertIn("$(ACT) -l", text)
        self.assertIn("$(ACT) -W .github/workflows/ci.yml", text)

    def test_manual_eval_db_targets_are_terminal_native_and_backup_first(
        self,
    ) -> None:
        text = _makefile_contract_text()

        self.assertRegex(
            text,
            r"(?m)^manual-evals-db manual-evals-db-refresh:$",
        )
        self.assertIn("--backup-existing", text)
        self.assertIn("--status-summary", text)
        self.assertRegex(text, r"(?m)^manual-evals-db-status:$")
        self.assertIn("$(PYTHON) -m tools.manual_evals_db_status", text)
        self.assertRegex(text, r"(?m)^manual-evals-db-health:$")
        self.assertIn("$(PYTHON) -m tools.manual_evals_db_health", text)
        self.assertEqual(
            1,
            text.count("$(PYTHON) -m tools.manual_evals_db_health"),
        )
        self.assertIn(
            "MANUAL_EVALS_DB_HEALTH_COMMAND ?= "
            "$(PYTHON) -m tools.manual_evals_db_health",
            text,
        )
        self.assertIn(
            "manual_evals_db_health = "
            "@$(call repo_activity,make $@,$@) && "
            "$(MANUAL_EVALS_DB_HEALTH_COMMAND) $(1) $(strip $(2))",
            text,
        )
        self.assertIn(
            "@$(call repo_activity,make $@,$@)\n"
            "\t$(PYTHON) -m tools.build_manual_evals_db",
            text,
        )
        self.assertRegex(
            text,
            r"(?m)^manual-evals-feedback-actionables:$",
        )
        self.assertIn(
            "$(call manual_evals_db_health,--open-feedback-actionables,"
            "$(MANUAL_EVALS_FEEDBACK_ACTIONABLE_ARGS))",
            text,
        )
        self.assertIn(
            "$(call manual_evals_db_health,--ocr-retry-selection-draft,"
            "$(MANUAL_EVALS_OCR_RETRY_PLAN_ARGS) "
            "$(MANUAL_EVALS_OCR_RETRY_SELECTION_DRAFT_ARGS))",
            text,
        )
        self.assertIn("--open-feedback-actionables", text)
        self.assertIn(
            "$(call manual_evals_db_health,--open-feedback-actionables,"
            "$(MANUAL_EVALS_FEEDBACK_ACTIONABLE_ARGS))",
            text,
        )
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
            r"(?m)^manual-evals-feedback-cohorts:$",
        )
        self.assertIn("--open-feedback-cohorts", text)
        self.assertIn("--cohort", text)
        self.assertIn("$(MANUAL_EVALS_FEEDBACK_FILTER_ARGS)", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-feedback-source-context:$",
        )
        self.assertIn("--feedback-source-context", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-feedback-decision-draft:$",
        )
        self.assertIn("--feedback-decision-draft", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-feedback-decision-preview:$",
        )
        self.assertIn("--feedback-decision-preview", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-overlay-comparison-readiness:$",
        )
        self.assertIn("--overlay-ocr-comparison-readiness", text)
        self.assertIn("--overlay-source-index", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-overlay-source-index-draft:$",
        )
        self.assertIn("--overlay-source-index-draft", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-overlay-source-index-validate:$",
        )
        self.assertIn("--overlay-source-index-validate", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-candidates:$",
        )
        self.assertIn("--ocr-retry-candidates", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-source-verification:$",
        )
        self.assertIn("--ocr-retry-source-verification", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-source-provenance:$",
        )
        self.assertIn("--ocr-retry-source-provenance", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-input-packet:$",
        )
        self.assertIn("--ocr-retry-input-packet", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-rerun-manifest:$",
        )
        self.assertIn("--ocr-retry-rerun-manifest", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-rerun-plan:$",
        )
        self.assertIn("--ocr-retry-rerun-plan", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-selection-review:$",
        )
        self.assertIn("--ocr-retry-selection-review", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-selection-template:$",
        )
        self.assertIn("--ocr-retry-selection-template", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-selection-draft:$",
        )
        self.assertIn("--ocr-retry-selection-draft", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-selection-validate:$",
        )
        self.assertIn("--ocr-retry-selection-validate", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-selection-apply-preview:$",
        )
        self.assertIn("--ocr-retry-selection-apply-preview", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-execution-readiness:$",
        )
        self.assertIn("--ocr-retry-execution-readiness", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-execute:$",
        )
        self.assertIn("--ocr-retry-execute", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-execution-report:$",
        )
        self.assertIn("--ocr-retry-execution-report", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-feedback-closure-preview:$",
        )
        self.assertIn("--ocr-retry-feedback-closure-preview", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-feedback-closure-apply:$",
        )
        self.assertIn("--ocr-retry-feedback-closure-apply", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-feedback-closure-apply-report:$",
        )
        self.assertIn("--ocr-retry-feedback-closure-apply-report", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-feedback-closure-restore-preview:$",
        )
        self.assertIn("--ocr-retry-feedback-closure-restore-preview", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-ocr-retry-feedback-closure-restore:$",
        )
        self.assertIn("--ocr-retry-feedback-closure-restore", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-no-context-reclassify-preview:$",
        )
        self.assertIn("--no-context-feedback-reclassify-preview", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-no-context-reclassify-apply:$",
        )
        self.assertIn("--no-context-feedback-reclassify-apply", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-feedback-reclassify-preview:$",
        )
        self.assertIn("--feedback-reclassify-preview", text)
        self.assertRegex(
            text,
            r"(?m)^manual-evals-feedback-reclassify-apply:$",
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
        self.assertIn("MANUAL_EVALS_RECLASSIFY_CONFIRM ?= $(CONFIRM)", text)
        self.assertIn("MANUAL_EVALS_RECLASSIFY_BACKUP_ROOT ?= $(BACKUP_ROOT)", text)
        self.assertIn("MANUAL_EVALS_FEEDBACK_DECISION_PATH ?= $(DECISION_PATH)", text)
        self.assertIn(
            "MANUAL_EVALS_FEEDBACK_DECISION_DRAFT_PATH ?= $(DRAFT_PATH)", text
        )
        self.assertIn("MANUAL_EVALS_FEEDBACK_DECISION_DRAFT_FORCE ?= $(FORCE)", text)
        self.assertIn("$(MANUAL_EVALS_FEEDBACK_DECISION_ARGS)", text)
        self.assertIn("$(MANUAL_EVALS_FEEDBACK_DECISION_DRAFT_ARGS)", text)
        self.assertIn("$(MANUAL_EVALS_FEEDBACK_RECLASSIFY_ARGS)", text)
        self.assertIn("$(MANUAL_EVALS_FEEDBACK_RECLASSIFY_APPLY_ARGS)", text)
        self.assertIn(
            "$(if $(strip $(MANUAL_EVALS_RECLASSIFY_CONFIRM)),"
            '--confirm "$(MANUAL_EVALS_RECLASSIFY_CONFIRM)")',
            text,
        )
        self.assertIn(
            "$(if $(strip $(MANUAL_EVALS_RECLASSIFY_BACKUP_ROOT)),"
            '--backup-root "$(MANUAL_EVALS_RECLASSIFY_BACKUP_ROOT)")',
            text,
        )
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

    def test_lifecycle_targets_keep_canonical_names(self) -> None:
        text = _makefile_contract_text()

        self.assertNotIn("eod", _phony_targets())
        self.assertNotRegex(text, r"(?m)^eod:")
        self.assertIn("end-preflight:", text)
        self.assertIn("END_SKIP_GIT_CHECK=1 END_SKIP_STOP=1", text)
        self.assertIn("git-prune-stale-refs", _phony_targets())
        self.assertRegex(text, r"(?m)^git-prune-stale-refs:$")
        self.assertIn("bash ./tools/git_prune_stale_refs.sh", text)
        self.assertNotIn("eod-stop", _phony_targets())
        self.assertNotRegex(text, r"(?m)^eod-stop:")
        self.assertRegex(
            text,
            r"(?m)^end-stop:\s*eval-sidecar-stop server-daemon-stop "
            r"caffeinate-off-all session-status$",
        )
        self.assertIn("session-status", _phony_targets())
        self.assertRegex(text, r"(?m)^session-status:$")
        self.assertIn("bash ./tools/session_status.sh", text)
        status_script = SESSION_STATUS_SCRIPT.read_text(encoding="utf-8")
        make_runtime_script = MAKE_RUNTIME_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("polinko_make_bin()", make_runtime_script)
        self.assertIn("polinko_require_make_command()", make_runtime_script)
        self.assertIn("polinko_command_available", make_runtime_script)
        self.assertIn("shell_command_common.sh", make_runtime_script)
        self.assertNotIn("command -v", make_runtime_script)
        self.assertIn('source "$script_dir/make_runtime.sh"', status_script)
        self.assertIn(
            'MAKE_BIN=$(polinko_require_make_command "session-status")',
            status_script,
        )
        self.assertNotIn('command -v "$MAKE_BIN"', status_script)
        self.assertIn("STATUS_STEP_LABELS=(", status_script)
        self.assertIn('"Server"', status_script)
        self.assertIn('"Eval sidecar"', status_script)
        self.assertIn('"Keep-awake"', status_script)
        self.assertIn('"server-daemon-status"', status_script)
        self.assertIn('"eval-sidecar-status"', status_script)
        self.assertIn('"caffeinate-status"', status_script)
        self.assertIn("status=0", status_script)
        self.assertIn("step_status=$?", status_script)
        self.assertIn('exit "$status"', status_script)
        self.assertNotIn("server-daemon-status || true", text)
        self.assertNotIn("eval-sidecar-status || true", text)
        self.assertNotIn("caffeinate-status || true", text)
        self.assertRegex(text, r"(?m)^caffeinate-on:\s*caffeinate$")
        self.assertRegex(text, r"(?m)^caffeinate-off:\s*decaffeinate$")
        self.assertRegex(text, r"(?m)^caffeinate-off-all:$")
        self.assertRegex(text, r"(?m)^decaffeinate-status:\s*caffeinate-status$")

    def test_local_privacy_guard_does_not_hide_tracked_docs_on_apply(self) -> None:
        text = LOCAL_PRIVACY_GUARD_SCRIPT.read_text(encoding="utf-8")
        apply_body_match = re.search(
            r"apply_guard\(\) \{\n(?P<body>.*?)\n\}", text, re.S
        )

        self.assertIsNotNone(apply_body_match)
        apply_body = apply_body_match.group("body")
        self.assertIn("write_exclude_block", apply_body)
        self.assertNotIn("--skip-worktree", apply_body)
        self.assertIn("docs/peanut/governance/SESSION_HANDOFF.md", text)
        self.assertNotIn("docs/INSTANCE_HANDOFF.md", text)
        self.assertNotIn("docs/POL1_COMMS.md", text)
        self.assertIn("install local excludes for machine-local docs", text)
        self.assertIn("clear tracked docs skip-worktree state", text)
        self.assertIn("git ls-files -v docs | awk", text)
        self.assertIn("skip_worktree_docs=$(list_skip_worktree_docs)", text)
        self.assertNotIn("rg '^S'", text)
        self.assertNotIn("|| true", text)
        self.assertNotIn("xargs -r", text)
        self.assertIn("git update-index --no-skip-worktree --", text)

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
            r"(?m)^ci-docs:\s*path-leak-check scripts-check "
            r"local-runtime-config-check risk-scan "
            r"runtime-tool-reference-check operator-command-check "
            r"startup-contracts-check lint-docs$",
        )
        self.assertIn("startup-contracts-check", _phony_targets())
        self.assertRegex(text, r"(?m)^startup-contracts-check:$")
        self.assertIn("$(PYTHON) -m unittest tests.test_startup_contracts", text)
        self.assertIn("risk-scan", _phony_targets())
        self.assertRegex(text, r"(?m)^risk-scan:$")
        self.assertIn("$(PYTHON) -m tools.check_runtime_risk_scan", text)
        self.assertIn("runtime-tool-reference-check", _phony_targets())
        self.assertRegex(text, r"(?m)^runtime-tool-reference-check:$")
        self.assertIn(
            "$(PYTHON) -m unittest tests.test_runtime_tool_reference_coverage",
            text,
        )
        self.assertIn("local-runtime-config-check", _phony_targets())
        self.assertRegex(text, r"(?m)^local-runtime-config-check:$")
        self.assertIn("$(PYTHON) -m tools.check_local_runtime_config", text)
        self.assertIn("operator-command-check", _phony_targets())
        self.assertRegex(text, r"(?m)^operator-command-check:$")
        self.assertIn("$(PYTHON) -m tools.check_operator_commands", text)
        self.assertRegex(text, r"(?m)^path-leak-audit-local:$")
        self.assertIn("$(PYTHON) -m tools.path_leak_check --scope local-config", text)
        self.assertIn("$(MAKE) --no-print-directory local-runtime-config-check", text)
        self.assertIn("CORE_STEP_LABELS=(", closeout_text)
        self.assertIn("TOTAL_STEPS=${#CORE_STEP_LABELS[@]}", closeout_text)
        self.assertIn("TOTAL_STEPS=$((TOTAL_STEPS + 3))", closeout_text)
        self.assertNotIn("TOTAL_STEPS=17", closeout_text)
        self.assertNotIn("run_planned_step", closeout_text)
        self.assertNotIn("read -r -a", closeout_text)
        self.assertNotIn("record%%|", closeout_text)
        self.assertIn('run_make_step "$label" "$label"', closeout_text)
        self.assertIn(
            '"git diff --check") run_step "$label" git diff --check',
            closeout_text,
        )
        self.assertIn(
            '"scripts-check"',
            closeout_text,
        )
        self.assertIn(
            '"path-leak-check"',
            closeout_text,
        )
        self.assertIn(
            '"risk-scan"',
            closeout_text,
        )
        self.assertIn(
            '"runtime-tool-reference-check"',
            closeout_text,
        )
        self.assertIn(
            '"operator-command-check"',
            closeout_text,
        )
        self.assertIn(
            'run_step "git-prune-stale-refs" make --no-print-directory git-prune-stale-refs',
            closeout_text,
        )
        self.assertIn(
            'run_step "github-health" make --no-print-directory github-health',
            closeout_text,
        )
        self.assertIn(
            'run_step "end-git-check" make --no-print-directory end-git-check',
            closeout_text,
        )
        self.assertGreater(
            closeout_text.index('"scripts-check"'),
            closeout_text.index('"doctor-env"'),
        )
        self.assertLess(
            closeout_text.index('"scripts-check"'),
            closeout_text.index('"path-leak-check"'),
        )
        self.assertLess(
            closeout_text.index('"path-leak-check"'),
            closeout_text.index('"risk-scan"'),
        )
        self.assertLess(
            closeout_text.index('"risk-scan"'),
            closeout_text.index('"runtime-tool-reference-check"'),
        )
        self.assertLess(
            closeout_text.index('"runtime-tool-reference-check"'),
            closeout_text.index('"operator-command-check"'),
        )
        self.assertLess(
            closeout_text.index('"operator-command-check"'),
            closeout_text.index('"ci-python-style"'),
        )
        self.assertLess(
            closeout_text.index('"security-checks"'),
            closeout_text.index('run_step "github-health"'),
        )
        self.assertLess(
            closeout_text.index('run_step "github-health"'),
            closeout_text.index('run_step "git-prune-stale-refs"'),
        )
        self.assertLess(
            closeout_text.index('run_step "git-prune-stale-refs"'),
            closeout_text.index('run_step "end-git-check"'),
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
        self.assertIn(
            "@$(call repo_activity,make backend-gate-start,backend-gate-start)",
            text,
        )
        self.assertIn("$(call repo_activity,make test-one,test-one)", text)
        self.assertIn("$(call repo_activity,make test-targeted,test-targeted)", text)
        self.assertRegex(text, r"(?m)^docs:\s*server-daemon$")
        self.assertRegex(text, r"(?m)^docs-open:\s*server-daemon$")
        self.assertNotRegex(text, r"(?m)^open-api-docs:")
        self.assertNotRegex(text, r"(?m)^open-api-docs-browser:")
        self.assertNotRegex(text, r"(?m)^open-limits:")
        self.assertNotRegex(text, r"(?m)^open-usage:")
        self.assertNotRegex(text, r"(?m)^open-billing:")
        self.assertNotRegex(text, r"(?m)^open-cost-console:")
        self.assertRegex(text, r"(?m)^viz:\s*server-daemon$")
        self.assertRegex(text, r"(?m)^viz-open:\s*server-daemon$")
        self.assertNotRegex(text, r"(?m)^open-viz:")
        for target in (
            "eval-clip-ab",
            "eval-file-search",
            "eval-hallucination",
            "eval-hallucination-deterministic",
            "eval-ocr",
            "eval-ocr-recovery",
            "eval-ocr-safety",
            "eval-response-behaviour",
            "eval-retrieval",
            "eval-style",
        ):
            self.assertRegex(text, rf"(?m)^{target}:\s*server-daemon$")
        self.assertNotRegex(text, r"(?m)^portfolio:")
        self.assertNotRegex(text, r"(?m)^portfolio-open:")
        self.assertNotRegex(text, r"(?m)^portfolio-playwright:")
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
        intake_workflow_text = OCR_INTAKE_WORKFLOW_SCRIPT.read_text(encoding="utf-8")
        ocr_workflow_text = OCR_WORKFLOW_SCRIPT.read_text(encoding="utf-8")

        self.assertNotIn("$(MAKE)", text)
        self.assertNotIn("import json,pathlib", text)
        self.assertNotIn("CASE_COUNT=", text)
        self.assertIn("tools.count_eval_cases", guard_text)
        self.assertIn("shell_command_common.sh", guard_text)
        self.assertIn(
            "polinko_command_available polinko_default_python_bin", guard_text
        )
        self.assertNotIn("command -v polinko_default_python_bin", guard_text)
        self.assertIn("EVAL_CASE_GUARD_SCRIPT", common_text)
        self.assertIn("eval_case_guard.sh", common_text)
        self.assertIn("ocr_workflow_resolve_export_root", common_text)
        self.assertIn("ocr_workflow_require_export_root", common_text)
        self.assertIn("OCR_WORKFLOW_EXPORT_ROOT", common_text)
        self.assertIn("source=tools/ocr_workflow_common.sh", intake_workflow_text)
        self.assertIn('. "$script_dir/ocr_workflow_common.sh"', intake_workflow_text)
        self.assertIn("ocr_workflow_require_export_root", intake_workflow_text)
        self.assertIn("source=tools/ocr_workflow_common.sh", ocr_workflow_text)
        self.assertIn('. "$script_dir/ocr_workflow_common.sh"', ocr_workflow_text)
        self.assertIn("ocr_workflow_require_export_root", ocr_workflow_text)
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
                f"@$(call repo_activity,make {suite},{suite})",
                text,
            )
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
            r"(?m)^ocr-notebook-workflow:\n\t@CGPT_EXPORT_ROOT=\"\$\(CGPT_EXPORT_ROOT\)\" \\\n\t\tCGPT_EXPORT_ROOT_DEFAULT=\"\$\(CGPT_EXPORT_ROOT_DEFAULT\)\" \\\n\t\tbash \"\$\(OCR_WORKFLOW_SCRIPT\)\" ocr-notebook-workflow$",
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
        self.assertTrue(PROCESS_LIFECYCLE_COMMON_SCRIPT.is_file())
        self.assertTrue(DETACHED_PROCESS_LAUNCHER_SCRIPT.is_file())
        self.assertTrue(END_GIT_CHECK_SCRIPT.is_file())
        self.assertTrue(os.access(CAFFEINATE_SCRIPT, os.X_OK))
        self.assertTrue(os.access(SERVER_DAEMON_SCRIPT, os.X_OK))
        detached_launcher_text = DETACHED_PROCESS_LAUNCHER_SCRIPT.read_text(
            encoding="utf-8"
        )
        self.assertIn("start_new_session=True", detached_launcher_text)
        self.assertIn("pid_file.write_text", detached_launcher_text)
        caffeinate_script_text = CAFFEINATE_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("launch_detached_process.py", caffeinate_script_text)
        self.assertIn('source "$script_dir/repo_root.sh"', caffeinate_script_text)
        self.assertIn("polinko_cd_repo_root", caffeinate_script_text)
        self.assertIn(
            'detached_launcher="$POLINKO_REPO_ROOT/tools/launch_detached_process.py"',
            caffeinate_script_text,
        )
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
        self.assertNotIn("PORTFOLIO_MOCKUP_SCRIPT", text)
        self.assertNotIn("run_portfolio_mockups.sh", text)
        self.assertNotIn('rm -f "$(SERVER_PID_FILE)"', text)
        server_daemon_script_text = SERVER_DAEMON_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("launch_detached_process.py", server_daemon_script_text)
        self.assertIn('source "$script_dir/repo_root.sh"', server_daemon_script_text)
        self.assertIn("polinko_cd_repo_root", server_daemon_script_text)
        self.assertIn(
            '. "$script_dir/process_lifecycle_common.sh"',
            server_daemon_script_text,
        )
        self.assertIn("polinko_pid_is_running", server_daemon_script_text)
        self.assertIn(
            'polinko_require_process_inspection "server-daemon PID inspection"',
            server_daemon_script_text,
        )
        self.assertIn("polinko_command_available lsof", server_daemon_script_text)
        self.assertNotIn("command -v lsof", server_daemon_script_text)
        self.assertIn("polinko_require_tcp_port", server_daemon_script_text)
        self.assertIn("polinko_require_positive_integer", server_daemon_script_text)
        self.assertIn(
            "polinko_require_non_negative_decimal",
            server_daemon_script_text,
        )
        self.assertIn(
            'polinko_require_command curl "server-daemon readiness check"',
            server_daemon_script_text,
        )
        self.assertIn(
            'detached_launcher="$POLINKO_REPO_ROOT/tools/launch_detached_process.py"',
            server_daemon_script_text,
        )
        self.assertNotIn("nohup", server_daemon_script_text)
        self.assertIn(
            "CAFFEINATE_MATCH_PATTERN ?= ^/usr/bin/caffeinate -d -i -m( |$$)",
            text,
        )
        self.assertIn(
            'CAFFEINATE_MATCH_PATTERN="$(CAFFEINATE_MATCH_PATTERN)"',
            text,
        )
        self.assertIn("CAFFEINATE_RUNTIME_ROOT ?= /tmp/polinko-runtime", text)
        self.assertIn(
            "CAFFEINATE_STATE_DIR ?= $(CAFFEINATE_RUNTIME_ROOT)/$(CAFFEINATE_REPO_SLUG)",
            text,
        )
        self.assertIn(
            "CAFFEINATE_PID_FILE ?= $(CAFFEINATE_STATE_DIR)/caffeinate.pid",
            text,
        )
        self.assertIn(
            "CAFFEINATE_LOG ?= $(CAFFEINATE_STATE_DIR)/caffeinate.log",
            text,
        )
        self.assertIn(
            "CAFFEINATE_META_FILE ?= $(CAFFEINATE_STATE_DIR)/caffeinate.meta.json",
            text,
        )
        self.assertIn(
            "CAFFEINATE_ACTIVITY_FILE ?= $(CAFFEINATE_STATE_DIR)/activity.meta.json",
            text,
        )
        self.assertIn("CAFFEINATE_REPO_SLUG ?= $(notdir $(CURDIR))", text)
        self.assertIn("CAFFEINATE_ACTIVE_WINDOW_SECONDS ?= 1800", text)
        self.assertIn("CAFFEINATE_ALLOW_GLOBAL_CLEANUP ?= 0", text)
        self.assertIn("repo_activity = $(CAFFEINATE_ENV)", text)
        self.assertIn('bash "$(CAFFEINATE_SCRIPT)" activity', text)
        self.assertIn('CAFFEINATE_ACTIVITY_LABEL="$(1)"', text)
        self.assertIn('CAFFEINATE_ACTIVITY_TARGET="$(2)"', text)
        self.assertIn("SERVER_REPO_SLUG ?= $(notdir $(CURDIR))", text)
        self.assertIn("SERVER_RUNTIME_ROOT ?= /tmp/polinko-runtime", text)
        self.assertIn(
            "SERVER_STATE_DIR ?= $(SERVER_RUNTIME_ROOT)/$(SERVER_REPO_SLUG)",
            text,
        )
        self.assertIn("SERVER_PID_FILE ?= $(SERVER_STATE_DIR)/server.pid", text)
        self.assertIn("SERVER_LOG ?= $(SERVER_STATE_DIR)/server.log", text)
        self.assertIn('SERVER_REPO_SLUG="$(SERVER_REPO_SLUG)"', text)
        self.assertIn('SERVER_RUNTIME_ROOT="$(SERVER_RUNTIME_ROOT)"', text)
        self.assertIn('SERVER_STATE_DIR="$(SERVER_STATE_DIR)"', text)
        self.assertIn("@$(call repo_activity,make test,test)", text)
        self.assertIn("@$(call repo_activity,make scripts-check,scripts-check)", text)
        self.assertIn("@$(call repo_activity,make risk-scan,risk-scan)", text)
        self.assertIn("@$(call repo_activity,make $@,$@)", text)
        self.assertIn("@$(call repo_activity,make chat,chat)", text)
        self.assertIn("@$(call repo_activity,make end,end)", text)
        self.assertIn(
            "@$(call repo_activity,make server-daemon,server-daemon)",
            text,
        )
        self.assertIn(
            "@$(call repo_activity,make server-daemon-stop,server-daemon-stop)",
            text,
        )
        self.assertIn(
            "@$(call repo_activity,make eval-sidecar-start,eval-sidecar-start)",
            text,
        )
        self.assertIn(
            "@$(call repo_activity,make eval-sidecar-stop,eval-sidecar-stop)",
            text,
        )
        self.assertIn(
            "@$(call repo_activity,make openai-account-summary,openai-account-summary)",
            text,
        )
        self.assertIn(
            "@$(call repo_activity,make openai-costs,openai-costs)",
            text,
        )
        self.assertIn(
            "@$(call repo_activity,make openai-usage,openai-usage)",
            text,
        )
        self.assertIn(
            "@$(call repo_activity,make openai-limits,openai-limits)",
            text,
        )
        self.assertIn(
            "@$(call repo_activity,make privacy-local-on,privacy-local-on)",
            text,
        )
        self.assertIn(
            "@$(call repo_activity,make privacy-local-off,privacy-local-off)",
            text,
        )
        self.assertNotIn(
            "@$(call repo_activity,make server-daemon-status,server-daemon-status)",
            text,
        )
        self.assertNotIn(
            "@$(call repo_activity,make eval-sidecar-status,eval-sidecar-status)",
            text,
        )
        self.assertNotIn(
            "@$(call repo_activity,make privacy-local-status,privacy-local-status)",
            text,
        )
        self.assertNotIn(
            "@$(call repo_activity,make caffeinate-status,caffeinate-status)",
            text,
        )
        self.assertIn(
            "@$(call repo_activity,make package-install-check,package-install-check)",
            text,
        )
        self.assertIn("@$(call repo_activity,make repo-search,repo-search)", text)
        self.assertIn(
            "@$(call repo_activity,make repo-search-full,repo-search-full)",
            text,
        )
        self.assertIn("@$(call repo_activity,make act-list,act-list)", text)
        self.assertIn("@$(call repo_activity,make act-ci,act-ci)", text)
        self.assertIn("@$(call repo_activity,make k6-chat-smoke,k6-chat-smoke)", text)
        self.assertIn("@$(call repo_activity,make trivy-fs,trivy-fs)", text)
        self.assertIn("@$(call repo_activity,make trivy-image,trivy-image)", text)
        self.assertIn("@$(call repo_activity,make docker-build,docker-build)", text)
        self.assertIn("@$(call repo_activity,make docker-run,docker-run)", text)
        self.assertIn("@$(call repo_activity,make mermaid-render,mermaid-render)", text)
        self.assertIn("@$(call repo_activity,make d3-render,d3-render)", text)
        self.assertIn("@$(call repo_activity,make transcript-fix,transcript-fix)", text)
        self.assertIn(
            "@$(call repo_activity,make transcript-check,transcript-check)", text
        )
        self.assertIn("@$(call repo_activity,make $@,$@)", text)
        self.assertIn(
            "@$(call repo_activity,make notebook-setup,notebook-setup)",
            text,
        )
        self.assertIn(
            "@$(call repo_activity,make playwright-snapshot-dir,playwright-snapshot-dir)",
            text,
        )
        self.assertIn('CAFFEINATE_META_FILE="$(CAFFEINATE_META_FILE)"', text)
        self.assertIn(
            'CAFFEINATE_ACTIVITY_FILE="$(CAFFEINATE_ACTIVITY_FILE)"',
            text,
        )
        self.assertIn('CAFFEINATE_RUNTIME_ROOT="$(CAFFEINATE_RUNTIME_ROOT)"', text)
        self.assertIn('CAFFEINATE_STATE_DIR="$(CAFFEINATE_STATE_DIR)"', text)
        self.assertIn('CAFFEINATE_REPO_SLUG="$(CAFFEINATE_REPO_SLUG)"', text)
        self.assertIn(
            'CAFFEINATE_ACTIVE_WINDOW_SECONDS="$(CAFFEINATE_ACTIVE_WINDOW_SECONDS)"',
            text,
        )
        self.assertIn(
            'CAFFEINATE_ALLOW_GLOBAL_CLEANUP="$(CAFFEINATE_ALLOW_GLOBAL_CLEANUP)"',
            text,
        )
        self.assertIn("CAFFEINATE_MATCH_PATTERN", caffeinate_script_text)
        self.assertNotIn("nohup $(CAFFEINATE_CMD)", text)
        self.assertNotIn('pgrep -f "^/usr/bin/caffeinate -d -i -m', text)
        self.assertNotIn("/usr/bin/pmset -g assertions", text)
        end_git_check_text = END_GIT_CHECK_SCRIPT.read_text(encoding="utf-8")
        self.assertIn('source "$script_dir/repo_root.sh"', end_git_check_text)
        self.assertIn("polinko_cd_repo_root", end_git_check_text)

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
        eval_report_script_text = EVAL_REPORT_RUNNER_SCRIPT.read_text(encoding="utf-8")
        self.assertIn('source "$script_dir/repo_root.sh"', eval_report_script_text)
        self.assertIn("polinko_cd_repo_root", eval_report_script_text)
        eval_reports_parallel_script_text = (
            EVAL_REPORTS_PARALLEL_RUNNER_SCRIPT.read_text(encoding="utf-8")
        )
        self.assertIn(
            'source "$script_dir/repo_root.sh"',
            eval_reports_parallel_script_text,
        )
        self.assertIn("polinko_cd_repo_root", eval_reports_parallel_script_text)
        local_eval_gate_script_text = LOCAL_EVAL_GATE_RUNNER_SCRIPT.read_text(
            encoding="utf-8"
        )
        self.assertIn('source "$script_dir/repo_root.sh"', local_eval_gate_script_text)
        self.assertIn("polinko_cd_repo_root", local_eval_gate_script_text)
        self.assertIn(
            '. "$script_dir/process_lifecycle_common.sh"',
            local_eval_gate_script_text,
        )
        self.assertIn(
            'polinko_require_command curl "local eval gate readiness check"',
            local_eval_gate_script_text,
        )
        self.assertIn(
            'polinko_require_process_inspection "local eval gate PID inspection"',
            local_eval_gate_script_text,
        )
        self.assertIn(
            "polinko_require_positive_integer",
            local_eval_gate_script_text,
        )
        self.assertIn(
            "polinko_require_non_negative_decimal",
            local_eval_gate_script_text,
        )
        self.assertIn("polinko_require_tcp_port", local_eval_gate_script_text)
        self.assertIn(
            'while [ "$attempt" -lt "$local_eval_gate_start_attempts" ]; do',
            local_eval_gate_script_text,
        )
        self.assertIn(
            'sleep "$local_eval_gate_start_sleep_seconds"',
            local_eval_gate_script_text,
        )
        self.assertNotIn("seq 1 100", local_eval_gate_script_text)
        sidecar_script_text = EVAL_SIDECAR_START_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("launch_detached_process.py", sidecar_script_text)
        self.assertIn('source "$script_dir/repo_root.sh"', sidecar_script_text)
        self.assertIn("polinko_cd_repo_root", sidecar_script_text)
        self.assertIn(
            '. "$script_dir/process_lifecycle_common.sh"',
            sidecar_script_text,
        )
        self.assertIn("polinko_pid_is_running", sidecar_script_text)
        self.assertIn(
            'polinko_require_process_inspection "eval-sidecar PID inspection"',
            sidecar_script_text,
        )
        self.assertIn("polinko_require_positive_integer", sidecar_script_text)
        self.assertIn("polinko_require_non_negative_decimal", sidecar_script_text)
        self.assertIn(
            'detached_launcher="$POLINKO_REPO_ROOT/tools/launch_detached_process.py"',
            sidecar_script_text,
        )
        self.assertNotIn("nohup", sidecar_script_text)
        eval_server_daemon_text = EVAL_SERVER_DAEMON_SCRIPT.read_text(encoding="utf-8")
        self.assertIn('source "$script_dir/make_runtime.sh"', eval_server_daemon_text)
        self.assertIn(
            'MAKE_BIN=$(polinko_require_make_command "ensure-eval-server-daemon")',
            eval_server_daemon_text,
        )
        self.assertNotIn('command -v "$MAKE_BIN"', eval_server_daemon_text)
        ocr_workflow_text = OCR_WORKFLOW_SCRIPT.read_text(encoding="utf-8")
        self.assertIn('source "$script_dir/make_runtime.sh"', ocr_workflow_text)
        self.assertIn(
            'MAKE_BIN=$(polinko_require_make_command "ocr-workflow")',
            ocr_workflow_text,
        )
        self.assertNotIn('command -v "$MAKE_BIN"', ocr_workflow_text)
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
        for script in (
            OCR_EVAL_RUNNER_SCRIPT,
            OCR_HANDWRITING_EVAL_RUNNER_SCRIPT,
            OCR_STABILITY_RUNNER_SCRIPT,
            OCR_GROWTH_EVAL_RUNNER_SCRIPT,
            OCR_GROWTH_BATCH_RUNNER_SCRIPT,
            OCR_GROWTH_STABILITY_RUNNER_SCRIPT,
        ):
            script_text = script.read_text(encoding="utf-8")
            self.assertIn('source "$script_dir/repo_root.sh"', script_text)
            self.assertIn("polinko_cd_repo_root", script_text)
            self.assertIn("source=tools/python_runtime.sh", script_text)
            self.assertIn('. "$script_dir/python_runtime.sh"', script_text)
            self.assertIn("python_bin=$(polinko_default_python_bin)", script_text)
        guarded_runner_text = OCR_GUARDED_CASE_RUNNER_SCRIPT.read_text(encoding="utf-8")
        common_text = OCR_WORKFLOW_COMMON_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("EVAL_CASE_GUARD_SCRIPT", common_text)
        self.assertIn("eval_case_guard.sh", common_text)
        self.assertIn('source "$script_dir/repo_root.sh"', guarded_runner_text)
        self.assertIn("polinko_cd_repo_root", guarded_runner_text)
        self.assertIn("OCR_WORKFLOW_COMMON_SCRIPT", guarded_runner_text)
        self.assertIn("ocr_workflow_use_eval_case_guard", guarded_runner_text)
        self.assertIn('exec "$@"', guarded_runner_text)
        base_transcript_workflow_text = OCR_BASE_TRANSCRIPT_WORKFLOW_SCRIPT.read_text(
            encoding="utf-8"
        )
        self.assertIn(
            'source "$script_dir/repo_root.sh"', base_transcript_workflow_text
        )
        self.assertIn("polinko_cd_repo_root", base_transcript_workflow_text)
        self.assertIn("OCR_WORKFLOW_COMMON_SCRIPT", base_transcript_workflow_text)
        self.assertIn("ocr_workflow_use_eval_case_guard", base_transcript_workflow_text)
        self.assertIn("eval_case_guard_or_exit", base_transcript_workflow_text)
        self.assertIn("OCR_EVAL_RUNNER_SCRIPT", base_transcript_workflow_text)
        self.assertIn("OCR_STABILITY_RUNNER_SCRIPT", base_transcript_workflow_text)
        self.assertIn('exec bash "$eval_runner_script"', base_transcript_workflow_text)
        lane_workflow_text = OCR_TRANSCRIPT_LANE_WORKFLOW_SCRIPT.read_text(
            encoding="utf-8"
        )
        self.assertIn('source "$script_dir/repo_root.sh"', lane_workflow_text)
        self.assertIn("polinko_cd_repo_root", lane_workflow_text)
        self.assertIn("OCR_GUARDED_CASE_RUNNER_SCRIPT", lane_workflow_text)
        self.assertIn("OCR_EVAL_RUNNER_SCRIPT", lane_workflow_text)
        self.assertIn("OCR_STABILITY_RUNNER_SCRIPT", lane_workflow_text)
        self.assertIn('exec bash "$guarded_case_runner_script"', lane_workflow_text)
        growth_case_workflow_text = OCR_GROWTH_CASE_WORKFLOW_SCRIPT.read_text(
            encoding="utf-8"
        )
        self.assertIn('source "$script_dir/repo_root.sh"', growth_case_workflow_text)
        self.assertIn("polinko_cd_repo_root", growth_case_workflow_text)
        self.assertIn("OCR_WORKFLOW_COMMON_SCRIPT", growth_case_workflow_text)
        self.assertIn("OCR_GROWTH_EVAL_RUNNER_SCRIPT", growth_case_workflow_text)
        self.assertIn("OCR_GROWTH_BATCH_RUNNER_SCRIPT", growth_case_workflow_text)
        self.assertIn("eval_case_guard_or_exit", growth_case_workflow_text)
        report_builder_text = OCR_REPORT_BUILDER_SCRIPT.read_text(encoding="utf-8")
        self.assertIn('source "$script_dir/repo_root.sh"', report_builder_text)
        self.assertIn("polinko_cd_repo_root", report_builder_text)
        report_workflow_text = OCR_REPORT_WORKFLOW_SCRIPT.read_text(encoding="utf-8")
        self.assertIn('source "$script_dir/repo_root.sh"', report_workflow_text)
        self.assertIn("polinko_cd_repo_root", report_workflow_text)
        self.assertIn("OCR_REPORT_BUILDER_SCRIPT", report_workflow_text)
        self.assertIn('exec bash "$report_builder_script"', report_workflow_text)
        intake_workflow_text = OCR_INTAKE_WORKFLOW_SCRIPT.read_text(encoding="utf-8")
        self.assertIn('source "$script_dir/repo_root.sh"', intake_workflow_text)
        self.assertIn("polinko_cd_repo_root", intake_workflow_text)
        self.assertIn("tools.build_ocr_cases_from_export", intake_workflow_text)
        self.assertIn("tools.build_handwriting_benchmark_cases", intake_workflow_text)
        self.assertIn("tools.build_ocr_generalization_review", intake_workflow_text)
        self.assertIn("tools.report_ocr_case_mining_delta", intake_workflow_text)
        for script in (
            OCR_FOCUS_STABILITY_WORKFLOW_SCRIPT,
            OCR_GROWTH_STABILITY_WORKFLOW_SCRIPT,
        ):
            script_text = script.read_text(encoding="utf-8")
            self.assertIn('source "$script_dir/repo_root.sh"', script_text)
            self.assertIn("polinko_cd_repo_root", script_text)
            self.assertIn("OCR_WORKFLOW_COMMON_SCRIPT", script_text)
            self.assertIn("ocr_workflow_use_eval_case_guard", script_text)
            self.assertIn('exec bash "', script_text)
        self.assertFalse((REPO_ROOT / "tools" / "ocr_workflow.sh").exists())
        self.assertFalse((REPO_ROOT / "tools" / "ensure_server_daemon.sh").exists())

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
                self.assertIn("tools.local_url", result.stdout)
                self.assertNotIn("LOCAL_URL_LAUNCHER_SCRIPT", result.stdout)
                self.assertNotIn('open "$URL"', result.stdout)
                self.assertNotIn("xdg-open", result.stdout)

    def test_local_url_targets_require_explicit_browser_launch(self) -> None:
        cases = (
            (
                ["docs-open"],
                "docs-open",
                '--mode system --launcher "./tools/open_local_url.sh"',
            ),
            (
                ["viz-open"],
                "viz-open",
                '--mode system --launcher "./tools/open_local_url.sh"',
            ),
            (
                ["docs", "LOCAL_BROWSER_LAUNCH=system"],
                "docs with launch override",
                '--mode "system" --launcher "./tools/open_local_url.sh"',
            ),
            (
                ["viz", "LOCAL_BROWSER_LAUNCH=system"],
                "viz with launch override",
                '--mode "system" --launcher "./tools/open_local_url.sh"',
            ),
        )
        for args, label, expected_script_call in cases:
            with self.subTest(target=label):
                result = subprocess.run(
                    ["make", "-n", *args],
                    cwd=REPO_ROOT,
                    check=True,
                    capture_output=True,
                    text=True,
                )

                self.assertIn("tools.local_url", result.stdout)
                self.assertIn(expected_script_call, result.stdout)
                self.assertNotIn("xdg-open", result.stdout)

    def test_local_url_launcher_owns_system_browser_launch(self) -> None:
        script_text = LOCAL_URL_LAUNCHER_SCRIPT.read_text(encoding="utf-8")

        self.assertTrue(LOCAL_URL_LAUNCHER_SCRIPT.is_file())
        self.assertTrue(os.access(LOCAL_URL_LAUNCHER_SCRIPT, os.X_OK))
        self.assertIn("is_local_url()", script_text)
        self.assertIn("Refusing to launch non-local URL", script_text)
        self.assertIn("shell_command_common.sh", script_text)
        self.assertIn("polinko_command_available open", script_text)
        self.assertIn("polinko_command_available xdg-open", script_text)
        self.assertNotIn("command -v open", script_text)
        self.assertNotIn("command -v xdg-open", script_text)
        self.assertIn('open "$url"', script_text)
        self.assertIn('xdg-open "$url"', script_text)
        self.assertIn("Open this URL in your browser: $url", script_text)

    def test_operator_wrapper_dry_runs_resolve_without_recursive_variable_errors(
        self,
    ) -> None:
        for target in (
            "docs",
            "docs-open",
            "viz",
            "viz-open",
            "openai-account-summary",
            "openai-costs",
            "openai-usage",
            "openai-limits",
            "caffeinate",
            "scripts-check",
            "caffeinate-status",
            "caffeinate-off-all",
            "end-stop",
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

    def test_build_hygiene_runs_ci_and_diff_whitespace_check(self) -> None:
        text = _makefile_contract_text()
        workflow_text = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(
            encoding="utf-8"
        )

        self.assertRegex(text, r"(?m)^\.PHONY: .*\bbuild-hygiene\b")
        self.assertRegex(
            text,
            r"(?m)^build-hygiene:\s*doctor-env transcript-check ci$",
        )
        self.assertRegex(text, r"(?m)^\s+git diff --check$")
        self.assertRegex(text, r"(?m)^\.PHONY: .*\bpr-preflight\b")
        self.assertRegex(text, r"(?m)^pr-preflight:\s*build-hygiene$")
        self.assertIn("build-hygiene:", workflow_text)
        self.assertIn("make build-hygiene PYTHON=python", workflow_text)

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
