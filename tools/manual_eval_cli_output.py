from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from typing import Any


ReportFormatter = Callable[[dict[str, Any]], str]


def emit_manual_eval_report(
    report: dict[str, Any],
    formatter: ReportFormatter,
    *,
    json_output: bool,
) -> None:
    if json_output:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(formatter(report))


def finish_manual_eval_report(
    report: dict[str, Any],
    formatter: ReportFormatter,
    *,
    json_output: bool,
    status_by_state: Mapping[str, int] | None = None,
    default_status: int = 0,
) -> int:
    emit_manual_eval_report(report, formatter, json_output=json_output)
    if status_by_state is None:
        return default_status
    return status_by_state.get(str(report.get("state") or ""), default_status)
