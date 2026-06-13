from __future__ import annotations

from typing import Any

from tools.manual_eval_ocr_retry_report_formatters import int_value, terminal_path_name


def format_ocr_retry_feedback_closure_preview_report(report: dict[str, Any]) -> str:
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    mutation = report.get("mutation_boundary")
    if not isinstance(mutation, dict):
        mutation = {}
    run_dir_name = terminal_path_name(report.get("run_dir"))

    lines = [
        "manual eval OCR retry feedback closure preview: "
        f"state={report.get('state', 'unknown')} "
        f"run={report.get('run_id') or 'unknown'} "
        f"bundle={report.get('bundle_state') or 'unknown'} "
        f"feedback={int_value(counts.get('feedback_items'))} "
        f"ready={int_value(counts.get('ready_feedback'))} "
        f"attention={int_value(counts.get('attention_feedback'))} "
        f"blocked={int_value(counts.get('blocked_feedback'))} "
        f"requests={int_value(counts.get('bundle_requests'))} "
        f"responses={int_value(counts.get('bundle_responses'))} "
        "requests_without_feedback_ids="
        f"{int_value(counts.get('requests_without_feedback_ids'))} "
        f"feedback_closure={mutation.get('feedback_closure') or 'none'} "
        f"warehouse_mutation={mutation.get('manual_eval_warehouse') or 'none'} "
        f"dir={run_dir_name}",
    ]
    closure_items = report.get("closure_items")
    if isinstance(closure_items, list) and closure_items:
        lines.append("closure_items:")
        for item in closure_items:
            if not isinstance(item, dict):
                continue
            evidence = item.get("evidence")
            evidence_count = len(evidence) if isinstance(evidence, list) else 0
            lines.append(
                "- "
                f"feedback={item.get('feedback_id') or 'unknown'} "
                f"state={item.get('state') or 'unknown'} "
                f"reason={item.get('reason') or 'unknown'} "
                f"proposed_status={item.get('proposed_feedback_status') or 'open'} "
                f"evidence={evidence_count} "
                f"mutation={item.get('mutation') or 'none'}"
            )
    blockers = report.get("preview_blockers")
    if isinstance(blockers, list) and blockers:
        lines.append("preview_blockers:")
        for blocker in blockers:
            if not isinstance(blocker, dict):
                continue
            lines.append(
                "- "
                f"code={blocker.get('code') or 'unknown'} "
                f"detail={blocker.get('detail') or ''}"
            )
    warnings = report.get("warnings")
    if isinstance(warnings, list) and warnings:
        lines.append("warnings:")
        lines.extend(f"- {str(item)}" for item in warnings)
    return "\n".join(lines)


def format_ocr_retry_feedback_closure_apply_report(report: dict[str, Any]) -> str:
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    mutation = report.get("mutation_boundary")
    if not isinstance(mutation, dict):
        mutation = {}
    backup = report.get("backup")
    if not isinstance(backup, dict):
        backup = {}
    run_dir_name = terminal_path_name(report.get("run_dir"))
    backup_dir_name = terminal_path_name(backup.get("dir"))

    lines = [
        "manual eval OCR retry feedback closure apply: "
        f"state={report.get('state', 'unknown')} "
        f"run={report.get('run_id') or 'unknown'} "
        f"bundle={report.get('bundle_state') or 'unknown'} "
        f"preview={report.get('preview_state') or 'unknown'} "
        f"feedback={int_value(counts.get('target_feedback_rows'))} "
        f"updated={int_value(counts.get('updated_feedback_rows'))} "
        f"skipped={int_value(counts.get('skipped_feedback_rows'))} "
        f"backups={int_value(counts.get('backups_written'))} "
        f"feedback_closure={mutation.get('feedback_closure') or 'none'} "
        f"warehouse_mutation={mutation.get('manual_eval_warehouse') or 'none'} "
        f"dir={run_dir_name} "
        f"backup_dir={backup_dir_name}",
    ]
    apply_items = report.get("apply_items")
    if isinstance(apply_items, list) and apply_items:
        lines.append("apply_items:")
        for item in apply_items:
            if not isinstance(item, dict):
                continue
            lines.append(
                "- "
                f"feedback={item.get('feedback_id') or 'unknown'} "
                f"status={item.get('status_before') or 'unknown'}"
                f"->{item.get('status_after') or 'unknown'} "
                f"evidence={int_value(item.get('evidence_count'))} "
                f"mutation={item.get('mutation') or 'none'}"
            )
    blockers = report.get("apply_blockers")
    if isinstance(blockers, list) and blockers:
        lines.append("apply_blockers:")
        for blocker in blockers:
            if not isinstance(blocker, dict):
                continue
            lines.append(
                "- "
                f"code={blocker.get('code') or 'unknown'} "
                f"detail={blocker.get('detail') or ''}"
            )
    if backup.get("restore_command"):
        lines.append("restore_hint=stop local server and restore from backup manifest")
    warnings = report.get("warnings")
    if isinstance(warnings, list) and warnings:
        lines.append("warnings:")
        lines.extend(f"- {str(item)}" for item in warnings)
    return "\n".join(lines)


