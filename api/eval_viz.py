from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPORT_SUBDIRS = ("ocr_stability_runs", "ocr_growth_stability_runs")
_RUN_ID_TIMESTAMP_RE = re.compile(r"^(?P<epoch>\d{9,})-r\d+$")


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


def build_pass_fail_viz_payload(report_root: Path | None = None, *, max_evals: int = 140) -> dict[str, Any]:
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
    latest_point = points[-1] if points else {
        "run_id": "n/a",
        "timestamp_ms": int(datetime.now(tz=timezone.utc).timestamp() * 1000),
        "label": "n/a",
        "pass": 0,
        "fail": 0,
        "errors": 0,
        "total": 0,
        "source": "n/a",
    }

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


def render_pass_fail_viz_html(refresh_ms: int = 4000, chart_max_points: int = 32) -> str:
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Polinko PASS/FAIL Live</title>
  <style>
    :root {{
      --bg: #050505;
      --panel: #0b0b0b;
      --line: #222;
      --text: #f5f5f5;
      --muted: #a6a6a6;
      --pass: #f2f2f2;
      --fail: #7a7a7a;
      --accent: #d0d0d0;
    }}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; padding: 0; background: var(--bg); color: var(--text); font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; }}
    main {{ height: 100vh; display: grid; grid-template-rows: auto minmax(220px, 34vh) minmax(220px, 1fr) minmax(170px, 28vh); gap: 10px; padding: 14px; }}
    .top {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }}
    .pill {{ border: 1px solid var(--line); border-radius: 999px; padding: 8px 12px; background: var(--panel); }}
    .pill select {{
      background: #0e0e0e;
      border: 1px solid #2b2b2b;
      color: var(--text);
      border-radius: 999px;
      padding: 3px 10px;
      font-size: 12px;
    }}
    .muted {{ color: var(--muted); }}
    .chart-wrap {{ border: 1px solid var(--line); background: var(--panel); border-radius: 12px; padding: 8px; position: relative; overflow: hidden; }}
    #chart {{ width: 100%; height: 100%; }}
    .chart-tip {{ position: absolute; pointer-events: none; background: rgba(0,0,0,.85); border: 1px solid #3a3a3a; padding: 8px; border-radius: 8px; font-size: 12px; color: #fff; display: none; max-width: 280px; }}
    .table-wrap-panel {{ border: 1px solid var(--line); background: var(--panel); border-radius: 12px; min-height: 0; display: flex; flex-direction: column; }}
    .table-title {{ padding: 10px 12px 0; font-size: 12px; color: var(--muted); }}
    .table-wrap {{ min-height: 0; overflow: auto; padding: 8px 10px 10px; flex: 1; }}
    table {{ width: 100%; border-collapse: collapse; table-layout: auto; }}
    th, td {{ text-align: left; vertical-align: top; border-bottom: 1px solid #1f1f1f; padding: 8px 10px; font-size: 12px; }}
    th {{ position: sticky; top: 0; background: #0f0f0f; z-index: 1; }}
    tr:hover {{ background: #111; cursor: pointer; }}
    tr.selected {{ background: #181818; outline: 1px solid #2b2b2b; }}
    td.obs {{ white-space: pre-wrap; word-break: break-word; max-width: 520px; }}
    td.exp {{ white-space: pre-wrap; word-break: break-word; max-width: 320px; }}
    .detail {{ border: 1px solid var(--line); border-radius: 12px; background: var(--panel); padding: 12px; overflow: auto; min-height: 0; }}
    .detail-card {{ border: 1px solid #2a2a2a; border-radius: 10px; padding: 10px; background: #0f0f0f; }}
    .detail h3 {{ margin: 0 0 8px; font-size: 14px; }}
    .detail pre {{ margin: 6px 0 0; white-space: pre-wrap; word-break: break-word; font-size: 12px; color: #ddd; }}
  </style>
  <script src=\"https://cdn.jsdelivr.net/npm/d3@7\"></script>
</head>
<body>
  <main>
    <section class=\"top\">
      <div class=\"pill\">run: <span id=\"runId\">n/a</span></div>
      <div class=\"pill\">pass: <strong id=\"passCount\">0</strong></div>
      <div class=\"pill\">fail: <strong id=\"failCount\">0</strong></div>
      <div class=\"pill\">total: <span id=\"totalCount\">0</span></div>
      <div class=\"pill\">chart points: <span id=\"chartPoints\">0 / 0</span></div>
      <div class=\"pill\">window:
        <select id=\"chartPointSelect\" aria-label=\"chart point window\">
          <option value=\"16\">16</option>
          <option value=\"32\" selected>32</option>
          <option value=\"64\">64</option>
          <option value=\"120\">120</option>
        </select>
      </div>
      <div class=\"pill muted\">updated: <span id=\"updatedAt\">n/a</span></div>
    </section>

    <section class=\"chart-wrap\">
      <div id=\"chart\"></div>
      <div id=\"chartTip\" class=\"chart-tip\"></div>
    </section>

    <section class=\"table-wrap-panel\">
      <div class=\"table-title\">latest run eval rows · hover expands detail · click persists</div>
      <div class=\"table-wrap\">
        <table>
          <thead>
            <tr>
              <th style=\"width: 96px\">Outcome</th>
              <th style=\"width: 180px\">Item</th>
              <th>Expected</th>
              <th>Observed</th>
            </tr>
          </thead>
          <tbody id=\"evalRows\"></tbody>
        </table>
      </div>
    </section>

    <aside class=\"detail\" id=\"detailPane\">
      <h3>Detail</h3>
      <div class=\"detail-card\" id=\"detailCard\">Hover a row to expand detail. Click to persist.</div>
    </aside>
  </main>

  <script>
    const REFRESH_MS = {int(refresh_ms)};
    const dataUrl = '/viz/pass-fail/data';
    const DEFAULT_MAX_CHART_POINTS = {int(chart_max_points)};
    const state = {{ payload: null, selectedItem: null, chartMaxPoints: DEFAULT_MAX_CHART_POINTS }};

    const runIdEl = document.getElementById('runId');
    const passEl = document.getElementById('passCount');
    const failEl = document.getElementById('failCount');
    const totalEl = document.getElementById('totalCount');
    const chartPointsEl = document.getElementById('chartPoints');
    const chartPointSelectEl = document.getElementById('chartPointSelect');
    const updatedEl = document.getElementById('updatedAt');
    const rowsEl = document.getElementById('evalRows');
    const detailCardEl = document.getElementById('detailCard');

    function fmtDate(ms) {{
      if (!ms) return 'n/a';
      const d = new Date(ms);
      if (Number.isNaN(d.getTime())) return 'n/a';
      return d.toLocaleString();
    }}

    function normalizeChartPointWindow(value) {{
      const parsed = Number.parseInt(String(value || ''), 10);
      if (!Number.isFinite(parsed)) return DEFAULT_MAX_CHART_POINTS;
      return Math.max(8, Math.min(parsed, 120));
    }}

    function updateChartWindowParam(nextValue) {{
      const url = new URL(window.location.href);
      url.searchParams.set('chart_max_points', String(nextValue));
      window.history.replaceState(null, '', url.toString());
    }}

    function initChartWindowControl() {{
      const url = new URL(window.location.href);
      const fromQuery = normalizeChartPointWindow(url.searchParams.get('chart_max_points'));
      state.chartMaxPoints = fromQuery;
      chartPointSelectEl.value = String(fromQuery);
      if (chartPointSelectEl.value !== String(fromQuery)) {{
        const option = document.createElement('option');
        option.value = String(fromQuery);
        option.textContent = String(fromQuery);
        chartPointSelectEl.appendChild(option);
        chartPointSelectEl.value = String(fromQuery);
      }}
      chartPointSelectEl.addEventListener('change', () => {{
        state.chartMaxPoints = normalizeChartPointWindow(chartPointSelectEl.value);
        updateChartWindowParam(state.chartMaxPoints);
        if (state.payload) renderChart(state.payload);
      }});
    }}

    function setDetail(row) {{
      if (!row) {{
        detailCardEl.textContent = 'Hover a row to expand detail. Click to persist.';
        return;
      }}
      const imagePath = row.image_path || '';
      const imageHref = imagePath ? `file://${{encodeURI(imagePath)}}` : '';
      detailCardEl.innerHTML = `
        <div><strong>${{row.outcome}}</strong> · ${{row.item}}</div>
        <div class=\"muted\" style=\"margin-top:6px\">source</div>
        <pre>${{row.source_name || '(none)'}}</pre>
        <div class=\"muted\" style=\"margin-top:8px\">asset path</div>
        <pre>${{imagePath || '(none)'}}</pre>
        ${{imageHref ? `<div style=\"margin-top:4px\"><a href=\"${{imageHref}}\" style=\"color:#d9d9d9\" target=\"_blank\" rel=\"noopener noreferrer\">open asset path</a></div>` : ''}}
        <div class=\"muted\" style=\"margin-top:6px\">expected</div>
        <pre>${{row.expected || '(none)'}}</pre>
        <div class=\"muted\" style=\"margin-top:8px\">observed</div>
        <pre>${{row.observed || '(empty)'}}</pre>
      `;
    }}

    function renderRows(payload) {{
      const rows = payload.evals || [];
      rowsEl.innerHTML = '';
      for (const row of rows) {{
        const tr = document.createElement('tr');
        if (state.selectedItem && state.selectedItem === row.row_key) tr.classList.add('selected');
        tr.innerHTML = `
          <td>${{row.outcome}}</td>
          <td>${{row.item}}</td>
          <td class=\"exp\">${{row.expected || ''}}</td>
          <td class=\"obs\">${{row.observed || ''}}</td>
        `;
        tr.addEventListener('mouseenter', () => {{
          setDetail(row);
        }});
        tr.addEventListener('mouseleave', () => {{
          if (!state.selectedItem) {{
            setDetail(null);
            return;
          }}
          const selected = rows.find(r => r.row_key === state.selectedItem);
          setDetail(selected || null);
        }});
        tr.addEventListener('click', () => {{
          if (state.selectedItem === row.row_key) {{
            state.selectedItem = null;
            setDetail(null);
          }} else {{
            state.selectedItem = row.row_key;
            setDetail(row);
          }}
          renderRows(payload);
        }});
        rowsEl.appendChild(tr);
      }}
    }}

    function renderSummary(payload) {{
      const s = payload.summary || {{}};
      runIdEl.textContent = s.run_id || 'n/a';
      passEl.textContent = String(s.pass || 0);
      failEl.textContent = String(s.fail || 0);
      totalEl.textContent = String(s.total || 0);
      updatedEl.textContent = payload.updated_at || 'n/a';
    }}

    function renderChart(payload) {{
      const root = document.getElementById('chart');
      root.innerHTML = '';
      const allPoints = (payload.points || []).map((p, i) => ({{
        ...p,
        idx: i,
        label: p.label || `run-${{i + 1}}`,
        pass: Number(p.pass || 0),
        fail: Number(p.fail || 0),
        total: Number(p.total || 0),
        timestamp_ms: Number(p.timestamp_ms || 0),
      }}));
      const points = allPoints.length > state.chartMaxPoints
        ? allPoints.slice(-state.chartMaxPoints)
        : allPoints;
      chartPointsEl.textContent = `${{points.length}} / ${{allPoints.length}}`;

      if (!points.length) {{
        chartPointsEl.textContent = '0 / 0';
        root.innerHTML = '<div class="muted" style="padding:12px">No runs yet. Execute OCR evals, then refresh.</div>';
        return;
      }}

      const w = root.clientWidth || 1200;
      const h = root.clientHeight || 320;
      const margin = {{ top: 12, right: 16, bottom: 28, left: 42 }};
      const innerW = w - margin.left - margin.right;
      const innerH = h - margin.top - margin.bottom;

      const svg = d3.select(root).append('svg').attr('width', w).attr('height', h);
      const g = svg.append('g').attr('transform', `translate(${{margin.left}},${{margin.top}})`);

      const keys = ['pass', 'fail'];
      const stacked = d3.stack().keys(keys)(points);
      const yMax = d3.max(points, d => d.pass + d.fail) || 1;
      const x = d3.scaleLinear().domain([0, Math.max(points.length - 1, 1)]).range([0, innerW]);
      const y = d3.scaleLinear().domain([0, yMax]).nice().range([innerH, 0]);

      const area = d3
        .area()
        .x((d, i) => x(i))
        .y0(d => y(d[0]))
        .y1(d => y(d[1]))
        .curve(d3.curveMonotoneX);

      const colors = {{ pass: 'var(--pass)', fail: 'var(--fail)' }};

      g.selectAll('path.layer')
        .data(stacked)
        .enter()
        .append('path')
        .attr('class', 'layer')
        .attr('fill', d => colors[d.key])
        .attr('opacity', 0.7)
        .attr('d', area)
        .attr('transform', `translate(${{innerW}},0)`)
        .transition()
        .duration(700)
        .attr('transform', 'translate(0,0)');

      g.append('g')
        .attr('transform', `translate(0,${{innerH}})`)
        .call(d3.axisBottom(x).ticks(Math.min(points.length, 8)).tickFormat(i => points[Math.round(i)]?.label || ''))
        .call(g => g.selectAll('text').attr('fill', '#aaa').attr('font-size', 10));

      g.append('g')
        .call(d3.axisLeft(y).ticks(5))
        .call(g => g.selectAll('text').attr('fill', '#aaa').attr('font-size', 10));

      const tip = document.getElementById('chartTip');
      g.selectAll('circle.dot')
        .data(points)
        .enter()
        .append('circle')
        .attr('class', 'dot')
        .attr('cx', d => x(d.idx))
        .attr('cy', d => y(d.pass + d.fail))
        .attr('r', 3)
        .attr('fill', '#f5f5f5')
        .on('mouseenter', (event, d) => {{
          tip.style.display = 'block';
          tip.innerHTML = `
            <div><strong>${{d.label}}</strong></div>
            <div>pass: ${{d.pass}} · fail: ${{d.fail}} · total: ${{d.total}}</div>
            <div class="muted">${{fmtDate(d.timestamp_ms)}}</div>
          `;
        }})
        .on('mousemove', event => {{
          const rect = root.getBoundingClientRect();
          tip.style.left = `${{event.clientX - rect.left + 10}}px`;
          tip.style.top = `${{event.clientY - rect.top + 10}}px`;
        }})
        .on('mouseleave', () => {{
          tip.style.display = 'none';
        }});
    }}

    async function refresh() {{
      try {{
        const res = await fetch(dataUrl, {{ cache: 'no-store' }});
        if (!res.ok) throw new Error(`HTTP ${{res.status}}`);
        const payload = await res.json();
        state.payload = payload;
        renderSummary(payload);
        renderChart(payload);
        renderRows(payload);
        if (state.selectedItem) {{
          const found = (payload.evals || []).find(r => r.row_key === state.selectedItem);
          if (found) setDetail(found);
          if (!found) {{
            state.selectedItem = null;
            setDetail(null);
          }}
        }}
      }} catch (err) {{
        console.error(err);
      }}
    }}

    initChartWindowControl();
    refresh();
    setInterval(refresh, REFRESH_MS);
  </script>
</body>
</html>
"""
