from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import time
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any

SUITE_PREFIXES = (
    "ocr-handwriting",
    "ocr-recovery",
    "file-search",
    "hallucination",
    "retrieval",
    "style",
    "clip-ab",
    "ocr",
    "parallel",
)

SUITE_LABELS = {
    "retrieval": "Retrieval",
    "file-search": "File Search",
    "ocr": "OCR",
    "ocr-handwriting": "OCR Handwriting",
    "ocr-recovery": "OCR Recovery",
    "style": "Style",
    "hallucination": "Hallucination",
    "clip-ab": "CLIP AB",
    "parallel": "Parallel",
    "unknown": "Unknown",
}


def _utc_iso(unix_seconds: float | int | None = None) -> str:
    if unix_seconds is None:
        stamp = datetime.now(timezone.utc)
    else:
        stamp = datetime.fromtimestamp(float(unix_seconds), tz=timezone.utc)
    return stamp.strftime("%Y-%m-%dT%H:%M:%SZ")


def _compact(text: str, *, limit: int = 160) -> str:
    one_line = " ".join(str(text).split()).strip()
    if len(one_line) <= limit:
        return one_line
    return one_line[: limit - 1].rstrip() + "…"


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _to_str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value:
        text = str(item).strip()
        if text:
            out.append(text)
    return out


def _suite_label(suite_key: str) -> str:
    return SUITE_LABELS.get(suite_key, SUITE_LABELS["unknown"])


def _detect_suite(path: Path) -> str:
    stem = path.stem.lower()
    for prefix in SUITE_PREFIXES:
        if stem == prefix or stem.startswith(f"{prefix}-"):
            return prefix
    return "unknown"


def _extract_run_id(path: Path, suite_key: str, payload: dict[str, Any]) -> str:
    run_id = str(payload.get("run_id", "")).strip()
    if run_id:
        return run_id
    stem = path.stem
    if stem == suite_key:
        return "latest"
    if stem.startswith(f"{suite_key}-"):
        return stem[len(suite_key) + 1 :]
    return stem


def _status_from_case(case: dict[str, Any]) -> str:
    error_text = str(case.get("error", "")).strip()
    if error_text:
        return "ERROR"

    raw_status = str(case.get("status", "")).strip().upper()
    if raw_status in {"PASS", "FAIL", "ERROR"}:
        return raw_status

    if isinstance(case.get("pass"), bool):
        return "PASS" if bool(case.get("pass")) else "FAIL"
    if isinstance(case.get("judge_pass"), bool):
        return "PASS" if bool(case.get("judge_pass")) else "FAIL"
    if isinstance(case.get("any_hit"), bool):
        return "PASS" if bool(case.get("any_hit")) else "FAIL"
    return "UNKNOWN"


def _build_tested_value(suite_key: str, case: dict[str, Any]) -> str:
    query = str(case.get("query", "")).strip()
    if suite_key in {"retrieval", "file-search"}:
        must_include = _to_str_list(case.get("must_include"))
        if query and must_include:
            return _compact(f"{query} | must include: {', '.join(must_include)}")
        if query:
            return _compact(query)
        if must_include:
            return _compact("must include: " + ", ".join(must_include))

    if suite_key in {"ocr", "ocr-handwriting"}:
        source_name = str(case.get("source_name", "")).strip()
        image_path = str(case.get("image_path", "")).strip()
        mode = str(case.get("transcription_mode", "")).strip()
        parts = [part for part in (source_name, image_path, mode) if part]
        if parts:
            return _compact(" | ".join(parts))

    if suite_key == "ocr-recovery":
        steps = case.get("steps")
        if isinstance(steps, list) and steps:
            first_step = steps[0] if isinstance(steps[0], dict) else {}
            prompt = str(first_step.get("prompt", "")).strip()
            if prompt:
                return _compact(prompt)
        guidance = str(case.get("labeling_guidance", "")).strip()
        if guidance:
            return _compact(guidance)

    if suite_key == "style" and query:
        return _compact(query)

    if suite_key == "hallucination":
        answer = str(case.get("answer", "")).strip()
        if answer:
            return _compact(answer)

    if suite_key == "clip-ab":
        case_id = str(case.get("case_id", "")).strip()
        arm = str(case.get("arm", "")).strip()
        parts = [part for part in (case_id, arm) if part]
        if parts:
            return _compact(" | ".join(parts))

    fallback_id = str(case.get("id", "")).strip() or str(case.get("case_id", "")).strip()
    return fallback_id or "n/a"


