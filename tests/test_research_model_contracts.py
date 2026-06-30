import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = "docs/research/pre-beta-2-4-research-model-contract-2026-05-19.md"
BETA_NOTE_PATHS = (
    "docs/research/beta_2_2_2026-05-08.md",
    "docs/research/beta-2-2-stability-soak-2026-05-09.md",
    "docs/research/beta_2_3_2026-05-16.md",
    "docs/research/pre-beta-2-4-research-model-contract-2026-05-19.md",
    "docs/eval/beta_2_3/README.md",
)
PUBLIC_MARKDOWN_PATHS = (
    "README.md",
    "docs/eval/README.md",
    "docs/eval/beta_2_3/README.md",
    *tuple(
        str(path.relative_to(REPO_ROOT))
        for path in sorted((REPO_ROOT / "docs/public").glob("*.md"))
    ),
    *tuple(
        str(path.relative_to(REPO_ROOT))
        for path in sorted((REPO_ROOT / "docs/research").glob("*.md"))
    ),
)
US_SPELLING_TERMS = (
    "behavior",
    "artifact",
    "artifacts",
    "stabilized",
    "stabilize",
    "stabilizes",
    "standardized",
    "generalization",
    "generalize",
    "operationalized",
    "operationalize",
    "operationalization",
    "summarize",
    "personalization",
    "license",
    "judgment",
    "judgments",
    "analyze",
    "normalized",
    "normalize",
    "organized",
    "organize",
    "center",
    "gray",
    "catalog",
    "modeling",
    "color",
    "materialize",
)


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def _markdown_prose_lines(text: str) -> list[tuple[int, str]]:
    prose_lines: list[tuple[int, str]] = []
    in_fence = False

    for line_number, line in enumerate(text.splitlines(), start=1):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        prose = "".join(
            segment for index, segment in enumerate(line.split("`")) if index % 2 == 0
        )
        prose = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", prose)
        prose = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", prose)
        prose_lines.append((line_number, prose))

    return prose_lines


def _is_allowed_public_spelling(relative_path: str, term: str, prose: str) -> bool:
    if relative_path != "README.md" or term.lower() != "license":
        return False

    normalized = prose.strip().lower()
    return normalized in {
        "## license",
        "apache-2.0. see license.",
    }


