from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPORT_SUBDIRS = (
    "ocr_focus_runs",
    "ocr_growth_batched_runs",
    "ocr_growth_stability_runs",
    "ocr_handwriting_benchmark_runs",
    "ocr_illustration_benchmark_runs",
    "ocr_stability_runs",
    "ocr_typed_benchmark_runs",
)
_RUN_ID_TIMESTAMP_RE = re.compile(r"^(?P<epoch>\d{9,})-r\d+$")
_BINARY_GATE_REPORT_ROOT = Path(".local/eval_reports")
_MANUAL_EVALS_DB_PATH = Path(".local/runtime_dbs/active/manual_evals.db")
_TRACKED_EVAL_ROOT = Path("docs/eval/beta_2_0")
_OCR_LANES = ("typed", "handwriting", "illustration")
_LANE_LABELS = {
    "typed": "text",
    "handwriting": "handwriting",
    "illustration": "illustration",
}
_TRACKED_LANE_SPECS = (
    {
        "lane_key": "ocr",
        "title": "OCR strict gate",
        "note": "Tracked binary gate snapshot for the mature OCR lane.",
        "pattern": "ocr-[0-9]*.json",
    },
    {
        "lane_key": "co_reasoning",
        "title": "Co-reasoning reliability",
        "note": "Promoted non-OCR lane carried in the tracked style surface.",
        "pattern": "style-[0-9]*.json",
    },
    {
        "lane_key": "response_behaviour",
        "title": "Response behaviour",
        "note": "Explicit uncertainty and claim-discipline gate snapshot.",
        "pattern": "response-behaviour-[0-9]*.json",
    },
    {
        "lane_key": "hallucination_boundary",
        "title": "Hallucination boundary",
        "note": "Grounding and uncertainty boundary snapshot.",
        "pattern": "hallucination-[0-9]*.json",
    },
    {
        "lane_key": "retrieval_grounding",
        "title": "Retrieval grounding",
        "note": "Grounding and no-leak retrieval gate snapshot.",
        "pattern": "retrieval-[0-9]*.json",
    },
    {
        "lane_key": "file_search",
        "title": "File search",
        "note": "Scoped file-search retrieval and leak boundary snapshot.",
        "pattern": "file-search-[0-9]*.json",
    },
)
_CAMERA_IMAGE_NAME_RX = re.compile(r"(?:^|[-_])(img|dsc)[_-]\d{3,}", re.IGNORECASE)
_SCREENSHOT_NAME_RX = re.compile(r"(?:^|[-_])screenshot(?:[-_]|$)", re.IGNORECASE)
_ILLUSTRATION_NAME_HINT_RX = re.compile(
    r"diagram|sketch|drawing|doodle|flow ?chart|flowchart|graph|whiteboard|wireframe|topolog|shape|node|edge|arrow",
    re.IGNORECASE,
)
_ILLUSTRATION_TEXT_HINT_RX = re.compile(
    r"diagram|flow ?chart|flowchart|graph|node|edge|arrow|axis|legend|figure|topology|trapezoid|prism",
    re.IGNORECASE,
)


def _normalize_text(value: Any, *, max_chars: int = 700) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1] + "..."


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def _latest_matching_json(root: Path, pattern: str) -> Path | None:
    candidates = sorted(path for path in root.glob(pattern) if path.is_file())
    if not candidates:
        return None
    return candidates[-1]


def _timestamp_ms(report: dict[str, Any], path: Path) -> int:
    run_id = str(report.get("run_id") or path.stem).strip()
    match = _RUN_ID_TIMESTAMP_RE.match(run_id)
    if match:
        try:
            return int(match.group("epoch")) * 1000
        except ValueError:
            pass

    generated_at = str(report.get("generated_at", "")).strip()
    if generated_at:
        normalized = generated_at.replace("Z", "+00:00")
        try:
            return int(datetime.fromisoformat(normalized).timestamp() * 1000)
        except ValueError:
            pass

    return int(path.stat().st_mtime * 1000)


def _report_paths(report_root: Path) -> list[Path]:
    paths: list[Path] = []
    for subdir in _REPORT_SUBDIRS:
        base = report_root / subdir
        if not base.is_dir():
            continue
        paths.extend(sorted(base.glob("*.json")))
    return paths


