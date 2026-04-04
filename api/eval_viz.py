from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPORT_SUBDIRS = ("ocr_stability_runs", "ocr_growth_stability_runs")
_RUN_ID_TIMESTAMP_RE = re.compile(r"^(?P<epoch>\d{9,})-r\d+$")
_EVAL_VIZ_DB_PATH = Path(".local/runtime_dbs/active/eval_viz.db")
_HISTORY_DB_PATH = Path(".local/runtime_dbs/active/history.db")
_OCR_LANES = ("typed", "handwriting", "illustration")
_LANE_LABELS = {
    "typed": "text",
    "handwriting": "handwriting",
    "illustration": "illustration",
}
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


def _timestamp_ms(report: dict[str, Any], path: Path) -> int:
    run_id = str(report.get("run_id", "")).strip()
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


def _build_payload_from_history_db(db_path: Path, *, max_runs: int = 120) -> dict[str, Any] | None:
    if not db_path.is_file():
        return None

    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    except sqlite3.Error:
        return None

    conn.row_factory = sqlite3.Row

    try:
        rows = conn.execute(
            """
            SELECT run_id, source_name, status, extracted_text, created_at
            FROM (
                SELECT id, run_id, source_name, status, extracted_text, created_at
                FROM ocr_runs
                ORDER BY created_at DESC
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

    points: list[dict[str, Any]] = []
    for row in rows:
        source_name = str(row["source_name"] or "").strip()
        extracted_text = str(row["extracted_text"] or "")
        lane = _classify_ocr_history_lane(source_name=source_name, extracted_text=extracted_text)
        status = str(row["status"] or "").strip().lower()
        point = _default_point(timestamp_ms=int(row["created_at"] or 0))
        point.update(
            {
                "run_id": str(row["run_id"] or "").strip() or "n/a",
                "label": str(row["run_id"] or "").strip() or "n/a",
                "pass": 1 if status == "ok" else 0,
                "fail": 0 if status == "ok" else 1,
                "errors": 0,
                "total": 1,
                "text": 1 if lane == "typed" else 0,
                "handwriting": 1 if lane == "handwriting" else 0,
                "illustration": 1 if lane == "illustration" else 0,
                "source": source_name or db_path.name,
            }
        )
        points.append(point)

    latest_point = points[-1]
    conn.close()

    return {
        "updated_at": datetime.fromtimestamp(
            int(latest_point["timestamp_ms"]) / 1000,
            tz=timezone.utc,
        ).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "summary": {
            "pass": int(latest_point["pass"]),
            "fail": int(latest_point["fail"]),
            "errors": int(latest_point["errors"]),
            "total": int(latest_point["total"]),
            "run_id": str(latest_point["run_id"]),
            "source": str(latest_point["source"]),
            "timestamp_ms": int(latest_point["timestamp_ms"]),
            "text": int(latest_point["text"]),
            "handwriting": int(latest_point["handwriting"]),
            "illustration": int(latest_point["illustration"]),
        },
        "summary_points": points[-2:],
        "points": points,
        "runs_total": len(points),
        "evals": [],
    }


def _build_payload_from_eval_db(db_path: Path, *, max_evals: int) -> dict[str, Any] | None:
    if not db_path.is_file():
        return None

    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    except sqlite3.Error:
        return None

    conn.row_factory = sqlite3.Row

    try:
        point_rows = conn.execute(
            """
            SELECT
                run_id,
                MAX(ts_unix) AS ts_unix,
                SUM(CASE WHEN lower(outcome) = 'pass' THEN 1 ELSE 0 END) AS pass,
                SUM(CASE WHEN lower(outcome) = 'fail' THEN 1 ELSE 0 END) AS fail,
                SUM(CASE WHEN lower(outcome) = 'error' THEN 1 ELSE 0 END) AS errors,
                COUNT(*) AS total,
                SUM(CASE WHEN lane = 'typed' THEN 1 ELSE 0 END) AS typed,
                SUM(CASE WHEN lane = 'handwriting' THEN 1 ELSE 0 END) AS handwriting,
                SUM(CASE WHEN lane = 'illustration' THEN 1 ELSE 0 END) AS illustration
            FROM eval_points
            WHERE lane IN (?, ?, ?)
            GROUP BY run_id
            ORDER BY MAX(ts_unix) ASC, run_id ASC
            """,
            _OCR_LANES,
        ).fetchall()
    except sqlite3.Error:
        conn.close()
        return None

    if not point_rows:
        conn.close()
        return None

    points: list[dict[str, Any]] = []
    for row in point_rows:
        timestamp_ms = int(row["ts_unix"] or 0) * 1000
        run_id = str(row["run_id"] or "").strip() or "n/a"
        points.append(
            {
                "run_id": run_id,
                "timestamp_ms": timestamp_ms,
                "label": run_id,
                "pass": int(row["pass"] or 0),
                "fail": int(row["fail"] or 0),
                "errors": int(row["errors"] or 0),
                "total": int(row["total"] or 0),
                "text": int(row["typed"] or 0),
                "handwriting": int(row["handwriting"] or 0),
                "illustration": int(row["illustration"] or 0),
                "source": db_path.name,
            }
        )

    latest_point = points[-1] if points else _default_point()
    try:
        rebuilt_row = conn.execute(
            "SELECT value FROM metadata WHERE key = 'rebuilt_at_unix'"
        ).fetchone()
    except sqlite3.Error:
        rebuilt_row = None
    try:
        rebuilt_at_unix = int(str(rebuilt_row["value"]).strip() or 0) if rebuilt_row else 0
    except (TypeError, ValueError):
        rebuilt_at_unix = 0
    updated_at_unix = rebuilt_at_unix or (int(latest_point["timestamp_ms"]) // 1000) or int(
        datetime.now(tz=timezone.utc).timestamp()
    )
    updated_at = datetime.fromtimestamp(
        updated_at_unix,
        tz=timezone.utc,
    ).strftime("%Y-%m-%dT%H:%M:%SZ")

    eval_rows: list[dict[str, Any]] = []
    try:
        latest_rows = conn.execute(
            """
            SELECT case_id, lane, outcome, expected_text, observed_text, source_path, case_index
            FROM eval_points
            WHERE run_id = ? AND lane IN (?, ?, ?)
            ORDER BY case_index ASC, case_id ASC
            LIMIT ?
            """,
            (str(latest_point["run_id"]), *_OCR_LANES, max_evals),
        ).fetchall()
    except sqlite3.Error:
        latest_rows = []

    for index, row in enumerate(latest_rows):
        case_id = str(row["case_id"] or "").strip() or "(unknown)"
        source_path = str(row["source_path"] or "").strip()
        lane = _LANE_LABELS.get(str(row["lane"] or "").strip(), "other")
        row_key = f"{case_id}::{source_path or index}"
        eval_rows.append(
            {
                "row_key": row_key,
                "item": case_id,
                "outcome": str(row["outcome"] or "UNKNOWN").strip().upper() or "UNKNOWN",
                "expected": _normalize_text(row["expected_text"] or "(none)", max_chars=360),
                "observed": _normalize_text(row["observed_text"] or "", max_chars=520),
                "source_name": lane,
                "image_path": source_path,
                "lane": lane,
            }
        )

    conn.close()

    return {
        "updated_at": updated_at,
        "summary": {
            "pass": int(latest_point["pass"]),
            "fail": int(latest_point["fail"]),
            "errors": int(latest_point["errors"]),
            "total": int(latest_point["total"]),
            "run_id": str(latest_point["run_id"]),
            "source": str(latest_point["source"]),
            "timestamp_ms": int(latest_point["timestamp_ms"]),
            "text": int(latest_point["text"]),
            "handwriting": int(latest_point["handwriting"]),
            "illustration": int(latest_point["illustration"]),
        },
        "summary_points": points[-2:],
        "points": points,
        "runs_total": len(points),
        "evals": eval_rows,
    }


def build_pass_fail_viz_payload(
    report_root: Path | None = None,
    *,
    max_evals: int = 140,
    db_path: Path | None = None,
    history_db_path: Path | None = None,
    max_history_runs: int = 120,
) -> dict[str, Any]:
    effective_db_path = db_path if db_path is not None else (_EVAL_VIZ_DB_PATH if report_root is None else None)
    effective_history_db_path = (
        history_db_path
        if history_db_path is not None
        else (_HISTORY_DB_PATH if report_root is None and db_path is None else None)
    )
    if report_root is None:
        history_payload = (
            _build_payload_from_history_db(effective_history_db_path, max_runs=max(1, max_history_runs))
            if effective_history_db_path is not None
            else None
        )
        eval_payload = (
            _build_payload_from_eval_db(effective_db_path, max_evals=max_evals)
            if effective_db_path is not None
            else None
        )
        if history_payload is not None:
            if eval_payload is not None:
                return {
                    "updated_at": history_payload["updated_at"],
                    "summary": eval_payload["summary"],
                    "summary_points": eval_payload.get("summary_points", []),
                    "points": history_payload["points"],
                    "runs_total": history_payload["runs_total"],
                    "evals": eval_payload["evals"],
                }
            return history_payload
        if eval_payload is not None:
            return eval_payload

    root = report_root or Path(".local/eval_reports")
    run_records: list[tuple[int, dict[str, Any], dict[str, Any], Path]] = []

    for path in _report_paths(root):
        report = _load_json(path)
        if report is None:
            continue
        summary = report.get("summary")
        if not isinstance(summary, dict):
            continue

        passed = int(summary.get("passed", 0) or 0)
        failed = int(summary.get("failed", 0) or 0)
        errors = int(summary.get("errors", 0) or 0)
        attempted = int(summary.get("attempted", summary.get("total_selected", 0)) or 0)
        timestamp_ms = _timestamp_ms(report, path)
        run_id = str(report.get("run_id", path.stem)).strip() or path.stem

        point = {
            "run_id": run_id,
            "timestamp_ms": timestamp_ms,
            "label": run_id,
            "pass": passed,
            "fail": failed,
            "errors": errors,
            "total": attempted,
            "source": path.parent.name,
        }
        run_records.append((timestamp_ms, point, report, path))

    run_records.sort(key=lambda item: item[0])

    points = [item[1] for item in run_records]
    latest_point = points[-1] if points else _default_point()

    latest_report = run_records[-1][2] if run_records else {}
    latest_cases = latest_report.get("cases") if isinstance(latest_report, dict) else None
    eval_rows: list[dict[str, Any]] = []
    if isinstance(latest_cases, list):
        for index, case in enumerate(latest_cases[:max_evals]):
            if not isinstance(case, dict):
                continue
            item = str(case.get("id", "")).strip() or "(unknown)"
            source_name = str(case.get("source_name", "")).strip()
            image_path = str(case.get("image_path", "")).strip()
            row_key = f"{item}::{source_name or image_path or index}"
            eval_rows.append(
                {
                    "row_key": row_key,
                    "item": item,
                    "outcome": str(case.get("status", "")).strip().upper() or "UNKNOWN",
                    "expected": _expected_for_case(case),
                    "observed": _normalize_text(case.get("extracted_text", ""), max_chars=520),
                    "source_name": source_name,
                    "image_path": image_path,
                }
            )

    return {
        "updated_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "summary": {
            "pass": int(latest_point["pass"]),
            "fail": int(latest_point["fail"]),
            "errors": int(latest_point["errors"]),
            "total": int(latest_point["total"]),
            "run_id": str(latest_point["run_id"]),
            "source": str(latest_point["source"]),
            "timestamp_ms": int(latest_point["timestamp_ms"]),
        },
        "points": points,
        "runs_total": len(points),
        "evals": eval_rows,
    }


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
          A live instrument panel for OCR lane drift.
          Deep detail stays in the database; this page is just the heartbeat.
        </p>
      </div>

      <div class="hero-stat">
        <div class="status-pill" id="healthState" data-state="warming">warming up</div>
        <div>
          <div class="metric-value" id="passRate">0%</div>
          <div class="metric-label">pass rate right now</div>
          <div class="delta-label" id="deltaLabel">Waiting for the first live window.</div>
        </div>
      </div>
    </section>

    <section class="panel">
      <div class="panel-top">
        <div>
          <h2 class="panel-title">Recent OCR mix</h2>
          <p class="panel-subtitle">Bucketed OCR runs stacked by lane across the recent window.</p>
          <div class="legend" aria-label="chart legend">
            <span class="legend-item"><span class="legend-swatch" style="background: var(--lane-text)"></span>text</span>
            <span class="legend-item"><span class="legend-swatch" style="background: var(--lane-handwriting)"></span>handwriting</span>
            <span class="legend-item"><span class="legend-swatch" style="background: var(--lane-illustration)"></span>illustration</span>
          </div>
        </div>

        <div class="meta-grid">
          <div class="meta-card">
            <span class="meta-label">Latest Bucket</span>
            <span class="meta-value" id="runId">n/a</span>
          </div>
          <div class="meta-card">
            <span class="meta-label">Current Mix</span>
            <span class="meta-value" id="latestMix">0 text · 0 handwriting · 0 illustration</span>
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
        <span class="window-copy">bucketed OCR lane history</span>
        <span>now</span>
      </div>
    </section>
  </main>

  <script>
    const REFRESH_MS = __REFRESH_MS__;
    const DEFAULT_MAX_CHART_POINTS = __DEFAULT_MAX_CHART_POINTS__;
    const dataUrl = '/viz/pass-fail/data';
    const state = { payload: null, chartMaxPoints: DEFAULT_MAX_CHART_POINTS };

    const passRateEl = document.getElementById('passRate');
    const deltaLabelEl = document.getElementById('deltaLabel');
    const healthStateEl = document.getElementById('healthState');
    const runIdEl = document.getElementById('runId');
    const latestMixEl = document.getElementById('latestMix');
    const windowLabelEl = document.getElementById('windowLabel');
    const updatedEl = document.getElementById('updatedAt');

    function normalizePoint(point, fallbackIndex = 0) {
      const pass = Number(point?.pass || 0);
      const fail = Number(point?.fail || 0);
      const errors = Number(point?.errors || 0);
      const text = Number(point?.text ?? point?.typed ?? 0);
      const handwriting = Number(point?.handwriting || 0);
      const illustration = Number(point?.illustration || 0);
      const explicitTotal = Number(point?.total || 0);
      const measuredTotal = pass + fail + errors;
      const laneTotal = text + handwriting + illustration;
      const total = Math.max(explicitTotal, measuredTotal, laneTotal, 1);
      const passRate = total > 0 ? pass / total : 0;
      return {
        run_id: point?.run_id || `run-${fallbackIndex + 1}`,
        label: point?.label || point?.run_id || `run-${fallbackIndex + 1}`,
        pass,
        fail,
        errors,
        total,
        text,
        handwriting,
        illustration,
        timestamp_ms: Number(point?.timestamp_ms || 0),
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

    function renderSummary(payload) {
      const rawPoints = (payload.points || []).map(normalizePoint);
      const bucketedPoints = bucketPoints(rawPoints, state.chartMaxPoints);
      const latestBucket = bucketedPoints.at(-1) || normalizePoint(payload.summary || {});
      const summaryPoints = Array.isArray(payload.summary_points)
        ? payload.summary_points.map(normalizePoint)
        : [];
      const latestSummary = summaryPoints.at(-1) || normalizePoint(payload.summary || latestBucket);
      const previousSummary = summaryPoints.length > 1 ? summaryPoints.at(-2) : null;
      const health = computeHealthState(latestSummary.passRate, latestSummary.total);

      passRateEl.textContent = formatPct(latestSummary.passRate);
      deltaLabelEl.textContent = previousSummary
        ? formatPtsDelta(latestSummary.passRate, previousSummary.passRate)
        : 'Waiting for the next run to show drift.';
      healthStateEl.textContent = health.label;
      healthStateEl.dataset.state = health.key;
      runIdEl.textContent = latestBucket.label || latestBucket.run_id || 'n/a';
      latestMixEl.textContent = `${latestBucket.text} text · ${latestBucket.handwriting} handwriting · ${latestBucket.illustration} illustration`;
      windowLabelEl.textContent = rawPoints.length
        ? `Last ${rawPoints.length} OCR runs · ${bucketedPoints.length} buckets`
        : 'Waiting for OCR runs';
      updatedEl.textContent = formatTimestamp(payload.updated_at || latestBucket.timestamp_ms);
    }

    function renderChart(payload) {
      const root = document.getElementById('chart');
      root.innerHTML = '';
      const tip = document.getElementById('chartTip');
      const allPoints = (payload.points || []).map(normalizePoint);
      const points = bucketPoints(allPoints, state.chartMaxPoints);

      if (!points.length) {
        root.innerHTML = '<div class="muted" style="padding:12px">No runs yet. Execute OCR evals, then refresh.</div>';
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
        const parts = [
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
          tip.innerHTML = `
            <div><strong>${d.label}</strong></div>
            <div class="tip-muted">${d.text} text · ${d.handwriting} handwriting · ${d.illustration} illustration</div>
            <div class="tip-muted">${d.runCount} runs · ${formatTimestamp(d.timestamp_ms)}</div>
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

    async function refresh() {
      try {
        const res = await fetch(dataUrl, { cache: 'no-store' });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const payload = await res.json();
        state.payload = payload;
        renderSummary(payload);
        renderChart(payload);
      } catch (error) {
        console.error(error);
      }
    }

    refresh();
    setInterval(refresh, REFRESH_MS);
  </script>
</body>
</html>
"""
    return (
        html.replace("__REFRESH_MS__", str(int(refresh_ms)))
        .replace("__DEFAULT_MAX_CHART_POINTS__", str(int(chart_max_points)))
    )
