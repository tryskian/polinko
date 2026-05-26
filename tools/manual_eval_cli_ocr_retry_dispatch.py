from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.manual_eval_cli_dispatch_support import (
    FinishReport,
    optional_path,
    positive_limit,
)
from tools.manual_eval_ocr_retry_candidates import (
    build_ocr_retry_candidates_report,
    format_ocr_retry_candidates_report,
)
from tools.manual_eval_ocr_retry_execution_bundle_report import (
    build_ocr_retry_execution_bundle_report,
)
from tools.manual_eval_ocr_retry_execution_readiness import (
    build_ocr_retry_execution_readiness_report,
    format_ocr_retry_execution_readiness_report,
)
from tools.manual_eval_ocr_retry_execution_report import (
    format_ocr_retry_execution_bundle_report,
    format_ocr_retry_execution_report,
)
from tools.manual_eval_ocr_retry_execution_writer import (
    DEFAULT_OCR_RETRY_MODEL,
    DEFAULT_OCR_RETRY_PROMPT,
    write_ocr_retry_execution_bundle,
)
from tools.manual_eval_ocr_retry_feedback_closure_apply import (
    write_ocr_retry_feedback_closure_apply,
)
from tools.manual_eval_ocr_retry_feedback_closure_apply_report import (
    build_ocr_retry_feedback_closure_apply_report,
)
from tools.manual_eval_ocr_retry_feedback_closure_formatters import (
    format_ocr_retry_feedback_closure_apply_report,
    format_ocr_retry_feedback_closure_apply_verification_report,
    format_ocr_retry_feedback_closure_preview_report,
    format_ocr_retry_feedback_closure_restore_report,
)
from tools.manual_eval_ocr_retry_feedback_closure_preview import (
    build_ocr_retry_feedback_closure_preview_report,
)
from tools.manual_eval_ocr_retry_feedback_closure_restore import (
    build_ocr_retry_feedback_closure_restore_preview_report,
    write_ocr_retry_feedback_closure_restore,
)
from tools.manual_eval_ocr_retry_input_packet import (
    build_ocr_retry_input_packet_report,
    format_ocr_retry_input_packet_report,
)
from tools.manual_eval_ocr_retry_rerun_manifest import (
    build_ocr_retry_rerun_manifest_report,
    format_ocr_retry_rerun_manifest_report,
)
from tools.manual_eval_ocr_retry_rerun_plan import (
    build_ocr_retry_rerun_plan_report,
    format_ocr_retry_rerun_plan_report,
)
from tools.manual_eval_ocr_retry_selection_apply_preview import (
    build_ocr_retry_selection_apply_preview_report,
    format_ocr_retry_selection_apply_preview_report,
)
from tools.manual_eval_ocr_retry_selection_decision_draft import (
    format_ocr_retry_selection_decision_draft_report,
    write_ocr_retry_selection_decision_draft,
)
from tools.manual_eval_ocr_retry_selection_review import (
    build_ocr_retry_selection_review_report,
    format_ocr_retry_selection_review_report,
)
from tools.manual_eval_ocr_retry_selection_template import (
    build_ocr_retry_selection_template_report,
    format_ocr_retry_selection_template_report,
)
from tools.manual_eval_ocr_retry_selection_validation import (
    build_ocr_retry_selection_validation_report,
    format_ocr_retry_selection_validation_report,
)
from tools.manual_eval_ocr_retry_source_provenance import (
    build_ocr_retry_source_provenance_report,
    format_ocr_retry_source_provenance_report,
)
from tools.manual_eval_ocr_retry_source_verification import (
    build_ocr_retry_source_verification_report,
    format_ocr_retry_source_verification_report,
)