def _safe_int(value: Any, *, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _case_binary_outcome(case: dict[str, Any]) -> str:
    raw = str(
        case.get("gate_outcome")
        or case.get("binary_outcome")
        or case.get("outcome")
        or case.get("status")
        or ""
    ).strip().lower()
    if raw in {"pass", "passed", "ok", "success"}:
        return "pass"
    if raw in {"fail", "failed", "error"}:
        return "fail"
    return ""


def _binary_report_run_id(report: dict[str, Any], path: Path) -> str:
    return str(report.get("run_id") or path.stem).strip() or path.stem


def _case_lane(case: dict[str, Any], *, suite: str) -> str:
    explicit = str(case.get("lane") or "").strip().lower()
    if explicit in _OCR_LANES:
        return explicit

    suite_key = suite.lower()
    if "handwriting" in suite_key:
        return "handwriting"
    if "illustration" in suite_key:
        return "illustration"
    if "typed" in suite_key:
        return "typed"

    return _classify_ocr_history_lane(
        source_name=str(case.get("source_name") or case.get("image_path") or ""),
        extracted_text=str(case.get("extracted_text") or case.get("observed_text") or ""),
    )


def _expected_for_case(case: dict[str, Any]) -> str:
    must_contain = [str(item).strip() for item in case.get("must_contain", []) if str(item).strip()]
    must_contain_any = [str(item).strip() for item in case.get("must_contain_any", []) if str(item).strip()]
    must_appear_in_order = [
        str(item).strip() for item in case.get("must_appear_in_order", []) if str(item).strip()
    ]
    must_match_regex = [str(item).strip() for item in case.get("must_match_regex", []) if str(item).strip()]

    expected_parts: list[str] = []
    if must_contain:
        expected_parts.append("contain: " + " | ".join(must_contain[:4]))
    if must_contain_any:
        expected_parts.append("contain any: " + " | ".join(must_contain_any[:4]))
    if must_appear_in_order:
        expected_parts.append("ordered: " + " -> ".join(must_appear_in_order[:4]))
    if must_match_regex:
        expected_parts.append("regex: " + " | ".join(must_match_regex[:2]))

    if not expected_parts:
        return "(none)"
    return _normalize_text("; ".join(expected_parts), max_chars=360)


def _binary_gate_expected_for_case(case: dict[str, Any]) -> str:
    expected = _expected_for_case(case)
    raw_reasons = case.get("gate_reasons", [])
    if not isinstance(raw_reasons, list):
        raw_reasons = [raw_reasons]
    extra_reasons = case.get("reasons", [])
    raw_reasons += extra_reasons if isinstance(extra_reasons, list) else [extra_reasons]
    reasons = [
        str(item).strip()
        for item in raw_reasons
        if item is not None and str(item).strip()
    ]
    if reasons:
        expected = f"{expected}; gate: {' | '.join(reasons[:3])}"
    status = str(case.get("status") or "").strip()
    error = str(case.get("error") or "").strip()
    if status and status.upper() not in {"PASS", "FAIL"}:
        expected = f"{expected}; status={status}"
    if error:
        expected = f"{expected}; error={error}"
    return _normalize_text(expected, max_chars=420)


def _default_point(*, timestamp_ms: int | None = None) -> dict[str, Any]:
    return {
        "run_id": "n/a",
        "timestamp_ms": int(timestamp_ms or datetime.now(tz=timezone.utc).timestamp() * 1000),
        "label": "n/a",
        "pass": 0,
        "fail": 0,
        "errors": 0,
        "total": 0,
        "text": 0,
        "handwriting": 0,
        "illustration": 0,
        "source": "n/a",
    }


def _classify_ocr_history_lane(*, source_name: str, extracted_text: str) -> str:
    basename = Path(source_name or "").name.lower()
    sample = (extracted_text or "")[:1200]

    if _ILLUSTRATION_NAME_HINT_RX.search(basename) or _ILLUSTRATION_TEXT_HINT_RX.search(sample):
        return "illustration"

    lines = [line.strip() for line in sample.splitlines() if line.strip()]
    short_lines = sum(1 for line in lines if len(line) <= 36 and len(line.split()) <= 5)
    uppercase_lines = sum(
        1 for line in lines if any(ch.isalpha() for ch in line) and line.upper() == line
    )
    if len(lines) >= 4 and short_lines >= 4 and (
        uppercase_lines >= 2 or short_lines / max(len(lines), 1) >= 0.7
    ):
        return "illustration"

    if _SCREENSHOT_NAME_RX.search(basename):
        return "typed"
    if _CAMERA_IMAGE_NAME_RX.search(basename):
        return "handwriting"
    if basename.endswith((".jpg", ".jpeg", ".heic", ".heif")):
        return "handwriting"
    return "typed"


def _unixish_to_timestamp_ms(value: Any) -> int:
    try:
        raw = int(value or 0)
    except (TypeError, ValueError):
        return 0
    if raw and raw < 10_000_000_000:
        return raw * 1000
    return raw


def _tracked_updated_at(report: dict[str, Any], path: Path) -> str:
    for key in ("updated_at", "generated_at"):
        value = str(report.get(key) or "").strip()
        if value:
            return value

    timestamp_unix = _safe_int(report.get("timestamp_unix"))
    if timestamp_unix > 0:
        return datetime.fromtimestamp(timestamp_unix, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _tracked_report_counts(report: dict[str, Any]) -> tuple[int, int, int, int, int]:
    summary = report.get("summary")
    summary_dict = summary if isinstance(summary, dict) else {}
    cases = report.get("cases")
    case_list = cases if isinstance(cases, list) else []

    passed = _safe_int(summary_dict.get("passed", summary_dict.get("gate_passed", report.get("passed"))))
    failed = _safe_int(summary_dict.get("failed", summary_dict.get("gate_failed", report.get("failed"))))
    partial = _safe_int(summary_dict.get("partial", report.get("partial")))
    errors = _safe_int(summary_dict.get("errors", report.get("errors")))
    total = _safe_int(summary_dict.get("total", report.get("total_cases", report.get("total"))))

    if total <= 0:
        total = max(passed + failed + partial + errors, len(case_list))
    if total < passed + failed + partial + errors:
        total = passed + failed + partial + errors

    return passed, failed, partial, errors, total


def _build_tracked_lane_summaries(tracked_eval_root: Path | None) -> list[dict[str, Any]]:
    if tracked_eval_root is None or not tracked_eval_root.is_dir():
        return []

    summaries: list[dict[str, Any]] = []

    for spec in _TRACKED_LANE_SPECS:
        path = _latest_matching_json(tracked_eval_root, spec["pattern"])
        if path is None:
            continue
        report = _load_json(path)
        if report is None:
            continue
        passed, failed, partial, errors, total = _tracked_report_counts(report)
        summaries.append(
            {
                "lane_key": spec["lane_key"],
                "title": spec["title"],
                "note": spec["note"],
                "kind": "tracked_report",
                "pass": passed,
                "fail": failed,
                "partial": partial,
                "errors": errors,
                "total": total,
                "updated_at": _tracked_updated_at(report, path),
                "run_id": str(report.get("run_id") or "").strip(),
                "source": str(path),
            }
        )

    operator_burden_path = tracked_eval_root / "operator_burden_rows.json"
    operator_burden = _load_json(operator_burden_path)
    if operator_burden is not None:
        rows = operator_burden.get("rows")
        row_list = rows if isinstance(rows, list) else []
        passed = sum(
            1
            for row in row_list
            if isinstance(row, dict) and str(row.get("verdict") or "").strip().lower() == "pass"
        )
        failed = sum(
            1
            for row in row_list
            if isinstance(row, dict) and str(row.get("verdict") or "").strip().lower() == "fail"
        )
        retain = sum(
            1
            for row in row_list
            if isinstance(row, dict)
            and str(row.get("verdict") or "").strip().lower() == "fail"
            and str(row.get("failure_disposition") or "").strip().lower() == "retain"
        )
        evict = sum(
            1
            for row in row_list
            if isinstance(row, dict)
            and str(row.get("verdict") or "").strip().lower() == "fail"
            and str(row.get("failure_disposition") or "").strip().lower() == "evict"
        )
        summaries.append(
            {
                "lane_key": "operator_burden",
                "title": "Operator burden",
                "note": "Thin judged lane with post-fail retain and evict handling.",
                "kind": "row_lane",
                "pass": passed,
                "fail": failed,
                "partial": 0,
                "errors": 0,
                "total": len(row_list),
                "retain": retain,
                "evict": evict,
                "updated_at": _tracked_updated_at(operator_burden, operator_burden_path),
                "run_id": "",
                "source": str(operator_burden_path),
            }
        )

    return summaries


def _attach_lane_summaries(payload: dict[str, Any], tracked_eval_root: Path | None) -> dict[str, Any]:
    enriched = dict(payload)
    enriched["lane_summaries"] = _build_tracked_lane_summaries(tracked_eval_root)
    return enriched


def _status_counts(status: str) -> tuple[int, int, int]:
    normalized = status.strip().lower()
    if normalized in {"ok", "pass", "passed", "success", "complete", "completed"}:
        return 1, 0, 0
    if "error" in normalized:
        return 0, 0, 1
    return 0, 1, 0


def _outcome_counts(outcome: str) -> tuple[int, int, int, int]:
    normalized = outcome.strip().lower()
    if normalized in {"pass", "passed", "success"}:
        return 1, 0, 0, 0
    if normalized in {"fail", "failed"}:
        return 0, 1, 0, 0
    if normalized in {"partial", "mixed", "warn", "warning"}:
        return 0, 0, 1, 0
    return 0, 0, 0, 1


def _feedback_outcome(row: sqlite3.Row, *, status: str) -> str:
    feedback_count = int(row["feedback_count"] or 0)
    if feedback_count <= 0:
        passed, failed, errors = _status_counts(status)
        if passed:
            return "PASS"
        if failed:
            return "FAIL"
        if errors:
            return "ERROR"
        return "UNKNOWN"

    if int(row["feedback_fail_count"] or 0) > 0:
        return "FAIL"
    if int(row["feedback_other_count"] or 0) > 0:
        return "PARTIAL"
    if int(row["feedback_pass_count"] or 0) > 0:
        return "PASS"
    return "UNKNOWN"


def _feedback_expected(row: sqlite3.Row) -> str:
    feedback_count = int(row["feedback_count"] or 0)
    if feedback_count <= 0:
        return "(raw OCR status)"

    pass_count = int(row["feedback_pass_count"] or 0)
    fail_count = int(row["feedback_fail_count"] or 0)
    other_count = int(row["feedback_other_count"] or 0)
    note = _normalize_text(row["feedback_notes"] or "", max_chars=220)
    summary = f"session feedback: {pass_count} pass / {fail_count} fail"
    if other_count:
        summary += f" / {other_count} other"
    if note:
        summary += f"; notes: {note}"
    return summary


def _load_metadata(conn: sqlite3.Connection) -> dict[str, str]:
    try:
        rows = conn.execute("SELECT key, value FROM metadata").fetchall()
    except sqlite3.Error:
        return {}
    return {
        str(row["key"]): str(row["value"])
        for row in rows
        if str(row["key"] or "").strip()
    }


def _ocr_lane_for_row(row: sqlite3.Row) -> str:
    return _classify_ocr_history_lane(
        source_name=str(row["source_name"] or "").strip(),
        extracted_text=str(row["extracted_text"] or ""),
    )


def _point_from_ocr_row(row: sqlite3.Row, *, db_name: str) -> dict[str, Any]:
    lane = _ocr_lane_for_row(row)
    passed, failed, errors = _status_counts(str(row["status"] or ""))
    run_id_value = str(row["run_id"] or "").strip() or "n/a"
    return {
        "run_id": run_id_value,
        "timestamp_ms": _unixish_to_timestamp_ms(row["created_at"]),
        "label": str(row["source_run_id"] or run_id_value),
        "pass": passed,
        "fail": failed,
        "partial": 0,
        "errors": errors,
        "total": 1,
        "text": 1 if lane == "typed" else 0,
        "handwriting": 1 if lane == "handwriting" else 0,
        "illustration": 1 if lane == "illustration" else 0,
        "source": str(row["source_name"] or "").strip() or db_name,
        "era": str(row["era"] or ""),
        "point_kind": "ocr_status",
    }


def _feedback_note(row: sqlite3.Row) -> str:
    parts = [
        str(row["note"] or "").strip(),
        str(row["recommended_action"] or "").strip(),
        str(row["action_taken"] or "").strip(),
    ]
    return _normalize_text(" | ".join(part for part in parts if part), max_chars=360)


def _build_payload_from_manual_evals_db(
    db_path: Path,
    *,
    max_evals: int,
    max_runs: int,
    run_id: str | None = None,
) -> dict[str, Any] | None:
    if not db_path.is_file():
        return None

    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    except sqlite3.Error:
        return None

    conn.row_factory = sqlite3.Row
    metadata = _load_metadata(conn)

    try:
        rows = conn.execute(
            """
            SELECT *
            FROM (
              SELECT
                r.id,
                r.run_id,
                r.source_run_id,
                r.era,
                r.source_label,
                r.session_id,
                r.source_session_id,
                r.source_name,
                r.status,
                r.extracted_text,
                r.created_at,
                ia.source_filename,
                ia.resolved_path,
                COALESCE(fb.feedback_count, 0) AS feedback_count,
                COALESCE(fb.pass_count, 0) AS feedback_pass_count,
                COALESCE(fb.fail_count, 0) AS feedback_fail_count,
                COALESCE(fb.other_count, 0) AS feedback_other_count,
                fb.notes AS feedback_notes
              FROM ocr_runs r
              LEFT JOIN image_assets ia ON ia.id = r.image_asset_id
              LEFT JOIN (
                SELECT
                  session_id,
                  COUNT(*) AS feedback_count,
                  SUM(CASE WHEN lower(outcome) = 'pass' THEN 1 ELSE 0 END) AS pass_count,
                  SUM(CASE WHEN lower(outcome) = 'fail' THEN 1 ELSE 0 END) AS fail_count,
                  SUM(CASE WHEN lower(outcome) NOT IN ('pass', 'fail') THEN 1 ELSE 0 END) AS other_count,
                  GROUP_CONCAT(NULLIF(note, ''), ' | ') AS notes
                FROM feedback
                GROUP BY session_id
              ) fb ON fb.session_id = r.session_id
              ORDER BY r.created_at DESC, r.id DESC
              LIMIT ?
            )
            ORDER BY created_at ASC, id ASC
            """,
            (max_runs,),
        ).fetchall()
    except sqlite3.Error:
        conn.close()
        return None

    if not rows:
        conn.close()
        return None

    ocr_points = [_point_from_ocr_row(row, db_name=db_path.name) for row in rows]
    feedback_points: list[dict[str, Any]] = []
    feedback_eval_rows: list[dict[str, Any]] = []

    feedback_where = "WHERE s.ocr_runs_count > 0"
    feedback_params: list[Any] = []
    if run_id:
        feedback_where += """
              AND EXISTS (
                SELECT 1
                FROM ocr_runs filtered
                WHERE filtered.session_id = f.session_id
                  AND (filtered.run_id = ? OR filtered.source_run_id = ?)
              )
        """
        feedback_params.extend([run_id, run_id])

    try:
        feedback_rows = conn.execute(
            f"""
            WITH latest_ocr AS (
              SELECT *
              FROM (
                SELECT
                  r.*,
                  ia.source_filename,
                  ia.resolved_path,
                  ROW_NUMBER() OVER (
                    PARTITION BY r.session_id
                    ORDER BY r.created_at DESC, r.id DESC
                  ) AS rn
                FROM ocr_runs r
                LEFT JOIN image_assets ia ON ia.id = r.image_asset_id
              )
              WHERE rn = 1
            )
            SELECT *
            FROM (
              SELECT
                f.id,
                f.session_id,
                f.source_session_id,
                f.era,
                f.source_label,
                f.message_id,
                f.outcome,
                f.tags_json,
                f.note,
                f.recommended_action,
                f.action_taken,
                f.status AS feedback_status,
                f.created_at,
                s.title,
                latest_ocr.run_id,
                latest_ocr.source_run_id,
                latest_ocr.source_name,
                latest_ocr.extracted_text,
                latest_ocr.source_filename,
                latest_ocr.resolved_path
              FROM feedback f
              JOIN sessions s ON s.session_id = f.session_id
              LEFT JOIN latest_ocr ON latest_ocr.session_id = f.session_id
              {feedback_where}
              ORDER BY f.created_at DESC, f.id DESC
              LIMIT ?
            )
            ORDER BY created_at ASC, id ASC
            """,
            (*feedback_params, max(1, max_runs)),
        ).fetchall()
    except sqlite3.Error:
        feedback_rows = []

    for index, row in enumerate(feedback_rows):
        outcome = str(row["outcome"] or "UNKNOWN").strip().upper() or "UNKNOWN"
        passed, failed, partial, errors = _outcome_counts(outcome)
        lane_key = _ocr_lane_for_row(row)
        lane = _LANE_LABELS.get(lane_key, "other")
        note = _feedback_note(row)
        source_name = str(row["source_name"] or "").strip()
        source_path = str(row["resolved_path"] or "").strip()
        source_filename = str(row["source_filename"] or "").strip()
        title = str(row["title"] or row["source_session_id"] or row["session_id"]).strip()
        item = source_filename or Path(source_name).name or title
        run_id_value = str(row["run_id"] or f"feedback-{row['id']}").strip()
        feedback_points.append(
            {
                "run_id": f"feedback-{row['id']}",
                "timestamp_ms": _unixish_to_timestamp_ms(row["created_at"]),
                "label": title,
                "pass": passed,
                "fail": failed,
                "partial": partial,
                "errors": errors,
                "total": 1,
                "text": 1 if lane_key == "typed" else 0,
                "handwriting": 1 if lane_key == "handwriting" else 0,
                "illustration": 1 if lane_key == "illustration" else 0,
                "source": source_name or title,
                "era": str(row["era"] or ""),
                "point_kind": "manual_feedback",
                "outcome": outcome,
            }
        )
        feedback_eval_rows.append(
            {
                "row_key": f"feedback-{row['id']}::{run_id_value or index}",
                "item": item,
                "outcome": outcome,
                "expected": note or "(manual feedback)",
                "observed": _normalize_text(row["extracted_text"] or title, max_chars=520),
                "source_name": lane,
                "image_path": source_path or source_name,
                "lane": lane,
                "era": str(row["era"] or ""),
                "run_id": run_id_value,
                "source_run_id": str(row["source_run_id"] or run_id_value),
                "source_session_id": str(row["source_session_id"] or row["session_id"] or ""),
            }
        )

    feedback_eval_rows.sort(
        key=lambda row: (
            {"FAIL": 0, "PARTIAL": 1, "ERROR": 2, "PASS": 3}.get(str(row["outcome"]), 4),
            str(row["row_key"]),
        )
    )

    use_feedback_chart = bool(feedback_points) and run_id is None
    chart_mode = "feedback" if use_feedback_chart else "ocr_lanes"
    points = feedback_points if use_feedback_chart else ocr_points
    latest_point = points[-1] if points else _default_point()
    eval_rows: list[dict[str, Any]] = []

    eval_where = ""
    params: list[Any] = []
    if run_id:
        eval_where = "WHERE r.run_id = ? OR r.source_run_id = ?"
        params.extend([run_id, run_id])

    try:
        latest_rows = conn.execute(
            f"""
            SELECT
              r.id,
              r.run_id,
              r.source_run_id,
              r.era,
              r.source_label,
              r.session_id,
              r.source_session_id,
              r.source_name,
              r.status,
              r.extracted_text,
              r.created_at,
              ia.source_filename,
              ia.resolved_path,
              COALESCE(fb.feedback_count, 0) AS feedback_count,
              COALESCE(fb.pass_count, 0) AS feedback_pass_count,
              COALESCE(fb.fail_count, 0) AS feedback_fail_count,
              COALESCE(fb.other_count, 0) AS feedback_other_count,
              fb.notes AS feedback_notes
            FROM ocr_runs r
            LEFT JOIN image_assets ia ON ia.id = r.image_asset_id
            LEFT JOIN (
              SELECT
                session_id,
                COUNT(*) AS feedback_count,
                SUM(CASE WHEN lower(outcome) = 'pass' THEN 1 ELSE 0 END) AS pass_count,
                SUM(CASE WHEN lower(outcome) = 'fail' THEN 1 ELSE 0 END) AS fail_count,
                SUM(CASE WHEN lower(outcome) NOT IN ('pass', 'fail') THEN 1 ELSE 0 END) AS other_count,
                GROUP_CONCAT(NULLIF(note, ''), ' | ') AS notes
              FROM feedback
              GROUP BY session_id
            ) fb ON fb.session_id = r.session_id
            {eval_where}
            ORDER BY r.created_at DESC, r.id DESC
            LIMIT ?
            """,
            (*params, max_evals),
        ).fetchall()
    except sqlite3.Error:
        latest_rows = []

    for index, row in enumerate(latest_rows):
        source_name = str(row["source_name"] or "").strip()
        source_path = str(row["resolved_path"] or "").strip()
        source_filename = str(row["source_filename"] or "").strip()
        extracted_text = str(row["extracted_text"] or "")
        lane_key = _classify_ocr_history_lane(source_name=source_name, extracted_text=extracted_text)
        lane = _LANE_LABELS.get(lane_key, "other")
        item = source_filename or Path(source_name).name or str(row["source_run_id"] or row["run_id"])
        row_key = f"{row['run_id']}::{source_path or source_name or index}"
        eval_rows.append(
            {
                "row_key": row_key,
                "item": item,
                "outcome": _feedback_outcome(row, status=str(row["status"] or "")),
                "expected": _feedback_expected(row),
                "observed": _normalize_text(extracted_text, max_chars=520),
                "source_name": lane,
                "image_path": source_path or source_name,
                "lane": lane,
                "era": str(row["era"] or ""),
                "run_id": str(row["run_id"] or ""),
                "source_run_id": str(row["source_run_id"] or ""),
                "source_session_id": str(row["source_session_id"] or ""),
            }
        )

    if use_feedback_chart:
        eval_rows = feedback_eval_rows[:max_evals]

    conn.close()

    updated_at = metadata.get("generated_at_utc")
    if not updated_at:
        updated_at = datetime.fromtimestamp(
            int(latest_point["timestamp_ms"]) / 1000,
            tz=timezone.utc,
        ).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "updated_at": updated_at,
        "summary": {
            "pass": int(latest_point["pass"]),
            "fail": int(latest_point["fail"]),
            "partial": int(latest_point.get("partial", 0)),
            "errors": int(latest_point["errors"]),
            "total": int(latest_point["total"]),
            "run_id": str(latest_point["run_id"]),
            "source": str(latest_point["source"]),
            "timestamp_ms": int(latest_point["timestamp_ms"]),
            "text": int(latest_point["text"]),
            "handwriting": int(latest_point["handwriting"]),
            "illustration": int(latest_point["illustration"]),
            "point_kind": str(latest_point.get("point_kind", "")),
        },
        "summary_points": points[-2:],
        "points": points,
        "runs_total": len(points),
        "chart_mode": chart_mode,
        "fallback_ocr_runs_total": len(ocr_points),
        "evals": eval_rows,
    }


def _build_payload_from_binary_gate_reports(
    report_root: Path,
    *,
    max_evals: int,
    max_runs: int,
    run_id: str | None = None,
) -> dict[str, Any] | None:
    if not report_root.is_dir():
        return None

    candidate_paths = _report_paths(report_root)
    if not candidate_paths:
        candidate_paths = sorted(
            path
            for path in report_root.rglob("*.json")
            if "ocr" in path.as_posix().lower()
        )

    run_records: list[tuple[int, str, dict[str, Any], list[dict[str, Any]]]] = []

    for path in candidate_paths:
        report = _load_json(path)
        if report is None:
            continue

        report_run_id = _binary_report_run_id(report, path)
        if run_id is not None and report_run_id != run_id:
            continue

        cases = report.get("cases")
        case_list = cases if isinstance(cases, list) else []
        summary = report.get("summary")
        summary_dict = summary if isinstance(summary, dict) else {}

        case_pass = 0
        case_fail = 0
        text_count = 0
        handwriting_count = 0
        illustration_count = 0
        case_rows: list[dict[str, Any]] = []
        suite = path.parent.name
        timestamp_ms = _timestamp_ms(report, path)

        for index, raw_case in enumerate(case_list):
            if not isinstance(raw_case, dict):
                continue
            outcome = _case_binary_outcome(raw_case)
            if not outcome:
                continue
            if outcome == "pass":
                case_pass += 1
            else:
                case_fail += 1

            lane_key = _case_lane(raw_case, suite=suite)
            text_count += 1 if lane_key == "typed" else 0
            handwriting_count += 1 if lane_key == "handwriting" else 0
            illustration_count += 1 if lane_key == "illustration" else 0
            lane = _LANE_LABELS.get(lane_key, "other")
            item = str(raw_case.get("id") or raw_case.get("case_id") or "").strip() or "(unknown)"
            source_name = str(raw_case.get("source_name") or "").strip()
            image_path = str(raw_case.get("image_path") or raw_case.get("source_path") or "").strip()
            row_key = f"{report_run_id}::{item}::{source_name or image_path or index}"
            case_rows.append(
                {
                    "row_key": row_key,
                    "item": item,
                    "outcome": outcome.upper(),
                    "expected": _binary_gate_expected_for_case(raw_case),
                    "observed": _normalize_text(
                        raw_case.get("extracted_text") or raw_case.get("observed_text") or "",
                        max_chars=520,
                    ),
                    "source_name": lane,
                    "image_path": image_path or source_name,
                    "lane": lane,
                    "era": "binary_gates",
                    "run_id": report_run_id,
                    "source_run_id": report_run_id,
                    "source_session_id": str(raw_case.get("session_id") or ""),
                    "timestamp_ms": timestamp_ms,
                    "report_path": str(path),
                }
            )

        passed = _safe_int(
            summary_dict.get("gate_passed", summary_dict.get("passed")),
            default=case_pass,
        )
        failed = _safe_int(
            summary_dict.get("gate_failed", summary_dict.get("failed")),
            default=case_fail,
        )
        total = _safe_int(
            summary_dict.get("attempted", summary_dict.get("total_selected", summary_dict.get("total"))),
            default=passed + failed,
        )
        if total < passed + failed:
            total = passed + failed
        if total <= 0:
            continue

        if not any((text_count, handwriting_count, illustration_count)):
            text_count = total

        point = {
            "run_id": report_run_id,
            "timestamp_ms": timestamp_ms,
            "label": report_run_id,
            "pass": passed,
            "fail": failed,
            "partial": 0,
            "errors": 0,
            "total": total,
            "text": text_count,
            "handwriting": handwriting_count,
            "illustration": illustration_count,
            "source": suite,
            "era": "binary_gates",
            "point_kind": "binary_gate_report",
        }
        run_records.append((timestamp_ms, report_run_id, point, case_rows))

    if not run_records:
        return None

    run_records.sort(key=lambda item: (item[0], item[1]))
    if run_id is None:
        run_records = run_records[-max_runs:]
    points = [item[2] for item in run_records]
    all_eval_rows = [row for record in run_records for row in record[3]]
    latest_point = points[-1] if points else _default_point()
    all_eval_rows.sort(
        key=lambda row: (
            0 if row["outcome"] == "FAIL" else 1,
            -int(row.get("timestamp_ms") or 0),
            str(row["row_key"]),
        )
    )
    eval_rows = all_eval_rows[:max_evals]

    updated_at = datetime.fromtimestamp(
        int(latest_point["timestamp_ms"]) / 1000,
        tz=timezone.utc,
    ).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "updated_at": updated_at,
        "summary": {
            "pass": int(latest_point["pass"]),
            "fail": int(latest_point["fail"]),
            "partial": 0,
            "errors": 0,
            "total": int(latest_point["total"]),
            "run_id": str(latest_point["run_id"]),
            "source": str(latest_point["source"]),
            "timestamp_ms": int(latest_point["timestamp_ms"]),
            "text": int(latest_point["text"]),
            "handwriting": int(latest_point["handwriting"]),
            "illustration": int(latest_point["illustration"]),
            "point_kind": str(latest_point.get("point_kind", "")),
        },
        "summary_points": points[-2:],
        "points": points,
        "runs_total": len(points),
        "chart_mode": "binary_gates",
        "evals": eval_rows,
    }