class ResearchModelContractTests(unittest.TestCase):
    def test_beta_notes_include_local_mermaid_diagrams(self) -> None:
        for path in BETA_NOTE_PATHS:
            text = _read(path)

            self.assertIn("## Diagram", text, path)
            self.assertIn("```mermaid", text, path)

    def test_public_markdown_uses_uk_english_outside_syntax(self) -> None:
        patterns = {
            term: re.compile(rf"\b{re.escape(term)}\b", flags=re.IGNORECASE)
            for term in US_SPELLING_TERMS
        }
        failures: list[str] = []

        for path in PUBLIC_MARKDOWN_PATHS:
            for line_number, prose in _markdown_prose_lines(_read(path)):
                for term, pattern in patterns.items():
                    if pattern.search(prose) and not _is_allowed_public_spelling(
                        path, term, prose
                    ):
                        failures.append(f"{path}:{line_number}: {term}")

        self.assertEqual([], failures)

    def test_pre_beta_2_4_contract_is_staged_and_source_bound(self) -> None:
        contract = _read(CONTRACT_PATH)

        for expected in (
            "Pre-Beta 2.4 Research Model Contract",
            "Status: `staged`",
            "`Beta 2.3`",
            "`pre-Beta 2.4`",
            "docs/eval/beta_2_3/",
            "staged contract is source-first",
            "source-first research claims",
            "manual eval workbench evidence from notebooks",
            "`POST /chat`",
            "`/chats/*`",
            "notebooks launched by `make notes`, `make notebook`, and `make nb`",
            "`.local/runtime_dbs/active/manual_evals.db`",
            "`.local/runtime_dbs/active/history.db`",
            "`pass` / `fail`",
            "source artefacts used",
            "Canonical pre-Beta 2.4 claims stay source-first and row/case-bound",
            "docs/eval/beta_2_4/",
        ):
            self.assertIn(expected, contract)

        for rejected in (
            "Non-OCR research pulses can use run-level",
            "final pulse verdict",
            "source artefact to row label to pulse verdict",
            "Pulse-level verdicts are not canonical rollups",
            "discarded run-level rollup hypothesis",
            "is not being carried forward as the next method",
            "Run-level verdicts are not canonical rollups",
        ):
            self.assertNotIn(rejected, contract)

    def test_current_truth_surfaces_name_the_staged_contract(self) -> None:
        for path in (
            "README.md",
            "docs/research/README.md",
            "docs/eval/README.md",
            "docs/governance/STATE.md",
            "docs/public/HYPOTHESIS.md",
        ):
            self.assertIn("pre-Beta 2.4", _read(path), path)

    def test_current_truth_surfaces_name_source_first_method_shape(self) -> None:
        expectations = {
            "README.md": "Source-first row and case evidence is the pre-Beta 2.4 method foundation",
            "docs/research/README.md": (
                "source-first row and case evidence is the method foundation"
            ),
            "docs/eval/README.md": (
                "source-first row and case evidence is the method foundation"
            ),
            "docs/governance/STATE.md": (
                "source-first row and case evidence is the pre-Beta 2.4 method foundation"
            ),
            "docs/public/HYPOTHESIS.md": (
                "source-first row and case evidence is the method shape"
            ),
        }

        for path, expected in expectations.items():
            self.assertIn(expected, _read(path), path)

    def test_active_contract_surfaces_do_not_expose_pulse_as_live_method(self) -> None:
        for path in (
            "README.md",
            CONTRACT_PATH,
            "docs/eval/README.md",
            "docs/governance/STATE.md",
            "docs/public/HYPOTHESIS.md",
        ):
            self.assertNotIn("pulse", _read(path).lower(), path)

    def test_research_index_and_manifest_include_the_contract(self) -> None:
        research_index = _read("docs/research/README.md")
        self.assertIn(
            "[Pre-Beta 2.4 research model contract]",
            research_index,
        )
        self.assertIn(Path(CONTRACT_PATH).name, research_index)

        manifest = json.loads(_read("docs/research/research-manifest.json"))
        artifact_paths = {artifact["path"] for artifact in manifest["artifacts"]}

        self.assertIn(CONTRACT_PATH, artifact_paths)

        labels = {artifact["label"] for artifact in manifest["artifacts"]}
        self.assertIn(
            "Fail-pressure method evidence (historical)",
            labels,
        )

    def test_fail_pressure_pulse_hypothesis_is_historical(self) -> None:
        pulse_hypothesis = _read(
            "docs/research/fail-pressure-pulse-hypothesis-2026-05-16.md"
        )
        normalized = " ".join(pulse_hypothesis.split())

        self.assertIn("Current disposition: `not carried forward`", pulse_hypothesis)
        self.assertIn("not the pre-Beta 2.4 forward path", normalized)

    def test_decision_log_supersedes_the_pulse_contract(self) -> None:
        decisions = _read("docs/governance/DECISIONS.md")

        self.assertIn("Current disposition: Superseded by `D-028`.", decisions)
        self.assertIn(
            "## D-028: Do not carry fail-pressure pulses into pre-Beta 2.4",
            decisions,
        )
        self.assertIn(
            "## D-041: Keep source-first workbench payloads free of run-level rollups",
            decisions,
        )

    def test_decision_log_records_human_led_refactor_method(self) -> None:
        decisions = _read("docs/governance/DECISIONS.md")
        state = _read("docs/governance/STATE.md")
        normalized_decisions = " ".join(decisions.split())

        for expected in (
            "## D-055: Record the refactor method as human-led",
            "- Human-led:",
            "The human lead made the scope decision to refactor Polinko",
            "one-kernel-at-a-time method",
        ):
            self.assertIn(expected, decisions)

        self.assertIn(
            "Codex executing implementation, validation, and Git flow",
            normalized_decisions,
        )

        for expected in (
            "Refactor method is human-led",
            "the human lead owns scope, method, acceptance, and go/no-go decisions",
            "cleanup proceeds one kernel at a time from clean synced `main`",
        ):
            self.assertIn(expected, state)

    def test_eval_map_keeps_manual_eval_workbench_sources_canonical(self) -> None:
        eval_map = _read("docs/eval/README.md")

        for expected in (
            "The manual eval workbench is the human-judged research workspace",
            "`make notes`",
            "shortcuts: `make notebook`, `make nb`",
            "default local path: `.local/notebooks/`",
            "`POST /chat`",
            "`/chats/*`",
            "`.local/runtime_dbs/active/manual_evals.db`",
            "manual eval workbench sources stay canonical inputs",
            "active manual eval workbench claims stay row/case-bound and source-first",
        ):
            self.assertIn(expected, eval_map)

    def test_source_first_schema_versions_are_documented(self) -> None:
        decisions = _read("docs/governance/DECISIONS.md")
        state = _read("docs/governance/STATE.md")
        eval_map = _read("docs/eval/README.md")

        for expected in (
            "## D-072: Version source-first manual eval payload boundaries",
            "`schema_version=polinko.manual_eval_source_first.v1`",
            "`schema_version=polinko.manual_evals_db.v1`",
        ):
            self.assertIn(expected, decisions)

        for expected in (
            "`schema_version=polinko.manual_eval_source_first.v1`",
            "`schema_version=polinko.manual_evals_db.v1`",
        ):
            self.assertIn(expected, state)
            self.assertIn(expected, eval_map)

    def test_api_smoke_covers_manual_eval_source_first_surfaces(self) -> None:
        decisions = _read("docs/governance/DECISIONS.md")
        state = _read("docs/governance/STATE.md")
        smoke = _read("tools/api_smoke.py")

        for expected in (
            "## D-073: Cover manual eval source-first data in API smoke",
            "`make api-smoke` checks `/manual-evals/surface`",
            "`/viz/pass-fail/data` without launching a browser",
            "`summary_unit=lane_summary`",
        ):
            self.assertIn(expected, decisions)

        for expected in (
            "`make api-smoke` includes non-browser checks for `/manual-evals/surface`",
            "`/viz/pass-fail/data`",
        ):
            self.assertIn(expected, state)

        for expected in (
            'path="/manual-evals/surface?max_runs=5&max_sessions=5"',
            'path="/viz/pass-fail/data?max_evals=5"',
            "SOURCE_FIRST_SCHEMA_VERSION",
            '"rollup_unit" in contract',
        ):
            self.assertIn(expected, smoke)

    def test_manual_eval_freshness_status_is_documented_and_guarded(self) -> None:
        decisions = _read("docs/governance/DECISIONS.md")
        state = _read("docs/governance/STATE.md")
        eval_map = _read("docs/eval/README.md")
        surface = _read("src/polinko/api/manual_evals_surface.py")
        smoke = _read("tools/api_smoke.py")

        for expected in (
            "## D-074: Surface manual eval warehouse freshness read-only",
            "`data_freshness` block",
            "`current`, `stale`, `unknown`, or `missing`",
            "## D-075: Compare freshness against manual eval import scope",
            "sessions count only when they have",
            "metadata exclude-prefixes are",
            "## D-076: Make manual eval warehouse refresh backup-first",
            "`make manual-evals-db-status`",
            "`.local_archive/manual-evals-db-refresh-*`",
            "## D-077: Report manual eval warehouse health read-only",
            "`make manual-evals-db-health`",
            "source coverage",
            "image resolution",
            "feedback status",
            "## D-078: Resolve manual eval images from local export archives",
            "`zip_path::member`",
            "archived bytes",
            "## D-079: Resolve manual eval images from tracked eval snapshots",
            "`docs/eval/`",
            "Curated eval evidence",
            "## D-080: Resolve manual eval screenshots from Dropbox sync roots",
            "macOS Dropbox",
            "historical source-name debt",
            "## D-081: Classify manual eval missing-image debt by source family",
            "source family",
            "text-fixture debt",
            "## D-082: Classify manual eval open feedback debt read-only",
            "same-session OCR presence",
            "not infer feedback-to-OCR links",
            "## D-083: List manual eval open feedback actionables read-only",
            "`make manual-evals-feedback-actionables`",
            "`schema_version=polinko.manual_eval_feedback_actionables.v1`",
            "## D-084: Cohort manual eval open feedback actionables read-only",
            "`make manual-evals-feedback-cohorts`",
            "`schema_version=polinko.manual_eval_feedback_cohorts.v1`",
            "## D-085: Filter manual eval feedback drilldowns by cohort read-only",
            "`COHORT=<cohort_id>`",
            "`ocr_retry_evidence`",
            "## D-086: Packet OCR retry candidates read-only before reruns",
            "`make manual-evals-ocr-retry-candidates`",
            "`schema_version=polinko.manual_eval_ocr_retry_candidates.v1`",
            "## D-087: Flag OCR retry packet readiness before reruns",
            "`schema_version=polinko.manual_eval_ocr_retry_candidates.v2`",
            "same-session OCR context",
            "## D-088: Verify OCR retry source candidates before closure",
            "`make manual-evals-ocr-retry-source-verification`",
            "`schema_version=polinko.manual_eval_ocr_retry_source_verification.v1`",
            "exact not-confirmed reasons",
            "## D-089: Drill into OCR retry source-history provenance read-only",
            "`make manual-evals-ocr-retry-source-provenance`",
            "`schema_version=polinko.manual_eval_ocr_retry_source_provenance.v1`",
            "source-history feedback messages",
            "## D-090: Packet OCR retry rerun inputs read-only",
            "`make manual-evals-ocr-retry-input-packet`",
            "`schema_version=polinko.manual_eval_ocr_retry_input_packet.v1`",
            "exact-link blocker state",
            "## D-091: Manifest OCR retry source artifacts before reruns",
            "`make manual-evals-ocr-retry-rerun-manifest`",
            "`schema_version=polinko.manual_eval_ocr_retry_rerun_manifest.v1`",
            "separate feedback-closure blocker state",
            "## D-092: Preview OCR retry rerun plans before execution",
            "`make manual-evals-ocr-retry-rerun-plan`",
            "`schema_version=polinko.manual_eval_ocr_retry_rerun_plan.v1`",
            "payload-only command preview",
            "## D-093: Shortlist OCR retry source artifacts before reruns",
            "`make manual-evals-ocr-retry-selection-review`",
            "`schema_version=polinko.manual_eval_ocr_retry_selection_review.v1`",
            "`rerun_input`, `curated_case`, or",
            "## D-094: Template OCR retry source-artifact decisions before reruns",
            "`make manual-evals-ocr-retry-selection-template`",
            "`schema_version=polinko.manual_eval_ocr_retry_selection_template.v1`",
            "`selected_action=undecided`",
            "## D-097: Materialize OCR retry decision drafts locally",
            "`make manual-evals-ocr-retry-selection-draft`",
            "`schema_version=polinko.manual_eval_ocr_retry_selection_decision_draft.v1`",
            "template fingerprints",
            "## D-095: Validate OCR retry source-artifact decisions before execution",
            "`make manual-evals-ocr-retry-selection-validate`",
            "`schema_version=polinko.manual_eval_ocr_retry_selection_validation.v1`",
            "missing, stale, duplicate, or mismatched selections",
            "## D-096: Preview OCR retry selection application before execution",
            "`make manual-evals-ocr-retry-selection-apply-preview`",
            "`schema_version=polinko.manual_eval_ocr_retry_selection_apply_preview.v1`",
            "validation is `ok`",
            "## D-100: Gate OCR retry execution readiness before execution",
            "`make manual-evals-ocr-retry-execution-readiness`",
            "`schema_version=polinko.manual_eval_ocr_retry_execution_readiness.v1`",
            "Execution remains a separate",
            "## D-102: Implement OCR retry execution as a local bundle first",
            "`make manual-evals-ocr-retry-execute`",
            "`CONFIRM=ocr-retry-execute`",
            "## D-103: Inspect OCR retry execution bundles before mutation gates",
            "`make manual-evals-ocr-retry-execution-report`",
            "`schema_version=polinko.manual_eval_ocr_retry_execution_report.v1`",
            "## D-104: Preview OCR retry feedback closure before applying it",
            "`make manual-evals-ocr-retry-feedback-closure-preview`",
            "`schema_version=polinko.manual_eval_ocr_retry_feedback_closure_preview.v1`",
            "## D-105: Design OCR retry feedback closure as backup-first apply",
            "CONFIRM=ocr-retry-feedback-closure-apply",
            ".local_archive/manual-evals-feedback-closure-apply-<timestamp>/",
            "## D-106: Implement OCR retry feedback closure as backup-first apply",
            "`schema_version=polinko.manual_eval_ocr_retry_feedback_closure_apply.v1`",
            "## D-107: Verify OCR retry feedback closure after apply",
            "`schema_version=polinko.manual_eval_ocr_retry_feedback_closure_apply_report.v1`",
            "## D-108: Restore OCR retry feedback closure from verified apply backups",
            "`schema_version=polinko.manual_eval_ocr_retry_feedback_closure_restore.v1`",
            "CONFIRM=ocr-retry-feedback-closure-restore",
        ):
            self.assertIn(expected, decisions)

        for expected in (
            "`data_freshness` status",
            "is visible without rebuilding",
            "local databases",
            "`data_freshness` compares source history counts",
            "against the manual eval",
            "import scope",
            "`make manual-evals-db-status` prints terminal-native freshness",
            "preserves an",
            "existing warehouse under `.local_archive/manual-evals-db-refresh-*`",
            "`make manual-evals-db-health` reports read-only source-quality",
            "missing image assets",
            "missing image debt by source family",
            "feedback-to-result links",
            "feedback debt by outcome",
            "`make manual-evals-feedback-actionables` prints a read-only",
            "`schema_version=polinko.manual_eval_feedback_actionables.v1`",
            "`make manual-evals-feedback-cohorts` prints read-only",
            "`schema_version=polinko.manual_eval_feedback_cohorts.v1`",
            "`COHORT=<cohort_id>`",
            "`OUTCOME=<outcome>`",
            "`LIMIT=<n>`",
            "`make manual-evals-ocr-retry-candidates` prints a read-only OCR",
            "`schema_version=polinko.manual_eval_ocr_retry_candidates.v2`",
            "read-only readiness flags",
            "`make manual-evals-ocr-retry-source-verification` prints a read-only",
            "`schema_version=polinko.manual_eval_ocr_retry_source_verification.v1`",
            "exact not-confirmed reasons",
            "`make manual-evals-ocr-retry-source-provenance` prints a read-only",
            "`schema_version=polinko.manual_eval_ocr_retry_source_provenance.v1`",
            "source-history feedback message",
            "exact OCR source/result message IDs",
            "`make manual-evals-ocr-retry-input-packet` prints a read-only",
            "`schema_version=polinko.manual_eval_ocr_retry_input_packet.v1`",
            "resolved image status",
            "exact-link blocker state",
            "`make manual-evals-ocr-retry-rerun-manifest` prints a read-only",
            "`schema_version=polinko.manual_eval_ocr_retry_rerun_manifest.v1`",
            "thumbnail dimensions",
            "separate feedback-closure blocker state",
            "`make manual-evals-ocr-retry-rerun-plan` prints a read-only",
            "`schema_version=polinko.manual_eval_ocr_retry_rerun_plan.v1`",
            "payload-only command previews",
            "`ARTIFACT_IDS=<artifact_id>`",
            "`make manual-evals-ocr-retry-selection-review` prints a read-only",
            "`schema_version=polinko.manual_eval_ocr_retry_selection_review.v1`",
            "collapse duplicate source image artifacts",
            "`rerun_input`, `curated_case`, or",
            "`make manual-evals-ocr-retry-selection-template` prints a read-only",
            "`schema_version=polinko.manual_eval_ocr_retry_selection_template.v1`",
            "candidate artifact IDs",
            "`selected_action=undecided`",
            "`make manual-evals-ocr-retry-selection-draft` writes a local",
            "`schema_version=polinko.manual_eval_ocr_retry_selection_decision_draft.v1`",
            ".local/manual_eval_decisions/ocr_retry_selection_draft.json",
            "template fingerprints",
            "`make manual-evals-ocr-retry-selection-validate` validates a local",
            "`schema_version=polinko.manual_eval_ocr_retry_selection_validation.v1`",
            "flags missing/stale/duplicate decisions",
            "`make manual-evals-ocr-retry-selection-apply-preview` prints a read-only",
            "`schema_version=polinko.manual_eval_ocr_retry_selection_apply_preview.v1`",
            "split valid decisions by `rerun_input`",
            "`make manual-evals-ocr-retry-execution-readiness` prints a read-only",
            "`schema_version=polinko.manual_eval_ocr_retry_execution_readiness.v1`",
            "requires apply-preview `state=ok`",
            "`make manual-evals-ocr-retry-execute` is the local-bundle OCR retry",
            "`CONFIRM=ocr-retry-execute`",
            ".local/manual_eval_runs/ocr_retry/",
            "`make manual-evals-ocr-retry-execution-report` inspects one local",
            "`schema_version=polinko.manual_eval_ocr_retry_execution_report.v1`",
            "no-warehouse-mutation boundary",
            "`make manual-evals-ocr-retry-feedback-closure-preview` previews feedback",
            "`schema_version=polinko.manual_eval_ocr_retry_feedback_closure_preview.v1`",
            "do not close feedback, write action-taken text",
            "`make manual-evals-ocr-retry-feedback-closure-apply` applies OCR retry",
            "`schema_version=polinko.manual_eval_ocr_retry_feedback_closure_apply.v1`",
            "`CONFIRM=ocr-retry-feedback-closure-apply`",
            "`make manual-evals-ocr-retry-feedback-closure-apply-report`",
            "`schema_version=polinko.manual_eval_ocr_retry_feedback_closure_apply_report.v1`",
            ".local_archive/manual-evals-feedback-closure-apply-<timestamp>/",
            "`make manual-evals-ocr-retry-feedback-closure-restore-preview`",
            "`make manual-evals-ocr-retry-feedback-closure-restore`",
            "`schema_version=polinko.manual_eval_ocr_retry_feedback_closure_restore.v1`",
            ".local_archive/manual-evals-feedback-closure-restore-<timestamp>/",
            "tracked `docs/eval/`",
            "Dropbox screenshot sync root",
            "historical source-name debt",
            "matching files inside `.zip`",
            "archives under configured image roots",
            "without extracting files",
        ):
            self.assertIn(expected, state)

        self.assertIn("read-only `data_freshness` status", eval_map)
        self.assertIn("evidence-bearing import scope", eval_map)
        self.assertIn("inspect freshness without mutation", eval_map)
        self.assertIn("`.local_archive/manual-evals-db-refresh-*`", eval_map)
        self.assertIn(
            "inspect warehouse health with `make manual-evals-db-health`", eval_map
        )
        self.assertIn("source family", eval_map)
        self.assertIn("open feedback debt", eval_map)
        self.assertIn("`make manual-evals-feedback-actionables`", eval_map)
        self.assertIn(
            "`schema_version=polinko.manual_eval_feedback_actionables.v1`",
            eval_map,
        )
        self.assertIn("`make manual-evals-feedback-cohorts`", eval_map)
        self.assertIn(
            "`schema_version=polinko.manual_eval_feedback_cohorts.v1`",
            eval_map,
        )
        self.assertIn(
            "`make manual-evals-feedback-actionables COHORT=ocr_retry_evidence`",
            eval_map,
        )
        self.assertIn("`COHORT=<cohort_id>`", eval_map)
        self.assertIn("`make manual-evals-ocr-retry-candidates`", eval_map)
        self.assertIn(
            "`schema_version=polinko.manual_eval_ocr_retry_candidates.v2`",
            eval_map,
        )
        self.assertIn("read-only readiness flags", eval_map)
        self.assertIn(
            "`make manual-evals-ocr-retry-source-verification`",
            eval_map,
        )
        self.assertIn(
            "`schema_version=polinko.manual_eval_ocr_retry_source_verification.v1`",
            eval_map,
        )
        self.assertIn("exact not-confirmed reasons", eval_map)
        self.assertIn(
            "`make manual-evals-ocr-retry-source-provenance`",
            eval_map,
        )
        self.assertIn(
            "`schema_version=polinko.manual_eval_ocr_retry_source_provenance.v1`",
            eval_map,
        )
        self.assertIn("source-history feedback message presence", eval_map)
        self.assertIn("exact OCR source/result message IDs", eval_map)
        self.assertIn(
            "`make manual-evals-ocr-retry-input-packet`",
            eval_map,
        )
        self.assertIn(
            "`schema_version=polinko.manual_eval_ocr_retry_input_packet.v1`",
            eval_map,
        )
        self.assertIn("resolved image status", eval_map)
        self.assertIn("exact-link blocker state", eval_map)
        self.assertIn(
            "`make manual-evals-ocr-retry-rerun-manifest`",
            eval_map,
        )
        self.assertIn(
            "`schema_version=polinko.manual_eval_ocr_retry_rerun_manifest.v1`",
            eval_map,
        )
        self.assertIn("thumbnail dimensions", eval_map)
        self.assertIn("separate feedback-closure blocker state", eval_map)
        self.assertIn("`make manual-evals-ocr-retry-rerun-plan`", eval_map)
        self.assertIn(
            "`schema_version=polinko.manual_eval_ocr_retry_rerun_plan.v1`",
            eval_map,
        )
        self.assertIn("payload-only command previews", eval_map)
        self.assertIn("`ARTIFACT_IDS=<artifact_id>`", eval_map)
        self.assertIn("`make manual-evals-ocr-retry-selection-review`", eval_map)
        self.assertIn(
            "`schema_version=polinko.manual_eval_ocr_retry_selection_review.v1`",
            eval_map,
        )
        self.assertIn("collapse duplicate source image artefacts", eval_map)
        self.assertIn("`rerun_input`, `curated_case`, or `context_only`", eval_map)
        self.assertIn("`make manual-evals-ocr-retry-selection-template`", eval_map)
        self.assertIn(
            "`schema_version=polinko.manual_eval_ocr_retry_selection_template.v1`",
            eval_map,
        )
        self.assertIn("candidate artefact IDs", eval_map)
        self.assertIn("`selected_action=undecided`", eval_map)
        self.assertIn("`make manual-evals-ocr-retry-selection-draft`", eval_map)
        self.assertIn(
            "`schema_version=polinko.manual_eval_ocr_retry_selection_decision_draft.v1`",
            eval_map,
        )
        self.assertIn("template fingerprints", eval_map)
        self.assertIn(
            "`make manual-evals-ocr-retry-selection-validate`",
            eval_map,
        )
        self.assertIn(
            "`schema_version=polinko.manual_eval_ocr_retry_selection_validation.v1`",
            eval_map,
        )
        self.assertIn("flags missing/stale/duplicate decisions", eval_map)
        self.assertIn(
            "`make manual-evals-ocr-retry-selection-apply-preview`",
            eval_map,
        )
        self.assertIn(
            "`schema_version=polinko.manual_eval_ocr_retry_selection_apply_preview.v1`",
            eval_map,
        )
        self.assertIn("split decisions by `rerun_input`", eval_map)
        self.assertIn(
            "`make manual-evals-ocr-retry-execution-readiness`",
            eval_map,
        )
        self.assertIn(
            "`schema_version=polinko.manual_eval_ocr_retry_execution_readiness.v1`",
            eval_map,
        )
        self.assertIn("separate explicit follow-up gate", eval_map)
        self.assertIn(
            "`make manual-evals-ocr-retry-execution-report RUN_DIR=<path>`",
            eval_map,
        )
        self.assertIn(
            "`schema_version=polinko.manual_eval_ocr_retry_execution_report.v1`",
            eval_map,
        )
        self.assertIn("no-warehouse-mutation", eval_map)
        self.assertIn(
            "`make manual-evals-ocr-retry-feedback-closure-preview RUN_DIR=<path>`",
            eval_map,
        )
        self.assertIn(
            "`schema_version=polinko.manual_eval_ocr_retry_feedback_closure_preview.v1`",
            eval_map,
        )
        self.assertIn("feedback status, action-taken text", eval_map)
        self.assertIn(
            "`make manual-evals-ocr-retry-feedback-closure-apply RUN_DIR=<path>",
            eval_map,
        )
        self.assertIn(
            "`schema_version=polinko.manual_eval_ocr_retry_feedback_closure_apply.v1`",
            eval_map,
        )
        self.assertIn(
            "`make manual-evals-ocr-retry-feedback-closure-apply-report RUN_DIR=<path>`",
            eval_map,
        )
        self.assertIn(
            "`schema_version=polinko.manual_eval_ocr_retry_feedback_closure_apply_report.v1`",
            eval_map,
        )
        self.assertIn("backup-first", eval_map)
        self.assertIn("feedback-closure apply is backup-first", eval_map)
        self.assertIn("`status`, `action_taken`, and `updated_at`", eval_map)
        self.assertIn(
            "`make manual-evals-ocr-retry-feedback-closure-restore-preview",
            eval_map,
        )
        self.assertIn(
            "`schema_version=polinko.manual_eval_ocr_retry_feedback_closure_restore.v1`",
            eval_map,
        )
        self.assertIn("pre-restore backup", eval_map)
        self.assertIn("without inferring links", eval_map)
        self.assertIn("matching files inside", eval_map)
        self.assertIn("tracked `docs/eval/` snapshots", eval_map)
        self.assertIn("Dropbox screenshot sync root", eval_map)
        self.assertIn("historical source-name debt", eval_map)
        self.assertIn("`.zip` archives", eval_map)

        for expected in (
            "MANUAL_EVALS_DB_SCHEMA_VERSION",
            "_exclude_prefixes_from_metadata",
            "_source_history_count_row",
            "count_scope",
            '"state": state',
            '"source_history_dbs": source_snapshots',
        ):
            self.assertIn(expected, surface)

        for expected in (
            "_validate_data_freshness_payload",
            '{"current", "stale", "unknown", "missing"}',
            '"schema_current" not in manual_evals_db',
        ):
            self.assertIn(expected, smoke)


if __name__ == "__main__":
    unittest.main()