def handle_ocr_retry_pre_feedback_commands(
    *,
    args: Any,
    db_path: Path,
    finish: FinishReport,
) -> int | None:
    if args.ocr_retry_selection_draft:
        report = write_ocr_retry_selection_decision_draft(
            db_path=db_path,
            output_path=optional_path(args.output_path),
            force=bool(args.force),
            outcome=args.outcome or "partial",
            cohort=args.cohort or "ocr_retry_evidence",
            limit=positive_limit(args.limit),
            artifact_ids=args.artifact_id,
        )
        return finish(
            report,
            format_ocr_retry_selection_decision_draft_report,
            status_by_state={"written": 0},
            default_status=2,
        )

    if args.ocr_retry_selection_apply_preview:
        report = build_ocr_retry_selection_apply_preview_report(
            db_path=db_path,
            selection_path=optional_path(args.selection_path),
            outcome=args.outcome or "partial",
            cohort=args.cohort or "ocr_retry_evidence",
            limit=positive_limit(args.limit),
            artifact_ids=args.artifact_id,
        )
        return finish(report, format_ocr_retry_selection_apply_preview_report)

    if args.ocr_retry_execution_readiness:
        report = build_ocr_retry_execution_readiness_report(
            db_path=db_path,
            selection_path=optional_path(args.selection_path),
            outcome=args.outcome or "partial",
            cohort=args.cohort or "ocr_retry_evidence",
            limit=positive_limit(args.limit),
            artifact_ids=args.artifact_id,
        )
        return finish(report, format_ocr_retry_execution_readiness_report)

    if args.ocr_retry_execution_report:
        report = build_ocr_retry_execution_bundle_report(
            run_dir=optional_path(args.run_dir),
        )
        return finish(
            report,
            format_ocr_retry_execution_bundle_report,
            status_by_state={"error": 2},
        )

    if args.ocr_retry_feedback_closure_preview:
        report = build_ocr_retry_feedback_closure_preview_report(
            run_dir=optional_path(args.run_dir),
        )
        return finish(
            report,
            format_ocr_retry_feedback_closure_preview_report,
            status_by_state={"blocked": 2},
        )

    if args.ocr_retry_feedback_closure_apply:
        report = write_ocr_retry_feedback_closure_apply(
            db_path=db_path,
            run_dir=optional_path(args.run_dir),
            confirm_token=str(args.confirm or ""),
            backup_root=optional_path(args.backup_root),
        )
        return finish(
            report,
            format_ocr_retry_feedback_closure_apply_report,
            status_by_state={"applied": 0},
            default_status=2,
        )

    if args.ocr_retry_feedback_closure_apply_report:
        report = build_ocr_retry_feedback_closure_apply_report(
            db_path=db_path,
            run_dir=optional_path(args.run_dir),
        )
        return finish(
            report,
            format_ocr_retry_feedback_closure_apply_verification_report,
            status_by_state={"ok": 0},
            default_status=2,
        )

    if args.ocr_retry_feedback_closure_restore_preview:
        report = build_ocr_retry_feedback_closure_restore_preview_report(
            db_path=db_path,
            backup_dir=optional_path(args.backup_dir),
        )
        return finish(
            report,
            format_ocr_retry_feedback_closure_restore_report,
            status_by_state={"ok": 0},
            default_status=2,
        )

    if args.ocr_retry_feedback_closure_restore:
        report = write_ocr_retry_feedback_closure_restore(
            db_path=db_path,
            backup_dir=optional_path(args.backup_dir),
            confirm_token=str(args.confirm or ""),
            restore_root=optional_path(args.restore_root),
        )
        return finish(
            report,
            format_ocr_retry_feedback_closure_restore_report,
            status_by_state={"restored": 0},
            default_status=2,
        )

    return None