def build_pass_fail_viz_payload(
    report_root: Path | None = None,
    *,
    max_evals: int = 140,
    db_path: Path | None = None,
    history_db_path: Path | None = None,
    max_history_runs: int = 120,
    run_id: str | None = None,
    tracked_eval_root: Path | None = _TRACKED_EVAL_ROOT,
) -> dict[str, Any]:
    _ = history_db_path
    if report_root is not None:
        payload = _build_payload_from_binary_gate_reports(
            report_root,
            max_evals=max(1, max_evals),
            max_runs=max(1, max_history_runs),
            run_id=run_id,
        )
        if payload is not None:
            return _attach_lane_summaries(payload, tracked_eval_root)
        return _attach_lane_summaries({
            "updated_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "summary": _default_point(),
            "summary_points": [],
            "points": [],
            "runs_total": 0,
            "evals": [],
        }, tracked_eval_root)

    if db_path is None:
        payload = _build_payload_from_binary_gate_reports(
            _BINARY_GATE_REPORT_ROOT,
            max_evals=max(1, max_evals),
            max_runs=max(1, max_history_runs),
            run_id=run_id,
        )
        if payload is not None:
            return _attach_lane_summaries(payload, tracked_eval_root)

    effective_db_path = db_path if db_path is not None else _MANUAL_EVALS_DB_PATH
    if report_root is None:
        payload = (
            _build_payload_from_manual_evals_db(
                effective_db_path,
                max_evals=max(1, max_evals),
                max_runs=max(1, max_history_runs),
                run_id=run_id,
            )
            if effective_db_path is not None
            else None
        )
        if payload is not None:
            return _attach_lane_summaries(payload, tracked_eval_root)
        return _attach_lane_summaries({
            "updated_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "summary": _default_point(),
            "summary_points": [],
            "points": [],
            "runs_total": 0,
            "evals": [],
        }, tracked_eval_root)


