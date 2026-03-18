<!-- @format -->

# Hybrid OpenAI Adoption Plan (No Runtime Migration)

## Scope Boundary

- Keep current runtime/API behavior unchanged.
- Add adoption checkpoints around evals and traceability first.
- Only promote to runtime integration after readiness gates pass repeatedly.

## Phase Status

- Phase 1: implemented.
- Phase 2: implemented.
- Phase 3: scaffold implemented (pilot dry-run path only).

## Phase 1 (Implemented): Report-Level Readiness Gate

- Command: `make hybrid-openai-readiness`
- Inputs:
  - latest `style-strict-*.json`
  - latest `file-search-*.json`
  - latest two `clip-ab-*.json`
- Pass criteria:
  - strict style: all-pass
  - file-search: all-pass, zero errors/skips
  - CLIP pair: each report meets D-040 thresholds
- Output:
  - `READY` or `NOT_READY` with per-gate diagnostics

## Phase 2 (Implemented): Trace Artifact Contract

- Shared schema and writer:
  - `tools/eval_trace_artifacts.py`
  - schema version: `polinko.eval_trace.v1`
  - default append path:
    `docs/portfolio/raw_evidence/INBOX/eval_trace_artifacts.jsonl`
- Trace payload includes:
  - `trace_id`, `trace_type`, `generated_at`
  - `run_id`, `tool_name`
  - `model_metadata`
  - `source_artifacts`
  - `gate_outcomes`
  - `summary`, `metadata`
- Tooling wired to emit append-only traces:
  - `tools/eval_file_search.py`
  - `tools/eval_clip_ab.py`
  - `tools/eval_style.py`
  - `tools/eval_ocr.py`
  - `tools/eval_ocr_recovery.py`
  - `tools/eval_retrieval.py`
  - `tools/eval_hallucination.py`
  - `tools/check_hybrid_openai_readiness.py`
- Runtime boundary preserved:
  - no `/chat` behavior changes
  - no runtime path migration

## Phase 3 (Implemented Scaffold): OpenAI-Native Tooling Pilot (No Runtime Migration)

- Pilot scope v1 (planned):
  - offline metadata bridge from local eval trace artifacts to
    OpenAI-compatible trace/grader payload shape
  - no runtime `/chat` call path changes
  - no prompt rewrite or orchestration-path default changes
- In scope:
  - tooling-only transformer for existing
    `eval_trace_artifacts.jsonl` records
  - deterministic mapping spec for:
    - trace identifier
    - run metadata
    - gate outcomes
    - source artifact references
  - dry-run validation output for inspection before any provider upload path
- Out of scope:
  - replacing local eval harness execution with platform-native eval runners
  - runtime request/response interception
  - default-on config changes
- Guardrails:
  - opt-in via env flags
  - rollback-safe defaults (`off`)
  - runtime parity checks before/after enablement
- Success criteria:
  - deterministic transformer output from identical input artifacts
  - zero changes to `make test` behavior/results
  - unchanged `/chat` request/response contract
  - documented rollback path (`unset flag` + disable pilot tooling command)
- Scaffold status (implemented):
  - dry-run bridge tool: `tools/hybrid_openai_trace_bridge.py`
  - backfill tool: `tools/backfill_eval_trace_artifacts.py`
  - preview checker: `tools/check_hybrid_openai_bridge_preview.py`
  - OpenAI custom-eval exporter:
    `tools/export_openai_eval_dataset.py`
  - OpenAI custom-eval export checker:
    `tools/check_openai_eval_dataset_export.py`
  - command:
    `make hybrid-openai-pilot-dry-run HYBRID_OPENAI_PILOT_ENABLED=true`
  - validation command:
    `make hybrid-openai-pilot-check`
  - OpenAI custom-eval export command:
    `make hybrid-openai-export-dataset`
  - OpenAI custom-eval export validation:
    `make hybrid-openai-export-check`
  - OpenAI custom-eval one-command cycle:
    `make hybrid-openai-export-cycle`
  - one-command cycle:
    `make hybrid-openai-pilot-cycle`
  - default remains disabled (`HYBRID_OPENAI_PILOT_ENABLED=false`)
  - output (append-only preview):
    `docs/portfolio/raw_evidence/INBOX/openai_trace_bridge_preview.jsonl`
  - output (overwrite-per-run export):
    - `docs/portfolio/raw_evidence/INBOX/openai_eval_dataset.jsonl`
    - `docs/portfolio/raw_evidence/INBOX/openai_eval_item_schema.json`
  - latest local validation (2026-03-16):
    - backfill source rows: `17`
    - transformed rows per bridge run: `17`
    - preview checker: `OK`

## Promotion Rule

- Promote to next phase only when:
  - readiness gate stays green for two consecutive validation cycles
  - trace artifacts are generated consistently in report workflows
  - no runtime/API regression appears in `make test` and quality-gate family
  - decisions + state docs are updated with concrete artifact references