def _build_outcome_summary(case: dict[str, Any]) -> str:
    parts: list[str] = []
    detail = str(case.get("detail", "")).strip()
    notes = str(case.get("notes", "")).strip()
    if detail:
        parts.append(detail)
    if notes:
        parts.append(notes)

    fail_reasons = _to_str_list(case.get("fail_reasons"))
    reasons = _to_str_list(case.get("reasons"))
    gate_reasons = _to_str_list(case.get("gate_reasons"))
    forbidden_hits = _to_str_list(case.get("forbidden_hits"))
    if fail_reasons:
        parts.append("fail: " + "; ".join(fail_reasons[:2]))
    if reasons:
        parts.append("reasons: " + "; ".join(reasons[:2]))
    if gate_reasons:
        parts.append("gate: " + "; ".join(gate_reasons[:2]))
    if forbidden_hits:
        parts.append("forbidden: " + ", ".join(forbidden_hits[:4]))

    score = case.get("score")
    risk = str(case.get("risk", "")).strip()
    fit = str(case.get("fit", "")).strip()
    if score is not None:
        parts.append(f"score={score}")
    if risk:
        parts.append(f"risk={risk}")
    if fit:
        parts.append(f"fit={fit}")

    extracted_text = str(case.get("extracted_text", "")).strip()
    if extracted_text:
        parts.append("text: " + _compact(extracted_text, limit=120))

    error_text = str(case.get("error", "")).strip()
    if error_text:
        parts.append("error: " + error_text)

    if not parts:
        return "No summary details."
    return _compact(" | ".join(parts), limit=260)


def _collect_references(case: dict[str, Any]) -> list[str]:
    refs: list[str] = []
    seen: set[str] = set()
    for key in (
        "session_id",
        "seed_session",
        "target_session",
        "distractor_session",
        "top_session_id",
    ):
        value = str(case.get(key, "")).strip()
        if value:
            label = f"session:{value}"
            if label not in seen:
                refs.append(label)
                seen.add(label)

    image_path = str(case.get("image_path", "")).strip()
    if image_path and image_path not in seen:
        refs.append(image_path)
        seen.add(image_path)

    source_name = str(case.get("source_name", "")).strip()
    if source_name:
        label = f"source:{source_name}"
        if label not in seen:
            refs.append(label)
            seen.add(label)

    return refs


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def _summary_from_payload(suite_key: str, payload: dict[str, Any]) -> dict[str, Any]:
    raw_summary = payload.get("summary")
    summary = raw_summary if isinstance(raw_summary, dict) else {}
    total = _to_int(summary.get("total"), _to_int(payload.get("total_cases"), 0))
    passed = _to_int(summary.get("passed"), _to_int(payload.get("passed"), 0))
    failed = _to_int(summary.get("failed"), _to_int(payload.get("failed"), 0))
    errors = _to_int(summary.get("errors"), 0)
    gate_failed = _to_int(summary.get("gate_failed"), 0)
    if suite_key == "hallucination" and errors == 0:
        # Hallucination reports currently expose pass/fail + risk without explicit errors.
        errors = max(0, total - passed - failed)
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "gate_failed": gate_failed,
    }


def _latest_reports(report_dir: Path) -> dict[str, Path]:
    latest: dict[str, Path] = {}
    if not report_dir.exists():
        return latest
    for path in sorted(report_dir.glob("*.json")):
        if not path.is_file():
            continue
        suite_key = _detect_suite(path)
        current = latest.get(suite_key)
        if current is None or path.stat().st_mtime > current.stat().st_mtime:
            latest[suite_key] = path
    return latest