def render_pass_fail_viz_html(refresh_ms: int = 4000, chart_max_points: int = 20) -> str:
    html = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Polinko Eval Pulse</title>
  <style>
    :root {
      --paper: #f7f1e8;
      --ink: #171413;
      --muted: #6d6256;
      --panel: rgba(255, 251, 245, 0.78);
      --panel-line: rgba(84, 67, 49, 0.12);
      --track: rgba(110, 98, 85, 0.12);
      --pass: #1f8a70;
      --fail: #d05d3f;
      --error: #e1ae3b;
      --other: #d5ccc0;
      --lane-text: #6f9fc4;
      --lane-handwriting: #f07d23;
      --lane-illustration: #2d6d3e;
      --shadow: 0 24px 80px rgba(47, 35, 19, 0.08);
    }

    * { box-sizing: border-box; }

    html, body {
      margin: 0;
      min-height: 100%;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(73, 148, 128, 0.14), transparent 28%),
        radial-gradient(circle at top right, rgba(214, 120, 84, 0.14), transparent 30%),
        radial-gradient(circle at bottom center, rgba(225, 174, 59, 0.12), transparent 32%),
        linear-gradient(180deg, #fbf7f1 0%, #f4ede2 100%);
      font-family: "Avenir Next", "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    }

    body {
      padding: 26px;
    }

    .shell {
      max-width: 1400px;
      margin: 0 auto;
      display: grid;
      gap: 18px;
    }

    .hero {
      display: grid;
      grid-template-columns: minmax(280px, 1.2fr) minmax(260px, 0.8fr);
      gap: 18px;
      align-items: stretch;
    }

    .hero-copy,
    .hero-stat,
    .panel {
      background: var(--panel);
      backdrop-filter: blur(16px);
      border: 1px solid var(--panel-line);
      box-shadow: var(--shadow);
      border-radius: 30px;
    }

    .hero-copy {
      padding: 28px 30px 30px;
    }

    .eyebrow {
      font-size: 12px;
      letter-spacing: 0.18em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 14px;
    }

    .hero-copy h1 {
      margin: 0;
      font-family: "Iowan Old Style", "Palatino Linotype", "Book Antiqua", Georgia, serif;
      font-size: clamp(2.6rem, 5vw, 4.8rem);
      line-height: 0.95;
      font-weight: 600;
      max-width: 12ch;
    }

    .hero-copy p {
      margin: 18px 0 0;
      max-width: 56ch;
      font-size: 1rem;
      line-height: 1.55;
      color: var(--muted);
    }

    .hero-stat {
      padding: 28px 30px 30px;
      display: grid;
      align-content: space-between;
      min-height: 248px;
    }

    .status-pill {
      justify-self: start;
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 10px 14px;
      border-radius: 999px;
      background: rgba(23, 20, 19, 0.06);
      color: var(--ink);
      font-size: 13px;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }

    .status-pill::before {
      content: "";
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: var(--other);
      box-shadow: 0 0 0 6px rgba(213, 204, 192, 0.25);
    }

    .status-pill[data-state="steady"]::before {
      background: var(--pass);
      box-shadow: 0 0 0 6px rgba(31, 138, 112, 0.16);
    }

    .status-pill[data-state="watching"]::before {
      background: var(--error);
      box-shadow: 0 0 0 6px rgba(225, 174, 59, 0.18);
    }

    .status-pill[data-state="rough"]::before {
      background: var(--fail);
      box-shadow: 0 0 0 6px rgba(208, 93, 63, 0.16);
    }

    .metric-value {
      font-size: clamp(4rem, 10vw, 7.2rem);
      line-height: 0.9;
      letter-spacing: -0.05em;
      font-weight: 700;
      margin-top: 10px;
    }

    .metric-label {
      margin-top: 10px;
      font-size: 0.96rem;
      color: var(--muted);
    }

    .delta-label {
      margin-top: 8px;
      font-size: 0.92rem;
      color: var(--ink);
    }

    .panel {
      padding: 22px 22px 18px;
      position: relative;
      overflow: hidden;
    }

    .panel::after {
      content: "";
      position: absolute;
      inset: auto -10% -30% auto;
      width: 320px;
      height: 320px;
      background: radial-gradient(circle, rgba(31, 138, 112, 0.08), transparent 68%);
      pointer-events: none;
    }

    .panel-top {
      display: grid;
      grid-template-columns: minmax(220px, 1fr) auto;
      gap: 18px;
      align-items: start;
      margin-bottom: 12px;
      position: relative;
      z-index: 1;
    }

    .panel-title {
      margin: 0;
      font-size: 1.35rem;
      line-height: 1.1;
      font-weight: 600;
    }

    .panel-subtitle {
      margin: 8px 0 0;
      color: var(--muted);
      font-size: 0.95rem;
    }

    .legend {
      display: flex;
      gap: 14px;
      flex-wrap: wrap;
      margin-top: 14px;
    }

    .legend-item {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 0.9rem;
      color: var(--muted);
    }

    .legend-swatch {
      width: 11px;
      height: 11px;
      border-radius: 999px;
      display: inline-block;
    }

    .meta-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(140px, 1fr));
      gap: 10px;
      min-width: min(34vw, 360px);
    }

    .meta-card {
      padding: 12px 14px;
      border-radius: 18px;
      background: rgba(255, 255, 255, 0.46);
      border: 1px solid rgba(84, 67, 49, 0.08);
    }

    .meta-label {
      display: block;
      font-size: 11px;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 6px;
    }

    .meta-value {
      font-size: 0.96rem;
      line-height: 1.35;
      word-break: break-word;
    }

    .chart-frame {
      height: min(56vh, 520px);
      min-height: 340px;
      position: relative;
      z-index: 1;
    }

    #chart {
      width: 100%;
      height: 100%;
    }

    .chart-tip {
      position: absolute;
      display: none;
      pointer-events: none;
      max-width: 240px;
      padding: 12px 14px;
      border-radius: 16px;
      background: rgba(22, 19, 18, 0.9);
      color: #fffdf8;
      border: 1px solid rgba(255, 255, 255, 0.12);
      box-shadow: 0 18px 40px rgba(17, 14, 12, 0.24);
      font-size: 13px;
      line-height: 1.45;
      backdrop-filter: blur(12px);
      z-index: 5;
    }

    .chart-tip .tip-muted {
      color: rgba(255, 253, 248, 0.7);
    }

    .panel-bottom {
      display: grid;
      grid-template-columns: auto 1fr auto;
      gap: 10px;
      align-items: center;
      margin-top: 12px;
      font-size: 0.88rem;
      color: var(--muted);
      position: relative;
      z-index: 1;
    }

    .panel-bottom .window-copy {
      text-align: center;
    }

    .lane-panel {
      padding: 22px 22px 20px;
    }

    .lane-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 12px;
      margin-top: 14px;
      position: relative;
      z-index: 1;
    }

    .lane-card {
      padding: 14px 15px;
      border-radius: 20px;
      background: rgba(255, 255, 255, 0.52);
      border: 1px solid rgba(84, 67, 49, 0.08);
      display: grid;
      gap: 10px;
      align-content: start;
      min-height: 148px;
    }

    .lane-card-head {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 10px;
    }

    .lane-card-title {
      font-size: 0.96rem;
      font-weight: 600;
      color: var(--ink);
    }

    .lane-card-updated {
      font-size: 0.72rem;
      color: var(--muted);
      white-space: nowrap;
    }

    .lane-card-note {
      font-size: 0.82rem;
      line-height: 1.45;
      color: var(--muted);
    }

    .lane-card-state {
      justify-self: start;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 4px 10px;
      border-radius: 999px;
      font-size: 0.72rem;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      background: rgba(23, 20, 19, 0.06);
      color: var(--ink);
    }

    .lane-card-state::before {
      content: "";
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--other);
    }

    .lane-card-state[data-state="steady"]::before {
      background: var(--pass);
    }

    .lane-card-state[data-state="watching"]::before {
      background: var(--error);
    }

    .lane-card-state[data-state="rough"]::before {
      background: var(--fail);
    }

    .lane-card-metric {
      font-size: 1.18rem;
      line-height: 1.1;
      font-weight: 650;
      color: var(--ink);
    }

    .lane-card-detail,
    .lane-card-source {
      font-size: 0.76rem;
      color: var(--muted);
    }

    .lane-empty {
      display: none;
      margin-top: 14px;
      color: var(--muted);
      font-size: 0.88rem;
      position: relative;
      z-index: 1;
    }

    .eval-panel {
      margin-top: 18px;
      border-top: 1px solid var(--line);
      padding-top: 14px;
      position: relative;
      z-index: 1;
    }

    .eval-header {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 10px;
    }

    .eval-title {
      font-size: 0.96rem;
      font-weight: 600;
      color: var(--ink-soft);
    }

    .eval-subtitle {
      font-size: 0.82rem;
      color: var(--muted);
    }

    .eval-table-wrap {
      max-height: 34vh;
      overflow: auto;
      border-radius: 12px;
      border: 1px solid rgba(84, 67, 49, 0.12);
      background: rgba(255, 255, 255, 0.48);
    }

    table.eval-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.82rem;
      line-height: 1.35;
    }

    .eval-table th,
    .eval-table td {
      text-align: left;
      vertical-align: top;
      padding: 8px 10px;
      border-bottom: 1px solid rgba(84, 67, 49, 0.1);
    }

    .eval-table th {
      position: sticky;
      top: 0;
      background: rgba(244, 241, 233, 0.96);
      color: var(--ink-soft);
      font-weight: 600;
      z-index: 1;
    }

    .eval-table tr:last-child td {
      border-bottom: 0;
    }

    .eval-outcome {
      display: inline-block;
      min-width: 40px;
      text-align: center;
      font-weight: 700;
      letter-spacing: 0.02em;
      border-radius: 999px;
      padding: 3px 8px;
      font-size: 0.74rem;
    }

    .eval-outcome.pass {
      color: #114735;
      background: rgba(45, 109, 62, 0.16);
    }

    .eval-outcome.fail {
      color: #7a1d18;
      background: rgba(198, 58, 49, 0.15);
    }

    .eval-outcome.error {
      color: #5f4317;
      background: rgba(166, 122, 49, 0.16);
    }

    .eval-clip {
      display: inline-block;
      max-width: 100%;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .eval-path {
      font-family: "SFMono-Regular", Menlo, Monaco, Consolas, "Liberation Mono", monospace;
      font-size: 0.72rem;
      color: var(--muted);
      word-break: break-all;
    }

    .poll-status {
      font-size: 0.78rem;
      color: var(--muted);
    }

    .poll-status[data-mode="updating"] {
      color: #145a46;
    }

    .poll-status[data-mode="error"] {
      color: #7a1d18;
    }

    .eval-empty {
      padding: 14px 12px;
      color: var(--muted);
    }

    .eval-controls {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }

    .refresh-btn {
      border: 1px solid rgba(84, 67, 49, 0.2);
      background: rgba(255, 255, 255, 0.72);
      color: var(--ink-soft);
      border-radius: 999px;
      padding: 5px 12px;
      font-size: 0.78rem;
      line-height: 1;
      cursor: pointer;
    }

    .refresh-btn:disabled {
      opacity: 0.55;
      cursor: wait;
    }

    @media (max-width: 980px) {
      body { padding: 16px; }
      .hero,
      .panel-top {
        grid-template-columns: 1fr;
      }
      .meta-grid {
        min-width: 0;
      }
      .chart-frame {
        height: 48vh;
        min-height: 300px;
      }
    }
  </style>
  <script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <div class="hero-copy">
        <div class="eyebrow">Polinko Eval Pulse</div>
        <h1>See the balance move.</h1>
        <p>
          A live window for the active eval lane, with tracked snapshots from
          the wider evidence map. Deep detail stays in the database; this page
          is the heartbeat and the lane overview.
        </p>
      </div>

      <div class="hero-stat">
        <div class="status-pill" id="healthState" data-state="warming">warming up</div>
        <div>
          <div class="metric-value" id="passRate">0%</div>
          <div class="metric-label" id="metricLabel">pass rate right now</div>
          <div class="delta-label" id="deltaLabel">Waiting for the first live window.</div>
        </div>
      </div>
    </section>

    <section class="panel lane-panel">
      <div class="panel-top">
        <div>
          <h2 class="panel-title">Tracked Lane Snapshots</h2>
          <p class="panel-subtitle">
            The chart stays on the active window. These cards keep the broader
            Polinko evidence surface visible from tracked eval artifacts.
          </p>
        </div>
      </div>
      <div class="lane-grid" id="laneSummaries"></div>
      <div class="lane-empty" id="laneEmpty">No tracked lane snapshots yet.</div>
    </section>

    <section class="panel">
      <div class="panel-top">
        <div>
          <h2 class="panel-title" id="chartTitle">Current strict gate window</h2>
          <p class="panel-subtitle" id="chartSubtitle">Bucketed PASS/FAIL gate reports from the active lane with FAIL visible.</p>
          <div class="legend" id="chartLegend" aria-label="chart legend">
            <span class="legend-item"><span class="legend-swatch" style="background: var(--fail)"></span>fail</span>
            <span class="legend-item"><span class="legend-swatch" style="background: var(--pass)"></span>pass</span>
          </div>
        </div>

        <div class="meta-grid">
          <div class="meta-card">
            <span class="meta-label">Latest Bucket</span>
            <span class="meta-value" id="runId">n/a</span>
          </div>
          <div class="meta-card">
            <span class="meta-label" id="latestMixLabel">Current Signal</span>
            <span class="meta-value" id="latestMix">0 fail · 0 pass</span>
          </div>
          <div class="meta-card">
            <span class="meta-label">Window</span>
            <span class="meta-value" id="windowLabel">Last __DEFAULT_MAX_CHART_POINTS__ buckets</span>
          </div>
          <div class="meta-card">
            <span class="meta-label">Updated</span>
            <span class="meta-value" id="updatedAt">n/a</span>
          </div>
        </div>
      </div>

      <div class="chart-frame">
        <div id="chart"></div>
        <div id="chartTip" class="chart-tip"></div>
      </div>

      <div class="panel-bottom">
        <span>older</span>
        <span class="window-copy" id="windowCopy">bucketed binary gate report history</span>
        <span>now</span>
      </div>

      <div class="eval-panel" aria-live="polite">
        <div class="eval-header">
          <div class="eval-title">Latest Eval Rows</div>
          <div class="eval-controls">
            <button class="refresh-btn" id="refreshNow" type="button">Refresh</button>
            <div class="poll-status" id="pollStatus">update mode: post-batch/manual</div>
          </div>
        </div>
        <div class="eval-subtitle" id="evalSubtitle">fail-first gate rows · observed output · source path</div>
        <div class="eval-table-wrap">
          <table class="eval-table">
            <thead>
              <tr>
                <th>outcome</th>
                <th>lane</th>
                <th>item</th>
                <th>expected</th>
                <th>observed</th>
                <th>path</th>
              </tr>
            </thead>
            <tbody id="evalRows"></tbody>
          </table>
          <div class="eval-empty" id="evalEmpty">No eval rows yet.</div>
        </div>
      </div>
    </section>
  </main>

  <script>
    const REFRESH_MS = __REFRESH_MS__;
    const DEFAULT_MAX_CHART_POINTS = __DEFAULT_MAX_CHART_POINTS__;
    const dataUrl = '/viz/pass-fail/data';
    const state = { payload: null, chartMaxPoints: DEFAULT_MAX_CHART_POINTS };
    let inFlight = false;

    const passRateEl = document.getElementById('passRate');
    const deltaLabelEl = document.getElementById('deltaLabel');
    const healthStateEl = document.getElementById('healthState');
    const runIdEl = document.getElementById('runId');
    const chartTitleEl = document.getElementById('chartTitle');
    const chartSubtitleEl = document.getElementById('chartSubtitle');
    const chartLegendEl = document.getElementById('chartLegend');
    const metricLabelEl = document.getElementById('metricLabel');
    const latestMixLabelEl = document.getElementById('latestMixLabel');
    const latestMixEl = document.getElementById('latestMix');
    const windowLabelEl = document.getElementById('windowLabel');
    const windowCopyEl = document.getElementById('windowCopy');
    const updatedEl = document.getElementById('updatedAt');
    const pollStatusEl = document.getElementById('pollStatus');
    const refreshNowEl = document.getElementById('refreshNow');
    const evalRowsEl = document.getElementById('evalRows');
    const evalEmptyEl = document.getElementById('evalEmpty');
    const evalSubtitleEl = document.getElementById('evalSubtitle');
    const laneSummariesEl = document.getElementById('laneSummaries');
    const laneEmptyEl = document.getElementById('laneEmpty');

    function setPollStatus(text, mode = '') {
      if (!pollStatusEl) return;
      if (mode) {
        pollStatusEl.dataset.mode = mode;
      } else {
        pollStatusEl.removeAttribute('data-mode');
      }
      pollStatusEl.textContent = text;
    }

    function escapeHtml(value) {
      return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
    }

    function shorten(text, maxLen = 140) {
      const value = String(text ?? '').trim();
      if (!value) return '(none)';
      if (value.length <= maxLen) return value;
      return `${value.slice(0, maxLen - 1)}…`;
    }

    function leafName(path) {
      const value = String(path || '').trim();
      if (!value) return '(none)';
      const bits = value.split('/');
      return bits[bits.length - 1] || value;
    }

    function formatLaneSnapshotUpdated(value) {
      if (!value) return 'updated n/a';
      const direct = new Date(value);
      if (!Number.isNaN(direct.getTime())) {
        return `updated ${direct.toLocaleDateString([], { month: 'short', day: 'numeric' })}`;
      }
      const numeric = Number(value);
      if (!Number.isNaN(numeric) && numeric > 0) {
        const date = new Date(numeric < 10_000_000_000 ? numeric * 1000 : numeric);
        if (!Number.isNaN(date.getTime())) {
          return `updated ${date.toLocaleDateString([], { month: 'short', day: 'numeric' })}`;
        }
      }
      return `updated ${String(value)}`;
    }

    function normalizePoint(point, fallbackIndex = 0) {
      const pass = Number(point?.pass || 0);
      const fail = Number(point?.fail || 0);
      const partial = Number(point?.partial || 0);
      const errors = Number(point?.errors || 0);
      const text = Number(point?.text ?? point?.typed ?? 0);
      const handwriting = Number(point?.handwriting || 0);
      const illustration = Number(point?.illustration || 0);
      const explicitTotal = Number(point?.total || 0);
      const measuredTotal = pass + fail + partial + errors;
      const laneTotal = text + handwriting + illustration;
      const total = Math.max(explicitTotal, measuredTotal, laneTotal, 1);
      const passRate = total > 0 ? pass / total : 0;
      return {
        run_id: point?.run_id || `run-${fallbackIndex + 1}`,
        label: point?.label || point?.run_id || `run-${fallbackIndex + 1}`,
        pass,
        fail,
        partial,
        errors,
        total,
        text,
        handwriting,
        illustration,
        timestamp_ms: Number(point?.timestamp_ms || 0),
        point_kind: point?.point_kind || '',
        outcome: point?.outcome || '',
        passRate,
      };
    }

    function formatPct(value) {
      return `${(value * 100).toFixed(1)}%`;
    }

    function formatPtsDelta(current, previous) {
      const delta = (current - previous) * 100;
      const sign = delta > 0 ? '+' : '';
      return `${sign}${delta.toFixed(1)} pts vs previous`;
    }

    function formatTimestamp(value) {
      if (!value) return 'n/a';
      const direct = new Date(value);
      if (!Number.isNaN(direct.getTime())) return direct.toLocaleTimeString([], {hour: 'numeric', minute: '2-digit', second: '2-digit'});
      const parsed = Date.parse(value);
      if (Number.isNaN(parsed)) return 'n/a';
      return new Date(parsed).toLocaleTimeString([], {hour: 'numeric', minute: '2-digit', second: '2-digit'});
    }

    function clipId(runId) {
      return `clip-${String(runId || 'run').replace(/[^a-zA-Z0-9_-]/g, '_')}`;
    }

    function formatBucketLabel(startMs, endMs, runCount = 1) {
      if (!endMs) return runCount > 1 ? `${runCount} runs` : '1 run';
      const start = new Date(startMs || endMs);
      const end = new Date(endMs);
      const endText = Number.isNaN(end.getTime())
        ? 'recent'
        : end.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
      if (runCount <= 1 || Number.isNaN(start.getTime())) {
        return `${endText} · ${runCount} run`;
      }
      const sameHour = start.getHours() === end.getHours() && start.getDate() === end.getDate();
      const startText = sameHour
        ? start.toLocaleTimeString([], { minute: '2-digit' })
        : start.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
      return `${startText}-${endText} · ${runCount} runs`;
    }

    function bucketPoints(points, desiredBuckets = DEFAULT_MAX_CHART_POINTS) {
      if (!points.length) return [];
      if (points.length <= desiredBuckets) {
        return points.map((point, index) => ({
          ...point,
          run_id: point.run_id || `bucket-${index + 1}`,
          label: formatBucketLabel(point.timestamp_ms, point.timestamp_ms, 1),
          runCount: 1
        }));
      }

      const bucketSize = Math.max(1, Math.ceil(points.length / desiredBuckets));
      const buckets = [];
      for (let startIndex = 0; startIndex < points.length; startIndex += bucketSize) {
        const chunk = points.slice(startIndex, startIndex + bucketSize);
        const first = chunk[0];
        const last = chunk.at(-1);
        const pass = chunk.reduce((sum, point) => sum + point.pass, 0);
        const fail = chunk.reduce((sum, point) => sum + point.fail, 0);
        const partial = chunk.reduce((sum, point) => sum + point.partial, 0);
        const errors = chunk.reduce((sum, point) => sum + point.errors, 0);
        const total = chunk.reduce((sum, point) => sum + point.total, 0);
        const text = chunk.reduce((sum, point) => sum + point.text, 0);
        const handwriting = chunk.reduce((sum, point) => sum + point.handwriting, 0);
        const illustration = chunk.reduce((sum, point) => sum + point.illustration, 0);
        buckets.push({
          run_id: `bucket-${buckets.length + 1}-${last?.run_id || startIndex + 1}`,
          label: formatBucketLabel(first?.timestamp_ms || 0, last?.timestamp_ms || 0, chunk.length),
          pass,
          fail,
          partial,
          errors,
          total: Math.max(total, 1),
          text,
          handwriting,
          illustration,
          timestamp_ms: Number(last?.timestamp_ms || 0),
          passRate: total > 0 ? pass / total : 0,
          runCount: chunk.length
        });
      }
      return buckets;
    }

    function computeHealthState(rate, total) {
      if (!total) return { key: 'warming', label: 'warming up' };
      if (rate >= 0.95) return { key: 'steady', label: 'steady' };
      if (rate >= 0.8) return { key: 'watching', label: 'watching' };
      return { key: 'rough', label: 'rough' };
    }

    function computeFailState(rate, total) {
      if (!total) return { key: 'warming', label: 'warming up' };
      if (rate >= 0.35) return { key: 'rough', label: 'fail signal' };
      if (rate >= 0.1) return { key: 'watching', label: 'watch list' };
      return { key: 'steady', label: 'mostly clean' };
    }

    function computeLaneSnapshotState(lane) {
      const total = Number(lane?.total || 0);
      const fail = Number(lane?.fail || 0);
      const partial = Number(lane?.partial || 0);
      const errors = Number(lane?.errors || 0);
      const pressure = total > 0 ? (fail + partial + errors) / total : 0;
      return computeFailState(pressure, total);
    }

    function sumPoints(points) {
      return points.reduce((acc, point) => ({
        pass: acc.pass + point.pass,
        fail: acc.fail + point.fail,
        partial: acc.partial + point.partial,
        errors: acc.errors + point.errors,
        total: acc.total + point.total,
      }), { pass: 0, fail: 0, partial: 0, errors: 0, total: 0 });
    }

    function setLegend(items) {
      if (!chartLegendEl) return;
      chartLegendEl.innerHTML = items.map(item => `
        <span class="legend-item"><span class="legend-swatch" style="background: ${item.color}"></span>${item.label}</span>
      `).join('');
    }

    function renderSummary(payload) {
      const chartMode = payload?.chart_mode || 'ocr_lanes';
      const isBinaryGateMode = chartMode === 'binary_gates';
      const isFeedbackMode = chartMode === 'feedback';
      const isOutcomeMode = isBinaryGateMode || isFeedbackMode;
      const rawPoints = (payload.points || []).map(normalizePoint);
      const bucketedPoints = bucketPoints(rawPoints, state.chartMaxPoints);
      const latestBucket = bucketedPoints.at(-1) || normalizePoint(payload.summary || {});
      const summaryPoints = Array.isArray(payload.summary_points)
        ? payload.summary_points.map(normalizePoint)
        : [];
      const latestSummary = isOutcomeMode
        ? latestBucket
        : (summaryPoints.at(-1) || normalizePoint(payload.summary || latestBucket));
      const previousSummary = isOutcomeMode
        ? (bucketedPoints.length > 1 ? bucketedPoints.at(-2) : null)
        : (summaryPoints.length > 1 ? summaryPoints.at(-2) : null);
      const windowSummary = sumPoints(rawPoints);
      const failPressure = windowSummary.total > 0
        ? (windowSummary.fail + windowSummary.partial + windowSummary.errors) / windowSummary.total
        : 0;
      const health = isOutcomeMode
        ? computeFailState(failPressure, windowSummary.total)
        : computeHealthState(latestSummary.passRate, latestSummary.total);

      if (isBinaryGateMode) {
        chartTitleEl.textContent = 'Current strict gate window';
        chartSubtitleEl.textContent = 'Bucketed PASS/FAIL gate reports from the active lane; FAIL is the signal to inspect.';
        metricLabelEl.textContent = 'fail rate in live gate window';
        latestMixLabelEl.textContent = 'Current Signal';
        windowCopyEl.textContent = 'bucketed strict gate history';
        if (evalSubtitleEl) {
          evalSubtitleEl.textContent = 'fail-first gate rows · observed output · source path';
        }
        setLegend([
          { label: 'fail', color: 'var(--fail)' },
          { label: 'pass', color: 'var(--pass)' },
        ]);
      } else if (isFeedbackMode) {
        chartTitleEl.textContent = 'Current evaluated window';
        chartSubtitleEl.textContent = 'Bucketed manual eval outcomes from the active lane; FAIL/PARTIAL are the signal to inspect.';
        metricLabelEl.textContent = 'fail/partial rate in evaluated window';
        latestMixLabelEl.textContent = 'Current Signal';
        windowCopyEl.textContent = 'bucketed manual eval outcome history';
        if (evalSubtitleEl) {
          evalSubtitleEl.textContent = 'fail-first feedback rows · observed output · source path';
        }
        setLegend([
          { label: 'fail', color: 'var(--fail)' },
          { label: 'partial', color: 'var(--error)' },
          { label: 'pass', color: 'var(--pass)' },
        ]);
      } else {
        chartTitleEl.textContent = 'Recent active-lane mix';
        chartSubtitleEl.textContent = 'Bucketed live runs stacked by lane across the recent window.';
        metricLabelEl.textContent = 'pass rate right now';
        latestMixLabelEl.textContent = 'Current Mix';
        windowCopyEl.textContent = 'bucketed active-lane mix history';
        if (evalSubtitleEl) {
          evalSubtitleEl.textContent = 'latest evaluated rows · observed output · source path';
        }
        setLegend([
          { label: 'text', color: 'var(--lane-text)' },
          { label: 'handwriting', color: 'var(--lane-handwriting)' },
          { label: 'illustration', color: 'var(--lane-illustration)' },
        ]);
      }

      passRateEl.textContent = isOutcomeMode
        ? formatPct(failPressure)
        : formatPct(latestSummary.passRate);
      deltaLabelEl.textContent = isBinaryGateMode
        ? `${windowSummary.fail} fail · ${windowSummary.pass} pass across gate cases`
        : isFeedbackMode
          ? `${windowSummary.fail} fail · ${windowSummary.partial} partial · ${windowSummary.pass} pass in this window`
        : (
            previousSummary
              ? formatPtsDelta(latestSummary.passRate, previousSummary.passRate)
              : 'Waiting for the next run to show drift.'
          );
      healthStateEl.textContent = health.label;
      healthStateEl.dataset.state = health.key;
      runIdEl.textContent = latestBucket.label || latestBucket.run_id || 'n/a';
      latestMixEl.textContent = isBinaryGateMode
        ? `${latestBucket.fail} fail · ${latestBucket.pass} pass`
        : isFeedbackMode
          ? `${latestBucket.fail} fail · ${latestBucket.partial} partial · ${latestBucket.pass} pass`
        : `${latestBucket.text} text · ${latestBucket.handwriting} handwriting · ${latestBucket.illustration} illustration`;
      windowLabelEl.textContent = rawPoints.length
        ? (
            isBinaryGateMode
              ? `Last ${rawPoints.length} live gate reports · ${bucketedPoints.length} buckets`
              : isFeedbackMode
                ? `Last ${rawPoints.length} evaluated outcomes · ${bucketedPoints.length} buckets`
              : `Last ${rawPoints.length} live runs · ${bucketedPoints.length} buckets`
          )
        : (isBinaryGateMode ? 'Waiting for live gate reports' : isFeedbackMode ? 'Waiting for manual feedback' : 'Waiting for active-lane runs');
      updatedEl.textContent = formatTimestamp(payload.updated_at || latestBucket.timestamp_ms);
    }

    function renderLaneSummaries(payload) {
      const lanes = Array.isArray(payload?.lane_summaries) ? payload.lane_summaries : [];
      if (!laneSummariesEl || !laneEmptyEl) return;
      if (!lanes.length) {
        laneSummariesEl.innerHTML = '';
        laneEmptyEl.style.display = 'block';
        return;
      }
      laneEmptyEl.style.display = 'none';
      laneSummariesEl.innerHTML = lanes.map(lane => {
        const pass = Number(lane?.pass || 0);
        const fail = Number(lane?.fail || 0);
        const partial = Number(lane?.partial || 0);
        const errors = Number(lane?.errors || 0);
        const retain = Number(lane?.retain || 0);
        const evict = Number(lane?.evict || 0);
        const primary = partial > 0 || errors > 0
          ? `${pass} pass · ${fail} fail · ${partial + errors} other`
          : `${pass} pass · ${fail} fail`;
        const detail = retain > 0 || evict > 0
          ? `${retain} retain · ${evict} evict`
          : `${Number(lane?.total || 0)} total`;
        const state = computeLaneSnapshotState(lane);
        const note = escapeHtml(shorten(lane?.note || '', 140));
        const source = escapeHtml(leafName(lane?.source || ''));
        const runId = String(lane?.run_id || '').trim();
        const sourceLine = runId
          ? `${source}${source && runId ? ' · ' : ''}${escapeHtml(runId)}`
          : source || '(tracked)';
        return `
          <article class="lane-card">
            <div class="lane-card-head">
              <div class="lane-card-title">${escapeHtml(lane?.title || 'Lane')}</div>
              <div class="lane-card-updated">${escapeHtml(formatLaneSnapshotUpdated(lane?.updated_at || ''))}</div>
            </div>
            <div class="lane-card-state" data-state="${escapeHtml(state.key)}">${escapeHtml(state.label)}</div>
            <div class="lane-card-note">${note || '(no note)'}</div>
            <div class="lane-card-metric">${escapeHtml(primary)}</div>
            <div class="lane-card-detail">${escapeHtml(detail)}</div>
            <div class="lane-card-source">${sourceLine}</div>
          </article>
        `;
      }).join('');
    }

    function renderChart(payload) {
      const root = document.getElementById('chart');
      root.innerHTML = '';
      const tip = document.getElementById('chartTip');
      const chartMode = payload?.chart_mode || 'ocr_lanes';
      const isBinaryGateMode = chartMode === 'binary_gates';
      const isFeedbackMode = chartMode === 'feedback';
      const allPoints = (payload.points || []).map(normalizePoint);
      const points = bucketPoints(allPoints, state.chartMaxPoints);

      if (!points.length) {
        root.innerHTML = '<div class="muted" style="padding:12px">No eval runs yet. Execute evals, then refresh.</div>';
        tip.style.display = 'none';
        return;
      }

      const w = root.clientWidth || 1200;
      const h = root.clientHeight || 420;
      const margin = { top: 14, right: 14, bottom: 18, left: 10 };
      const innerW = w - margin.left - margin.right;
      const innerH = h - margin.top - margin.bottom;

      const svg = d3.select(root).append('svg').attr('width', w).attr('height', h);
      const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);
      const defs = svg.append('defs');

      const x = d3.scaleBand()
        .domain(points.map(d => d.run_id))
        .range([0, innerW])
        .paddingInner(0.28)
        .paddingOuter(0.12);

      const y = d3.scaleLinear()
        .domain([0, 1])
        .range([innerH, 0]);

      const clipDefs = defs.selectAll('clipPath')
        .data(points, d => d.run_id)
        .join(
          enter => {
            const clip = enter.append('clipPath').attr('id', d => clipId(d.run_id));
            clip.append('rect');
            return clip;
          },
        );

      clipDefs.select('rect')
        .attr('x', d => x(d.run_id))
        .attr('y', 0)
        .attr('width', x.bandwidth())
        .attr('height', innerH)
        .attr('rx', Math.min(18, x.bandwidth() / 2));

      g.selectAll('rect.track')
        .data(points, d => d.run_id)
        .join('rect')
        .attr('class', 'track')
        .attr('x', d => x(d.run_id))
        .attr('y', 0)
        .attr('width', x.bandwidth())
        .attr('height', innerH)
        .attr('rx', Math.min(18, x.bandwidth() / 2))
        .attr('fill', 'var(--track)');

      const segments = [];
      for (const point of points) {
        const parts = isBinaryGateMode
          ? [
              { key: 'fail', value: point.fail / point.total },
              { key: 'pass', value: point.pass / point.total },
            ].filter(part => part.value > 0)
          : isFeedbackMode
            ? [
              { key: 'fail', value: point.fail / point.total },
              { key: 'partial', value: point.partial / point.total },
              { key: 'pass', value: point.pass / point.total },
            ].filter(part => part.value > 0)
          : [
              { key: 'text', value: point.text / point.total },
              { key: 'handwriting', value: point.handwriting / point.total },
              { key: 'illustration', value: point.illustration / point.total },
            ].filter(part => part.value > 0);
        let cursor = 0;
        for (const part of parts) {
          const start = cursor;
          cursor += part.value;
          segments.push({
            run_id: point.run_id,
            key: part.key,
            start,
            end: cursor,
          });
        }
      }

      const palette = {
        text: getComputedStyle(document.documentElement).getPropertyValue('--lane-text').trim(),
        handwriting: getComputedStyle(document.documentElement).getPropertyValue('--lane-handwriting').trim(),
        illustration: getComputedStyle(document.documentElement).getPropertyValue('--lane-illustration').trim(),
        fail: getComputedStyle(document.documentElement).getPropertyValue('--fail').trim(),
        partial: getComputedStyle(document.documentElement).getPropertyValue('--error').trim(),
        pass: getComputedStyle(document.documentElement).getPropertyValue('--pass').trim(),
      };

      g.selectAll('rect.segment')
        .data(segments, d => `${d.run_id}:${d.key}`)
        .join('rect')
        .attr('class', 'segment')
        .attr('clip-path', d => `url(#${clipId(d.run_id)})`)
        .attr('x', d => x(d.run_id))
        .attr('width', x.bandwidth())
        .attr('y', d => y(d.end))
        .attr('height', d => Math.max(0, y(d.start) - y(d.end)))
        .attr('fill', d => palette[d.key]);

      g.selectAll('rect.hit')
        .data(points, d => d.run_id)
        .join('rect')
        .attr('class', 'hit')
        .attr('x', d => x(d.run_id))
        .attr('y', 0)
        .attr('width', x.bandwidth())
        .attr('height', innerH)
        .attr('fill', 'transparent')
        .style('cursor', 'crosshair')
        .on('mouseenter', (event, d) => {
          tip.style.display = 'block';
          const signal = isBinaryGateMode
            ? `${d.fail} fail · ${d.pass} pass`
            : isFeedbackMode
              ? `${d.fail} fail · ${d.partial} partial · ${d.pass} pass`
            : `${d.text} text · ${d.handwriting} handwriting · ${d.illustration} illustration`;
          const noun = isBinaryGateMode ? 'reports' : isFeedbackMode ? 'outcomes' : 'runs';
          tip.innerHTML = `
            <div><strong>${d.label}</strong></div>
            <div class="tip-muted">${signal}</div>
            <div class="tip-muted">${d.runCount} ${noun} · ${formatTimestamp(d.timestamp_ms)}</div>
          `;
        })
        .on('mousemove', event => {
          const rect = root.getBoundingClientRect();
          tip.style.left = `${event.clientX - rect.left + 14}px`;
          tip.style.top = `${event.clientY - rect.top + 14}px`;
        })
        .on('mouseleave', () => {
          tip.style.display = 'none';
        });
    }

    function renderEvals(payload) {
      const evals = Array.isArray(payload?.evals) ? payload.evals : [];
      const rows = evals.slice(0, 60);
      if (!rows.length) {
        evalRowsEl.innerHTML = '';
        evalEmptyEl.style.display = 'block';
        return;
      }
      evalEmptyEl.style.display = 'none';
      evalRowsEl.innerHTML = rows.map(row => {
        const outcome = String(row?.outcome || 'UNKNOWN').toUpperCase();
        const outcomeClass = outcome === 'PASS'
          ? 'pass'
          : outcome === 'FAIL'
            ? 'fail'
            : 'error';
        const lane = escapeHtml(row?.lane || row?.source_name || 'other');
        const item = escapeHtml(shorten(row?.item || '(unknown)', 80));
        const expected = escapeHtml(shorten(row?.expected || '(none)', 200));
        const observed = escapeHtml(shorten(row?.observed || '(none)', 220));
        const pathValue = String(row?.image_path || '').trim();
        const pathLeaf = escapeHtml(leafName(pathValue));
        const fullPath = escapeHtml(pathValue || '(none)');
        const pathCell = pathValue
          ? `<a class="eval-path" href="file://${encodeURI(pathValue)}" title="${fullPath}">${pathLeaf}</a>`
          : `<span class="eval-path">(none)</span>`;
        return `
          <tr>
            <td><span class="eval-outcome ${outcomeClass}">${escapeHtml(outcome)}</span></td>
            <td><span class="eval-clip">${lane}</span></td>
            <td><span class="eval-clip" title="${escapeHtml(String(row?.item || ''))}">${item}</span></td>
            <td><span class="eval-clip" title="${escapeHtml(String(row?.expected || ''))}">${expected}</span></td>
            <td><span class="eval-clip" title="${escapeHtml(String(row?.observed || ''))}">${observed}</span></td>
            <td>${pathCell}</td>
          </tr>
        `;
      }).join('');
    }

    async function refresh() {
      if (inFlight) return;
      inFlight = true;
      if (refreshNowEl) refreshNowEl.disabled = true;
      setPollStatus('refreshing…', 'updating');
      try {
        const res = await fetch(dataUrl, { cache: 'no-store' });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const payload = await res.json();
        state.payload = payload;
        renderSummary(payload);
        renderLaneSummaries(payload);
        renderChart(payload);
        renderEvals(payload);
        setPollStatus('update mode: post-batch/manual');
      } catch (error) {
        console.error(error);
        setPollStatus('refresh failed (see console)', 'error');
      } finally {
        inFlight = false;
        if (refreshNowEl) refreshNowEl.disabled = false;
      }
    }

    if (refreshNowEl) {
      refreshNowEl.addEventListener('click', () => {
        refresh();
      });
    }
    refresh();
  </script>
</body>
</html>
"""
    return (
        html.replace("__REFRESH_MS__", str(int(refresh_ms)))
        .replace("__DEFAULT_MAX_CHART_POINTS__", str(int(chart_max_points)))
    )
