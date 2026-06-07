from __future__ import annotations

import argparse

from tools.manual_eval_cli_feedback_parser import (
    add_feedback_context_args,
    add_feedback_reclassify_args,
)
from tools.manual_eval_cli_ocr_retry_parser import (
    add_ocr_execution_args,
    add_ocr_retry_args,
)
from tools.manual_eval_cli_shared_parser import (
    add_common_report_args,
    add_local_artifact_args,
    add_output_filter_args,
)


def build_manual_evals_db_health_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Print read-only manual eval warehouse health signals.",
    )
    add_common_report_args(parser)
    add_feedback_context_args(parser)
    add_ocr_retry_args(parser)
    add_feedback_reclassify_args(parser)
    add_local_artifact_args(parser)
    add_ocr_execution_args(parser)
    add_output_filter_args(parser)
    return parser