def _runtime_overview(db_path: Path) -> dict[str, Any]:
    if not db_path.exists():
        return {
            "available": False,
            "db_path": str(db_path),
            "error": "History DB not found.",
            "counts": {},
        }
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
    except Exception as exc:  # pragma: no cover - operational guard
        return {
            "available": False,
            "db_path": str(db_path),
            "error": str(exc),
            "counts": {},
        }

    try:
        table_rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        tables = {str(row["name"]) for row in table_rows}

        def count(sql: str, params: tuple[Any, ...] = ()) -> int:
            row = conn.execute(sql, params).fetchone()
            if row is None:
                return 0
            return _to_int(row[0], 0)

        counts: dict[str, int] = {}
        if "chats" in tables:
            counts["chats_total"] = count("SELECT COUNT(*) FROM chats;")
            counts["chats_active"] = count("SELECT COUNT(*) FROM chats WHERE status='active';")
            counts["chats_deprecated"] = count("SELECT COUNT(*) FROM chats WHERE status='deprecated';")
        if "chat_messages" in tables:
            counts["messages_total"] = count("SELECT COUNT(*) FROM chat_messages;")
            counts["messages_visible"] = count(
                "SELECT COUNT(*) FROM chat_messages WHERE role IN ('user','assistant');"
            )
        if "message_feedback" in tables:
            counts["reviews_total"] = count("SELECT COUNT(*) FROM message_feedback;")
            counts["reviews_pass"] = count(
                "SELECT COUNT(*) FROM message_feedback WHERE lower(outcome)='pass';"
            )
            counts["reviews_fail"] = count(
                "SELECT COUNT(*) FROM message_feedback WHERE lower(outcome)='fail';"
            )
        if "eval_checkpoints" in tables:
            counts["checkpoints_total"] = count("SELECT COUNT(*) FROM eval_checkpoints;")
        if "ocr_runs" in tables:
            counts["ocr_runs_total"] = count("SELECT COUNT(*) FROM ocr_runs;")

        return {
            "available": True,
            "db_path": str(db_path),
            "error": "",
            "counts": counts,
        }
    finally:
        conn.close()


def build_dashboard_dataset(
    *,
    report_dir: Path,
    db_path: Path,
    max_cases_per_suite: int,
) -> dict[str, Any]:
    latest = _latest_reports(report_dir)
    suites: list[dict[str, Any]] = []
    cases: list[dict[str, Any]] = []

    for suite_key in sorted(latest.keys(), key=lambda value: _suite_label(value).lower()):
        report_path = latest[suite_key]
        payload = _load_json(report_path)
        if payload is None:
            suites.append(
                {
                    "suite": suite_key,
                    "label": _suite_label(suite_key),
                    "report_path": str(report_path),
                    "run_id": "unknown",
                    "status": "ERROR",
                    "summary": {"total": 0, "passed": 0, "failed": 0, "errors": 1, "gate_failed": 0},
                    "generated_at": _utc_iso(report_path.stat().st_mtime),
                    "load_error": "Could not parse JSON report.",
                }
            )
            continue

        summary = _summary_from_payload(suite_key, payload)
        run_id = _extract_run_id(report_path, suite_key, payload)
        generated_at = _utc_iso(payload.get("generated_at") or payload.get("timestamp_unix") or report_path.stat().st_mtime)
        suite_status = "PASS" if summary["failed"] == 0 and summary["errors"] == 0 else "FAIL"
        if summary["total"] == 0 and summary["passed"] == 0 and summary["failed"] == 0:
            suite_status = "UNKNOWN"

        suites.append(
            {
                "suite": suite_key,
                "label": _suite_label(suite_key),
                "report_path": str(report_path),
                "run_id": run_id,
                "status": suite_status,
                "summary": summary,
                "generated_at": generated_at,
                "load_error": "",
            }
        )

        raw_cases = payload.get("cases")
        report_cases = raw_cases if isinstance(raw_cases, list) else []
        for index, raw_case in enumerate(report_cases[:max_cases_per_suite], start=1):
            if not isinstance(raw_case, dict):
                continue
            case_id = (
                str(raw_case.get("id", "")).strip()
                or str(raw_case.get("case_id", "")).strip()
                or f"{suite_key}-{index:03d}"
            )
            status = _status_from_case(raw_case)
            tested_value = _build_tested_value(suite_key, raw_case)
            outcome_summary = _build_outcome_summary(raw_case)
            references = _collect_references(raw_case)
            image_path = str(raw_case.get("image_path", "")).strip()
            source_name = str(raw_case.get("source_name", "")).strip()
            cases.append(
                {
                    "suite": suite_key,
                    "suite_label": _suite_label(suite_key),
                    "case_id": case_id,
                    "status": status,
                    "tested_value": tested_value,
                    "outcome_summary": outcome_summary,
                    "references": references,
                    "image_path": image_path,
                    "source_name": source_name,
                    "run_id": run_id,
                    "report_path": str(report_path),
                    "report_generated_at": generated_at,
                }
            )

    case_status_counts = {
        "PASS": sum(1 for item in cases if item["status"] == "PASS"),
        "FAIL": sum(1 for item in cases if item["status"] == "FAIL"),
        "ERROR": sum(1 for item in cases if item["status"] == "ERROR"),
        "UNKNOWN": sum(1 for item in cases if item["status"] == "UNKNOWN"),
    }
    runtime = _runtime_overview(db_path)

    return {
        "generated_at": _utc_iso(),
        "report_dir": str(report_dir),
        "runtime": runtime,
        "suites": suites,
        "cases": cases,
        "overview": {
            "suite_count": len(suites),
            "case_count": len(cases),
            "status_counts": case_status_counts,
        },
    }


