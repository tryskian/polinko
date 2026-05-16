# OCR Reference

This page is the command/reference note for the active OCR eval lane.
`docs/runtime/RUNBOOK.md` owns operator procedure; this file owns the OCR lane
workflow, output surfaces, and tuning knobs.

## Current Snapshot

- Latest tracked progress note:
  - [`docs/research/ocr-progress-2026-05-08.md`](../research/ocr-progress-2026-05-08.md)
- Prior tracked progress note:
  - [`docs/research/ocr-progress-2026-05-01.md`](../research/ocr-progress-2026-05-01.md)
- Current OCR read on `2026-05-08`:
  - growth stability: `25/25` stable, `0` flaky
  - fail cohort: `0` active fail-history cases
  - focus stability: `16/16` stable, `0` flaky
  - runtime OCR follow-up: parked
- Current remaining OCR research signal:
  - low-pressure exploratory output variability inside stable PASS behavior
  - if OCR follow-up reopens, it should be case-design-only and start from:
    - `gx-68844003-002`
    - `gx-6952d743-021`

## Lane Model

1. Treat OCR as the primary eval reliability lane.
2. Run two lane types:
   - `lockset`
     - strict release gate
     - benchmark subsets: `handwriting`, `typed`, `illustration`
   - `growth`
     - fail-tolerant novel-case lane
     - used to measure pass-from-fail movement, not to block release directly

## Canonical Command Sequence

1. End-to-end kernel:
   - `make ocrkernel`
   - optional export-root override:
     - `make ocrkernel CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT`
2. Mine and build cases:
   - `make ocrmine`
   - explicit export-root override:
     - `make ocrmine CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT`
   - optional local default export-root fallback:
     - `CGPT_EXPORT_ROOT_DEFAULT=/abs/path/to/CGPT-DATA-EXPORT`
3. Run the widened growth lane:
   - `make ocrwiden`
   - synchronous fallback:
     - `make ocrwidensync`
   - bounded batch run:
     - `make ocrwiden OCR_GROWTH_EVAL_OFFSET=0 OCR_GROWTH_EVAL_MAX_CASES=40`
   - timeout-safe slice run:
     - `make ocrwiden OCR_GROWTH_EVAL_MAX_CASES=40 OCR_EVAL_TIMEOUT=35 OCR_EVAL_OCR_RETRIES=0`
   - chunked full-window run:
     - `make ocrwidenall OCR_GROWTH_BATCH_SIZE=40`
   - retry-tuned chunked run:
     - `make ocrwidenall OCR_GROWTH_BATCH_SIZE=40 OCR_GROWTH_OCR_RETRIES=2 OCR_GROWTH_OCR_RETRY_DELAY_MS=750`
   - stability replay:
     - `make ocrstablegrowth`
4. Run lockset lanes:
   - `make ocrhandbench`
   - `make ocrtypebench`
   - `make ocrillubench`
5. Run lockset stability replays:
   - `make ocrstablehand`
   - `make ocrstabletype`
   - `make ocrstableillu`
6. Compute growth metrics and fail-derived follow-up:
   - growth metrics:
     - `make ocrgrowth`
   - stable growth fail cohort:
     - `make ocrfails`
     - cohort is filtered to OCR-framed transcript episodes
       (`ocr_framing_signal=true`) via
       `.local/eval_cases/ocr_transcript_cases_review.json`
     - if the cohort is unexpectedly empty, align min-runs with the stability
       report window (for example `make ocrfails OCR_STABILITY_RUNS=3`) or
       rerun `make ocrstablegrowth` with the target run count
   - focused replay on the fail-derived subset:
     - build focused cases:
       - `make ocrfocuscases`
     - focused stability replay:
       - `make eval-ocr-focus-stability`
   - one-shot focus command:
     - `make ocrfocus`
     - optional knobs:
       - `OCR_FOCUS_MAX_CASES=<n>`
       - `OCR_FOCUS_INCLUDE_FAIL_HISTORY=true|false`
       - `OCR_FOCUS_RUNS=<n>`
       - `OCR_FOCUS_CASE_DELAY_MS=<ms>`
       - `OCR_FOCUS_RATE_LIMIT_COOLDOWN_MS=<ms>`
       - `OCR_FOCUS_SKIP_RECENT_RATE_LIMIT=true|false`
       - `OCR_FOCUS_RATE_LIMIT_BACKOFF_SECONDS=<n>`

## Pressure and Rate-Limit Tuning

1. Single-run OCR targets support transient pressure tuning:
   - `OCR_EVAL_OCR_RETRIES=2 OCR_EVAL_OCR_RETRY_DELAY_MS=750`
2. On `HTTP 429`, retries honor upstream `Retry-After` when present:
   - effective delay is the max of configured delay and header delay
3. Fail-fast guard remains:
   - `OCR_MAX_CONSEC_RATE_LIMIT_ERRORS=3`
4. All stability replay targets (`make ocrstable*`) stop remaining runs after
   the first child report with `aborted_due_to_rate_limit=true`.
5. Focused replay adds a preflight backoff guard:
   - if the latest `.local/eval_reports/ocr_focus_stability.json` has a recent
     rate-limit abort, `make eval-ocr-focus-stability` auto-skips within
     `OCR_FOCUS_RATE_LIMIT_BACKOFF_SECONDS`

## Local Output Surfaces

1. Case sets live under `.local/eval_cases/`:
   - growth set:
     - `.local/eval_cases/ocr_transcript_cases_growth.json`
     - growth rows may include `source_quarantine=true` when mined from known
       unstable sources under strict high-signal guards
   - generalization candidates:
     - `.local/eval_cases/ocr_generalization_candidates.json`
     - OCR-ready assets that were not admitted into transcript-mined OCR
       episodes
     - used to widen Beta 2.3 intake beyond correction-shaped transcript asks
   - growth fail cohort:
     - `.local/eval_cases/ocr_growth_fail_cohort.json`
   - growth focus set:
     - `.local/eval_cases/ocr_growth_focus_cases.json`
2. Run and stability reports live under `.local/eval_reports/`:
   - growth stability:
     - `.local/eval_reports/ocr_growth_stability.json`
   - growth batch reports:
     - `.local/eval_reports/ocr_growth_batched_runs/`
   - growth batch summary:
     - `.local/eval_reports/ocr_growth_batched_summary.json`
     - `.local/eval_reports/ocr_growth_batched_summary.md`
3. Growth metrics reports:
   - `.local/eval_reports/ocr_growth_metrics.json`
   - `.local/eval_reports/ocr_growth_metrics.md`
4. Growth focus stability report:
   - `.local/eval_reports/ocr_focus_stability.json`
5. Growth fail cohort report:
   - `.local/eval_reports/ocr_growth_fail_cohort.md`
   - includes:
     - `require_ocr_framing`
     - `skipped_non_framed`
     - `skipped_case_map_mismatch`
   - if `skipped_case_map_mismatch` is non-zero, stability history and the
     current growth case map are from different generations; rerun
     `make ocrstablegrowth` after refreshing growth cases
6. Miner summary includes:
   - `growth_quarantine_cases_written`
   - `growth_regex_only_cases_written`
   - `generalization_candidates_written`

## Notebook and Offline Analysis

1. Notebook surface:
   - `make notes`
2. Offline transcript-mining refresh with no live OCR calls:
   - `make ocr-data CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT`
3. Full online notebook/eval workflow:
   - `make ocr-notebook-workflow CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT`
4. Starter template:
   - `output/jupyter-notebook/ocr-eval-live-filters-starter.ipynb`
