from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.manual_eval_cli_dispatch_support import FinishReport, optional_path
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


def handle_ocr_retry_feedback_closure_commands(
    *,
    args: Any,
    db_path: Path,
    finish: FinishReport,
) -> int | None:
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