def _render_dashboard_html(dataset: dict[str, Any]) -> str:
    payload = json.dumps(dataset, ensure_ascii=False)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Polinko Eval Dashboard</title>
  <style>
    :root {{
      --bg-a: #081222;
      --bg-b: #0f1b34;
      --panel: #101a2e;
      --panel-alt: #0c1527;
      --line: #2a3a5f;
      --text: #e8eefc;
      --muted: #9badcf;
      --pass: #27c18a;
      --fail: #ff6b7a;
      --warn: #f4c86a;
      --accent: #4da3ff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--text);
      font-family: "OpenAI Sans", "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
      background: radial-gradient(1200px 700px at 15% 5%, #152b55 0%, transparent 60%),
                  linear-gradient(180deg, var(--bg-a), var(--bg-b));
      min-height: 100vh;
    }}
    .wrap {{
      max-width: 1400px;
      margin: 0 auto;
      padding: 24px;
      display: grid;
      gap: 16px;
    }}
    .panel {{
      background: linear-gradient(180deg, rgba(23, 35, 60, 0.9), rgba(13, 23, 42, 0.9));
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 16px;
      box-shadow: 0 16px 42px rgba(0, 0, 0, 0.28);
    }}
    h1, h2 {{
      margin: 0;
      font-weight: 700;
      letter-spacing: 0.2px;
    }}
    .subtitle {{
      margin-top: 8px;
      color: var(--muted);
      font-size: 0.95rem;
    }}
    .row {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
    }}
    .chip {{
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 6px 10px;
      background: rgba(18, 32, 58, 0.75);
      font-size: 0.9rem;
      color: var(--muted);
    }}
    .chip strong {{
      color: var(--text);
    }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
      gap: 10px;
    }}
    .card {{
      background: var(--panel-alt);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 12px;
    }}
    .card .k {{
      color: var(--muted);
      font-size: 0.86rem;
      margin-bottom: 6px;
    }}
    .card .v {{
      font-size: 1.2rem;
      font-weight: 700;
    }}
    .stack {{
      display: grid;
      gap: 12px;
    }}
    .filters {{
      display: grid;
      grid-template-columns: 1.3fr 1fr 1fr;
      gap: 10px;
    }}
    @media (max-width: 1000px) {{
      .filters {{
        grid-template-columns: 1fr;
      }}
    }}
    input[type="text"] {{
      width: 100%;
      padding: 10px 12px;
      border-radius: 10px;
      border: 1px solid var(--line);
      background: #0c1629;
      color: var(--text);
      font-size: 0.95rem;
    }}
    label {{
      color: var(--muted);
      font-size: 0.86rem;
      display: block;
      margin-bottom: 6px;
    }}
    .check-grid {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px 10px;
      padding: 10px;
      border: 1px solid var(--line);
      border-radius: 10px;
      background: #0c1629;
      min-height: 48px;
      align-content: flex-start;
    }}
    .check-grid span {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 0.88rem;
      color: var(--text);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
    }}
    th, td {{
      border-bottom: 1px solid rgba(54, 74, 115, 0.42);
      padding: 9px 8px;
      text-align: left;
      vertical-align: top;
      font-size: 0.9rem;
    }}
    th {{
      color: var(--muted);
      font-size: 0.82rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }}
    td code {{
      background: rgba(16, 31, 58, 0.82);
      border: 1px solid rgba(60, 89, 142, 0.35);
      border-radius: 6px;
      padding: 2px 5px;
      color: #d8e6ff;
      font-size: 0.82rem;
      display: inline-block;
      margin: 1px 0;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 560px;
    }}
    .status {{
      display: inline-block;
      min-width: 64px;
      text-align: center;
      border-radius: 999px;
      padding: 3px 8px;
      border: 1px solid transparent;
      font-size: 0.78rem;
      font-weight: 700;
    }}
    .status-pass {{
      color: #d8fff0;
      background: rgba(39, 193, 138, 0.2);
      border-color: rgba(39, 193, 138, 0.45);
    }}
    .status-fail {{
      color: #ffe4e8;
      background: rgba(255, 107, 122, 0.2);
      border-color: rgba(255, 107, 122, 0.45);
    }}
    .status-error, .status-unknown {{
      color: #fff4d8;
      background: rgba(244, 200, 106, 0.2);
      border-color: rgba(244, 200, 106, 0.45);
    }}
    .small {{
      color: var(--muted);
      font-size: 0.82rem;
    }}
    .mono {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
    }}
    .suite-block {{
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 10px;
      background: #0c1629;
    }}
    .cli-summary {{
      margin: 0;
      padding: 12px;
      border-radius: 10px;
      border: 1px solid var(--line);
      background: #081122;
      color: #d7e6ff;
      white-space: pre-wrap;
      line-height: 1.45;
      font-size: 0.9rem;
    }}
    a.path-link {{
      color: #9cd1ff;
      text-decoration: underline;
      text-underline-offset: 2px;
      word-break: break-all;
    }}
    a.path-link:hover {{
      color: #c6e5ff;
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="panel">
      <h1>Eval Dashboard</h1>
      <p class="subtitle">Binary eval lens with tested values, outcome summaries, and session/image references.</p>
      <div class="row" style="margin-top: 12px;">
        <span class="chip"><strong>generated</strong>: <span id="generatedAt"></span></span>
        <span class="chip"><strong>report dir</strong>: <span class="mono" id="reportDir"></span></span>
        <span class="chip"><strong>history db</strong>: <span class="mono" id="dbPath"></span></span>
      </div>
    </section>

    <section class="panel stack">
      <h2>Overview</h2>
      <div class="cards" id="overviewCards"></div>
    </section>

    <section class="panel stack">
      <h2>CLI Snapshot</h2>
      <pre id="cliSummary" class="cli-summary"></pre>
    </section>

    <section class="panel stack">
      <h2>Suite Runs</h2>
      <div id="suiteRows" class="cards"></div>
    </section>

    <section class="panel stack">
      <h2>Case Explorer</h2>
      <div class="filters">
        <div>
          <label for="searchInput">Search tested value / summary / refs</label>
          <input id="searchInput" type="text" placeholder="type to filter cases..." />
        </div>
        <div>
          <label>Suites</label>
          <div class="check-grid" id="suiteFilter"></div>
        </div>
        <div>
          <label>Status</label>
          <div class="check-grid" id="statusFilter"></div>
        </div>
      </div>
      <div class="small">Showing <span id="caseCount">0</span> cases.</div>
      <div style="overflow:auto;">
        <table>
          <thead>
            <tr>
              <th>Suite</th>
              <th>Status</th>
              <th>Case</th>
              <th>Image path</th>
              <th>Tested value</th>
              <th>Outcome summary</th>
              <th>References</th>
            </tr>
          </thead>
          <tbody id="caseTableBody"></tbody>
        </table>
      </div>
    </section>
  </div>

  <script>
    const DATA = {payload};

    const state = {{
      search: "",
      suites: new Set((DATA.suites || []).map(item => item.suite)),
      statuses: new Set(["PASS", "FAIL", "ERROR", "UNKNOWN"]),
    }};

    function statusClass(status) {{
      if (status === "PASS") return "status status-pass";
      if (status === "FAIL") return "status status-fail";
      if (status === "ERROR") return "status status-error";
      return "status status-unknown";
    }}

    function esc(text) {{
      return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
    }}

    function toFileHref(path) {{
      const raw = String(path || "").trim();
      if (!raw) return "";
      const normalized = raw.replace(/\\\\/g, "/");
      if (/^[A-Za-z]:\\//.test(normalized)) {{
        return `file:///${{encodeURI(normalized).replace(/#/g, "%23")}}`;
      }}
      if (normalized.startsWith("/")) {{
        return `file://${{encodeURI(normalized).replace(/#/g, "%23")}}`;
      }}
      return "";
    }}

    function renderPathLink(path, label) {{
      const href = toFileHref(path);
      const text = label || path || "n/a";
      if (!href) return `<span class="small">${{esc(text)}}</span>`;
      return `<a class="path-link mono" href="${{href}}" target="_blank" rel="noopener noreferrer">${{esc(text)}}</a>`;
    }}

    function renderReference(ref) {{
      const value = String(ref || "").trim();
      if (!value) return "";
      if (value.startsWith("session:") || value.startsWith("source:")) {{
        return `<code>${{esc(value)}}</code>`;
      }}
      const href = toFileHref(value);
      if (href) {{
        return `<a class="path-link mono" href="${{href}}" target="_blank" rel="noopener noreferrer">${{esc(value)}}</a>`;
      }}
      return `<code>${{esc(value)}}</code>`;
    }}

    function renderOverview() {{
      document.getElementById("generatedAt").textContent = DATA.generated_at || "n/a";
      document.getElementById("reportDir").textContent = DATA.report_dir || "n/a";
      document.getElementById("dbPath").textContent = (DATA.runtime && DATA.runtime.db_path) || "n/a";

      const statusCounts = (DATA.overview && DATA.overview.status_counts) || {{}};
      const runtimeCounts = (DATA.runtime && DATA.runtime.counts) || {{}};
      const cards = [
        ["Suites", DATA.overview ? DATA.overview.suite_count : 0],
        ["Cases", DATA.overview ? DATA.overview.case_count : 0],
        ["PASS cases", statusCounts.PASS || 0],
        ["FAIL cases", statusCounts.FAIL || 0],
        ["ERROR cases", statusCounts.ERROR || 0],
        ["Chats (active)", runtimeCounts.chats_active ?? "n/a"],
        ["Messages", runtimeCounts.messages_visible ?? "n/a"],
        ["Reviews", runtimeCounts.reviews_total ?? "n/a"],
      ];
      document.getElementById("overviewCards").innerHTML = cards
        .map(([key, value]) => `<div class="card"><div class="k">${{esc(key)}}</div><div class="v">${{esc(value)}}</div></div>`)
        .join("");
    }}

    function renderCliSummary() {{
      const suites = (DATA.suites || []);
      const overview = DATA.overview || {{}};
      const statusCounts = overview.status_counts || {{}};
      const lines = [
        `generated: ${{DATA.generated_at || "n/a"}}`,
        `suites: ${{overview.suite_count ?? 0}} | cases: ${{overview.case_count ?? 0}} | pass: ${{statusCounts.PASS || 0}} | fail: ${{statusCounts.FAIL || 0}} | error: ${{statusCounts.ERROR || 0}}`,
      ];
      for (const item of suites) {{
        const summary = item.summary || {{}};
        lines.push(
          `[${{item.suite || "unknown"}}] ${{item.status || "UNKNOWN"}} total=${{summary.total ?? 0}} pass=${{summary.passed ?? 0}} fail=${{summary.failed ?? 0}} err=${{summary.errors ?? 0}} run=${{item.run_id || "n/a"}}`
        );
      }}
      document.getElementById("cliSummary").textContent = lines.join("\\n");
    }}

    function renderSuites() {{
      const container = document.getElementById("suiteRows");
      const suites = DATA.suites || [];
      if (!suites.length) {{
        container.innerHTML = `<div class="suite-block small">No eval report JSON files found yet in <code>${{esc(DATA.report_dir || "eval_reports")}}</code>.</div>`;
        return;
      }}
      container.innerHTML = suites.map(item => {{
        const summary = item.summary || {{}};
        return `
          <div class="suite-block">
            <div class="row" style="justify-content: space-between; margin-bottom: 8px;">
              <strong>${{esc(item.label || item.suite)}}</strong>
              <span class="${{statusClass(item.status)}}">${{esc(item.status || "UNKNOWN")}}</span>
            </div>
            <div class="small mono">run: ${{esc(item.run_id || "n/a")}}</div>
            <div class="small mono">report: ${{esc(item.report_path || "n/a")}}</div>
            <div class="small">total=${{esc(summary.total ?? 0)}}
              passed=${{esc(summary.passed ?? 0)}}
              failed=${{esc(summary.failed ?? 0)}}
              errors=${{esc(summary.errors ?? 0)}}
              gate_failed=${{esc(summary.gate_failed ?? 0)}}</div>
            <div class="small">generated: ${{esc(item.generated_at || "n/a")}}</div>
          </div>
        `;
      }}).join("");
    }}

    function renderFilters() {{
      const suiteFilter = document.getElementById("suiteFilter");
      const suites = (DATA.suites || []).map(item => [item.suite, item.label || item.suite]);
      suiteFilter.innerHTML = suites.map(([suite, label]) => `
        <span>
          <input type="checkbox" data-suite="${{esc(suite)}}" checked />
          <span>${{esc(label)}}</span>
        </span>
      `).join("");
      suiteFilter.querySelectorAll("input[type=checkbox]").forEach(input => {{
        input.addEventListener("change", () => {{
          if (input.checked) state.suites.add(input.dataset.suite);
          else state.suites.delete(input.dataset.suite);
          renderCases();
        }});
      }});

      const statusFilter = document.getElementById("statusFilter");
      const statuses = ["PASS", "FAIL", "ERROR", "UNKNOWN"];
      statusFilter.innerHTML = statuses.map(status => `
        <span>
          <input type="checkbox" data-status="${{status}}" checked />
          <span>${{status}}</span>
        </span>
      `).join("");
      statusFilter.querySelectorAll("input[type=checkbox]").forEach(input => {{
        input.addEventListener("change", () => {{
          if (input.checked) state.statuses.add(input.dataset.status);
          else state.statuses.delete(input.dataset.status);
          renderCases();
        }});
      }});

      const searchInput = document.getElementById("searchInput");
      searchInput.addEventListener("input", () => {{
        state.search = searchInput.value.trim().toLowerCase();
        renderCases();
      }});
    }}

    function renderCases() {{
      const rows = DATA.cases || [];
      const filtered = rows.filter(item => {{
        if (!state.suites.has(item.suite)) return false;
        if (!state.statuses.has(item.status)) return false;
        if (!state.search) return true;
        const haystack = [
          item.suite_label,
          item.case_id,
          item.tested_value,
          item.outcome_summary,
          (item.references || []).join(" "),
        ].join(" ").toLowerCase();
        return haystack.includes(state.search);
      }});

      document.getElementById("caseCount").textContent = String(filtered.length);
      const body = document.getElementById("caseTableBody");
      if (!filtered.length) {{
        body.innerHTML = `<tr><td colspan="7" class="small">No matching cases.</td></tr>`;
        return;
      }}
      body.innerHTML = filtered.map(item => {{
        const refs = item.references && item.references.length
          ? item.references.map(ref => renderReference(ref)).join("<br />")
          : "<span class='small'>n/a</span>";
        const imageCell = item.image_path
          ? renderPathLink(item.image_path, item.source_name || item.image_path)
          : "<span class='small'>n/a</span>";
        return `
          <tr>
            <td>${{esc(item.suite_label || item.suite)}}</td>
            <td><span class="${{statusClass(item.status)}}">${{esc(item.status)}}</span></td>
            <td><div>${{esc(item.case_id)}}</div><div class="small mono">${{esc(item.run_id || "")}}</div></td>
            <td>${{imageCell}}</td>
            <td>${{esc(item.tested_value || "n/a")}}</td>
            <td>${{esc(item.outcome_summary || "n/a")}}</td>
            <td>${{refs}}</td>
          </tr>
        `;
      }}).join("");
    }}

    renderOverview();
    renderCliSummary();
    renderSuites();
    renderFilters();
    renderCases();
  </script>
</body>
</html>
"""


def build_eval_dashboard(
    *,
    report_dir: Path,
    db_path: Path,
    output_html: Path,
    output_json: Path | None = None,
    max_cases_per_suite: int = 250,
) -> dict[str, Any]:
    dataset = build_dashboard_dataset(
        report_dir=report_dir,
        db_path=db_path,
        max_cases_per_suite=max(1, max_cases_per_suite),
    )
    output_html.parent.mkdir(parents=True, exist_ok=True)
    output_html.write_text(_render_dashboard_html(dataset), encoding="utf-8")
    if output_json is not None:
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(json.dumps(dataset, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return dataset


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a local HTML dashboard from latest eval report artifacts.",
    )
    parser.add_argument(
        "--report-dir",
        default="eval_reports",
        help="Directory containing eval report JSON files.",
    )
    parser.add_argument(
        "--history-db",
        default=".local/runtime_dbs/active/history.db",
        help="Path to runtime history DB for high-level counters.",
    )
    parser.add_argument(
        "--output",
        default=".local/dashboard/eval_dashboard.html",
        help="Path to generated dashboard HTML file.",
    )
    parser.add_argument(
        "--output-json",
        default="",
        help="Optional path to write dashboard dataset JSON.",
    )
    parser.add_argument(
        "--max-cases-per-suite",
        type=int,
        default=250,
        help="Maximum case rows to include per suite report.",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open generated dashboard in the default browser.",
    )
    return parser


def _open_in_browser(path: Path) -> None:
    commands = (
        ["open", str(path)],
        ["xdg-open", str(path)],
    )
    for cmd in commands:
        try:
            subprocess.run(cmd, check=False, capture_output=True)
            return
        except FileNotFoundError:
            continue


def main() -> int:
    args = build_parser().parse_args()
    report_dir = Path(args.report_dir).expanduser()
    db_path = Path(args.history_db).expanduser()
    output_html = Path(args.output).expanduser()
    output_json = Path(args.output_json).expanduser() if str(args.output_json).strip() else None

    started = time.time()
    dataset = build_eval_dashboard(
        report_dir=report_dir,
        db_path=db_path,
        output_html=output_html,
        output_json=output_json,
        max_cases_per_suite=args.max_cases_per_suite,
    )
    elapsed = round(time.time() - started, 2)
    suite_count = len(dataset.get("suites", []))
    case_count = len(dataset.get("cases", []))

    print(f"Eval dashboard written: {output_html}")
    print(f"Suites: {suite_count} | Cases: {case_count} | Elapsed: {elapsed}s")
    runtime = dataset.get("runtime", {})
    if isinstance(runtime, dict) and not runtime.get("available", False):
        print(f"Runtime DB unavailable: {runtime.get('error', 'unknown error')}")
    if output_json is not None:
        print(f"Dataset JSON written: {output_json}")
    if args.open:
        _open_in_browser(output_html)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
