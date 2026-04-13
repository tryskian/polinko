<!-- @format -->

# Eval Evidence Map

This directory preserves first-class eval evidence eras. Beta 1.0 and Beta 2.0
must be interpreted together; Beta 1.0 is not lesser evidence just because its
shape is older and more manually evaluated.

## Phase Semantics

- `beta_1_0`: binary-transition era.
- `beta_2_0`: binary-operational era.

Beta 1.0 marks the move from meaningful manual/screenshot-backed evaluation
toward strict binary eval semantics. Beta 2.0 extends that transition into a
more structured operational eval stack.

## Canonical Eval Database

There should be one app-facing eval database for analysis and UI work:

- canonical derived DB: `.local/runtime_dbs/active/manual_evals.db`
- rebuild command: `make manual-evals-db`
- current source input: `.local/runtime_dbs/active/history.db`
- optional Beta 1.0 source input:
  `.local/legacy_eval/archive_legacy_eval/databases/.polinko_history.db`

`manual_evals.db` is the integrated eval warehouse. It imports legacy and
current history sources into one schema with explicit `era`, `source_key`,
`source_history_db`, `source_session_id`, and `source_run_id` provenance. The
source DBs remain raw inputs, not separate user-facing eval truths.

The 2026-04-13 local integrated build contains:

- `beta_1_0`: 69 sessions, 90 OCR runs, 116 manual feedback rows.
- `current`: 634 sessions, 636 OCR runs, 0 manual feedback rows.
- total: 703 sessions, 726 OCR runs, 116 feedback rows.

`eval_viz.db` is retired as an app-facing eval database. If an old local copy
exists, treat it as a legacy cache only; do not wire current UI or analysis
against it. The 2026-04-13 active local copy was moved to
`.local/runtime_dbs/archive/retired_eval_viz_20260413/eval_viz.db`.

## Beta 1.0

Documents:

- local full snapshot:
  `/Users/tryskian/Github/old/polinko-incase`
- `docs/eval/beta_1_0/build_snapshot_polinko-incase/docs/`
- includes archived governance, runbook, state, decisions, research, portfolio,
  and transcript material from the beta 1.0 build snapshot.

Databases:

- local full snapshot DBs:
  - `/Users/tryskian/Github/old/polinko-incase/.polinko_history.db`
  - `/Users/tryskian/Github/old/polinko-incase/.polinko_memory.db`
  - `/Users/tryskian/Github/old/polinko-incase/.polinko_vector.db`
- local-only legacy database snapshots may exist under
  `.local/legacy_eval/archive_legacy_eval/databases/`.
- these are not tracked in git and should be treated as private/local audit
  material.
- Beta 1.0 eval rows should be consumed through the integrated
  `manual_evals.db` build, not by wiring UI/docs directly to a separate legacy
  database.

Evals:

- meaningful manual evaluation data in the full snapshot:
  `/Users/tryskian/Github/old/polinko-incase`
- meaningful screenshot-backed/manual OCR evaluation evidence under
  `docs/eval/beta_1_0/`
- archived OCR prompts/reports under
  `docs/eval/beta_1_0/build_snapshot_polinko-incase/docs/`
- archived eval reports under
  `docs/eval/beta_1_0/build_snapshot_polinko-incase/eval_reports/`
- archived raw portfolio evidence under
  `docs/eval/beta_1_0/build_snapshot_polinko-incase/docs/portfolio/raw_evidence/`

Logic:

- full beta 1.0 runtime/eval logic is preserved locally at
  `/Users/tryskian/Github/old/polinko-incase`.
- archived runtime/API/tooling/test logic under
  `docs/eval/beta_1_0/build_snapshot_polinko-incase/`
- includes earlier OCR, hallucination, retrieval, style, CLIP A/B, evidence
  indexing, metadata audit, and portfolio tooling paths.

Sankey role:

- left-side/legacy eval-era evidence.
- records meaningful manual evaluation and the transition into binary eval
  semantics.
- provides the contrast that makes Beta 2.0/current eval data meaningful.

## Beta 2.0

Documents:

- `docs/eval/beta_2_0/`
- contains active-era case files, trace artifacts, and report snapshots in a
  flatter structure.

Databases:

- active local runtime databases may exist under `.local/runtime_dbs/active/`.
- `history.db` is the current raw runtime source input.
- `manual_evals.db` is the canonical integrated eval warehouse for analysis and
  UI work.
- these are local-only and should not be committed unless explicitly approved.

Evals:

- structured report artifacts under `docs/eval/beta_2_0/`
- includes OCR, OCR recovery, OCR safety, hallucination, retrieval, file search,
  style, response behaviour, CLIP A/B, and trace artifacts.

Logic:

- current runtime/eval logic lives in the active repo source tree, especially:
  - `api/`
  - `core/`
  - `tools/`
  - `tests/`
  - `docs/runtime/`
  - `docs/governance/`

Sankey role:

- right-side/current eval-era evidence.
- shows what became structured, operational, and repeatable after the beta 1.0
  binary transition.

## Interpretation Rule

Do not compare Beta 1.0 and Beta 2.0 only by artifact neatness. Compare them by
role:

- Beta 1.0 explains the transition logic.
- Beta 1.0 manual evaluations are meaningful data.
- Beta 2.0 shows operationalization of that transition.
- Current eval work extends the operational lane.

Do not commit the full Beta 1.0 snapshot wholesale. It contains local-only
runtime state, `.env` material, `.git` metadata, editor history, and database
files. Promote only curated evidence maps or explicitly approved artifacts.