def format_ocr_retry_feedback_closure_apply_verification_report(
    report: dict[str, Any],
) -> str:
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    backup = report.get("backup")
    if not isinstance(backup, dict):
        backup = {}
    manual_db = report.get("manual_evals_db")
    if not isinstance(manual_db, dict):
        manual_db = {}
    run_dir_name = terminal_path_name(report.get("run_dir"))
    backup_dir_name = terminal_path_name(backup.get("dir"))

    lines = [
        "manual eval OCR retry feedback closure apply report: "
        f"state={report.get('state', 'unknown')} "
        f"run={report.get('run_id') or 'unknown'} "
        f"feedback={int_value(counts.get('target_feedback_rows'))} "
        f"active_closed={int_value(counts.get('active_closed_feedback'))} "
        f"backup_open={int_value(counts.get('backup_open_feedback'))} "
        f"active_missing={int_value(counts.get('active_missing_feedback'))} "
        f"backup_missing={int_value(counts.get('backup_missing_feedback'))} "
        f"blockers={int_value(counts.get('report_blockers'))} "
        f"active_integrity={manual_db.get('integrity_check') or 'unknown'} "
        f"backup_integrity={backup.get('integrity_check') or 'unknown'} "
        f"dir={run_dir_name} "
        f"backup_dir={backup_dir_name}",
    ]
    feedback_rows = report.get("feedback_rows")
    if isinstance(feedback_rows, list) and feedback_rows:
        lines.append("feedback_rows:")
        for row in feedback_rows:
            if not isinstance(row, dict):
                continue
            lines.append(
                "- "
                f"feedback={row.get('feedback_id') or 'unknown'} "
                f"active={row.get('active_status') or 'unknown'} "
                f"backup={row.get('backup_status') or 'unknown'} "
                "action_taken="
                f"{'yes' if row.get('active_action_taken_present') else 'no'}"
            )
    blockers = report.get("report_blockers")
    if isinstance(blockers, list) and blockers:
        lines.append("report_blockers:")
        for blocker in blockers:
            if not isinstance(blocker, dict):
                continue
            lines.append(
                "- "
                f"code={blocker.get('code') or 'unknown'} "
                f"detail={blocker.get('detail') or ''}"
            )
    if backup.get("restore_command"):
        lines.append("restore_hint=stop local server and restore from backup manifest")
    warnings = report.get("warnings")
    if isinstance(warnings, list) and warnings:
        lines.append("warnings:")
        lines.extend(f"- {str(item)}" for item in warnings)
    return "\n".join(lines)


def format_ocr_retry_feedback_closure_restore_report(report: dict[str, Any]) -> str:
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    source_backup = report.get("source_backup")
    if not isinstance(source_backup, dict):
        source_backup = {}
    pre_restore_backup = report.get("pre_restore_backup")
    if not isinstance(pre_restore_backup, dict):
        pre_restore_backup = {}
    manual_db = report.get("manual_evals_db")
    if not isinstance(manual_db, dict):
        manual_db = {}
    mutation = report.get("mutation_boundary")
    if not isinstance(mutation, dict):
        mutation = {}
    backup_dir_name = terminal_path_name(source_backup.get("dir"))
    restore_dir_name = terminal_path_name(pre_restore_backup.get("dir"))

    lines = [
        "manual eval OCR retry feedback closure restore: "
        f"state={report.get('state', 'unknown')} "
        f"mode={report.get('mode') or 'unknown'} "
        f"run={report.get('run_id') or 'unknown'} "
        f"feedback={int_value(counts.get('target_feedback_rows'))} "
        f"active_closed={int_value(counts.get('active_closed_feedback'))} "
        f"backup_open={int_value(counts.get('backup_open_feedback'))} "
        f"restored={int_value(counts.get('restored_feedback_rows'))} "
        f"backups={int_value(counts.get('backups_written'))} "
        f"blockers={int_value(counts.get('restore_blockers'))} "
        f"active_integrity={manual_db.get('integrity_check') or 'unknown'} "
        f"backup_integrity={source_backup.get('integrity_check') or 'unknown'} "
        f"warehouse_mutation={mutation.get('manual_eval_warehouse') or 'none'} "
        f"backup_dir={backup_dir_name} "
        f"restore_dir={restore_dir_name}",
    ]
    feedback_rows = report.get("feedback_rows")
    if isinstance(feedback_rows, list) and feedback_rows:
        lines.append("feedback_rows:")
        for row in feedback_rows:
            if not isinstance(row, dict):
                continue
            lines.append(
                "- "
                f"feedback={row.get('feedback_id') or 'unknown'} "
                f"active={row.get('active_status') or 'unknown'} "
                f"backup={row.get('backup_status') or 'unknown'} "
                "action_taken="
                f"{'yes' if row.get('active_action_taken_present') else 'no'}"
            )
    restore_items = report.get("restore_items")
    if isinstance(restore_items, list) and restore_items:
        lines.append("restore_items:")
        for item in restore_items:
            if not isinstance(item, dict):
                continue
            lines.append(
                "- "
                f"feedback={item.get('feedback_id') or 'unknown'} "
                f"status={item.get('status_before') or 'unknown'}"
                f"->{item.get('status_after') or 'unknown'} "
                f"mutation={item.get('mutation') or 'none'}"
            )
    blockers = report.get("restore_blockers")
    if isinstance(blockers, list) and blockers:
        lines.append("restore_blockers:")
        for blocker in blockers:
            if not isinstance(blocker, dict):
                continue
            lines.append(
                "- "
                f"code={blocker.get('code') or 'unknown'} "
                f"detail={blocker.get('detail') or ''}"
            )
    warnings = report.get("warnings")
    if isinstance(warnings, list) and warnings:
        lines.append("warnings:")
        lines.extend(f"- {str(item)}" for item in warnings)
    return "\n".join(lines)
