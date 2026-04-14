<!-- @format -->

# Project State

Last updated: 2026-04-13

## Current Truth

- Runtime is local-first and backend-first:
  - FastAPI API + CLI are canonical execution surfaces.
  - Prompt/runtime behavior remains minimal and deterministic.
- End-of-day closeout is green for 2026-04-14:
  - `make eod` passed end-to-end (`doctor-env`, `lint-docs`, and `test` with
    393 passing tests).
  - managed background runtime tasks were stopped (`server-daemon` and
    managed `caffeinate`).
- Portfolio shell route contract is active:
  - `GET /` redirects to `GET /portfolio`.
  - `GET /portfolio` serves `ui/index.html` (build output).
  - source of truth for shell edits is `frontend/`.
- Twin Sankey portfolio shell iteration is active in the frontend lane:
  - four-section Sankey strip now renders from real local data through
    `GET /portfolio/sankey-data`.
  - PR `#302` merged the latest visible scaffold checkpoint to `main`.
  - current visible row is `pipeline -> sankey 1 -> sankey 2 -> sankey 3 ->
    sankey 4 -> pipeline`.
  - that scaffold is a checkpoint, not the next implementation lock. The next
    frontend pass should reset from a clean slate rather than retrofit existing
    section logic.
  - the left Sankey uses Beta 1.0 manual feedback rows from
    `.local/runtime_dbs/active/manual_evals.db`.
  - the right Sankey uses current OCR binary gate report cases from
    `.local/eval_reports/`.
  - the connector graph uses source-side signal/category counts only; it is not
    a row-level join between legacy and current datasets.
  - `graphs.bridge` remains an API payload key for compatibility; it is not a
    portfolio IA label.
  - missing required sources produce an explicit no-data state, not decorative
    placeholder links.
  - beta 1.0 marks the transition to binary eval semantics and is the evidence
    layer for interpreting beta 2.0/current eval data.
  - beta 1.0 manual evaluations are meaningful data, not weaker evidence.
  - beta 1.0 and beta 2.0 should remain equally prominent across documents,
    databases, evals, and logic; see `docs/eval/README.md`.
  - `.local/runtime_dbs/active/manual_evals.db` is the single integrated
    app-facing eval warehouse; it is rebuilt from current history plus optional
    Beta 1.0 history with era/source provenance.
  - `eval_viz.db` is retired from the active app-facing path; the previous
    active local cache was archived under `.local/runtime_dbs/archive/`.
  - the full local beta 1.0 parity source is
    `/Users/tryskian/Github/old/polinko-incase`.
  - canonical beta 1.0 context is in earlier `DECISIONS` entries, not only the
    latest entries.
  - legacy and current eval eras may both include OCR evidence.
  - legacy OCR evidence includes screenshot-backed/manual eval artifacts under
    `docs/eval/beta_1_0/`.
  - local-only transcripts under `docs/peanut/transcripts/` are source
    evidence for reasoning/eval interpretation; `DECISIONS` records the
    binding interpretation and must not contradict transcript evidence.
  - long-term context should preserve evidence chains; do not replace source
    transcripts/reports with summary-of-summary state.
  - source remains `frontend/` with generated output in `ui/`.
- OCR-forward eval model remains active:
  - lockset lane is release-gating.
  - growth lane is fail-tolerant and signal-seeking.
- Eval gate semantics remain strict binary (`pass`/`fail`).
- Pass/fail visualization defaults to Pol-3 OCR binary gate reports under
  `.local/eval_reports/` so FAIL pressure stays visible.
- `manual_evals.db` remains the canonical integrated manual-eval warehouse and
  fallback/explicit DB path, not the primary strict-gate chart source.

## Active Priorities

1. Portfolio shipping lane:
   - start the next frontend pass from a clean slate.
   - remove current portfolio UI artefacts/wiring intentionally before
     rebuilding the desired IA.
   - preserve real-data evidence contracts unless explicitly changing backend
     data shape.
2. OCR reliability lane:
   - continue growth/lockset operations without changing binary gate semantics.
   - keep FAIL-first observability in `/viz/pass-fail`.
3. Documentation hygiene lane:
   - keep facts anchored to source evidence + binding decisions; avoid
     recursive summary drift.

## Canonical Sources

- Rules/authority: `docs/governance/CHARTER.md`
- Structure: `docs/runtime/ARCHITECTURE.md`
- Commands/procedure: `docs/runtime/RUNBOOK.md`
- Decision history: `docs/governance/DECISIONS.md`

## Validation Baseline

- `make doctor-env`
- `make eod-docs-check`
- `make lint-docs`
- `make test`
- `make frontend-build` (when `frontend/` changes)