def handle_ocr_retry_post_feedback_commands(
    *,
    args: Any,
    db_path: Path,
    finish: FinishReport,
) -> int | None:
    if args.ocr_retry_execute:
        report = write_ocr_retry_execution_bundle(
            db_path=db_path,
            selection_path=optional_path(args.selection_path),
            confirm_token=str(args.confirm or ""),
            outcome=args.outcome or "partial",
            cohort=args.cohort or "ocr_retry_evidence",
            limit=positive_limit(args.limit),
            artifact_ids=args.artifact_id,
            execution_dir=optional_path(args.execution_dir),
            ocr_provider=str(args.ocr_provider or "scaffold"),
            ocr_model=str(args.ocr_model or DEFAULT_OCR_RETRY_MODEL),
            ocr_prompt=str(args.ocr_prompt or DEFAULT_OCR_RETRY_PROMPT),
        )
        return finish(
            report,
            format_ocr_retry_execution_report,
            status_by_state={"completed": 0, "failed": 1, "partial_failure": 1},
            default_status=2,
        )

    if args.ocr_retry_selection_validate:
        report = build_ocr_retry_selection_validation_report(
            db_path=db_path,
            selection_path=optional_path(args.selection_path),
            outcome=args.outcome or "partial",
            cohort=args.cohort or "ocr_retry_evidence",
            limit=positive_limit(args.limit),
            artifact_ids=args.artifact_id,
        )
        return finish(report, format_ocr_retry_selection_validation_report)

    if args.ocr_retry_selection_template:
        report = build_ocr_retry_selection_template_report(
            db_path=db_path,
            outcome=args.outcome or "partial",
            cohort=args.cohort or "ocr_retry_evidence",
            limit=positive_limit(args.limit),
            artifact_ids=args.artifact_id,
        )
        return finish(report, format_ocr_retry_selection_template_report)

    if args.ocr_retry_selection_review:
        report = build_ocr_retry_selection_review_report(
            db_path=db_path,
            outcome=args.outcome or "partial",
            cohort=args.cohort or "ocr_retry_evidence",
            limit=positive_limit(args.limit),
            artifact_ids=args.artifact_id,
        )
        return finish(report, format_ocr_retry_selection_review_report)

    if args.ocr_retry_rerun_plan:
        report = build_ocr_retry_rerun_plan_report(
            db_path=db_path,
            outcome=args.outcome or "partial",
            cohort=args.cohort or "ocr_retry_evidence",
            limit=positive_limit(args.limit),
            artifact_ids=args.artifact_id,
        )
        return finish(report, format_ocr_retry_rerun_plan_report)

    if args.ocr_retry_rerun_manifest:
        report = build_ocr_retry_rerun_manifest_report(
            db_path=db_path,
            outcome=args.outcome or "partial",
            cohort=args.cohort or "ocr_retry_evidence",
            limit=positive_limit(args.limit),
        )
        return finish(report, format_ocr_retry_rerun_manifest_report)

    if args.ocr_retry_input_packet:
        report = build_ocr_retry_input_packet_report(
            db_path=db_path,
            outcome=args.outcome or "partial",
            cohort=args.cohort or "ocr_retry_evidence",
            limit=positive_limit(args.limit),
        )
        return finish(report, format_ocr_retry_input_packet_report)

    if args.ocr_retry_source_provenance:
        report = build_ocr_retry_source_provenance_report(
            db_path=db_path,
            outcome=args.outcome or "partial",
            cohort=args.cohort or "ocr_retry_evidence",
            limit=positive_limit(args.limit),
        )
        return finish(report, format_ocr_retry_source_provenance_report)

    if args.ocr_retry_source_verification:
        report = build_ocr_retry_source_verification_report(
            db_path=db_path,
            outcome=args.outcome or "partial",
            cohort=args.cohort or "ocr_retry_evidence",
            limit=positive_limit(args.limit),
        )
        return finish(report, format_ocr_retry_source_verification_report)

    if args.ocr_retry_candidates:
        report = build_ocr_retry_candidates_report(
            db_path=db_path,
            outcome=args.outcome or "partial",
            cohort=args.cohort or "ocr_retry_evidence",
            limit=positive_limit(args.limit),
        )
        return finish(report, format_ocr_retry_candidates_report)

    return None
