<!-- @format -->

# Eval Evidence Map

This folder is the tracked eval evidence lane.

Use it when you need:

- beta-era context
- case files and report snapshots
- the shortest path from eval artifacts to public proof

![Polinko evidence sankey](../public/diagrams/polinko-evidence-sankey.svg)

## Beta Meanings

- `beta_1_0`
  - binary-transition era
  - manual and screenshot-backed evaluation still carries real evidence weight
- `beta_2_0`
  - binary-operational era
  - flatter case/report structure and repeatable eval commands
- `beta_2_3`
  - frozen method-boundary snapshot for next-beta cleanup
  - OCR generalization pressure starts from the stabilized current-image base
  - tracked summary points to curated notes and evidence, with raw export
    material promoted only after explicit curation
- `pre-Beta 2.4`
  - staged research-model contract before the next evidence folder is cut
  - the discarded run-level rollup hypothesis is not being carried forward
  - row and case evidence remain source-bound before lane-level summaries
  - manual eval workbench sources stay canonical inputs

Beta 1.0, Beta 2.0, Beta 2.3, and pre-Beta 2.4 should be read by role.
Beta 1.0 explains the transition into binary evals. Beta 2.0 shows the
operationalized lane. Beta 2.3 freezes the current method read before the
next beta work starts. Pre-Beta 2.4 names the next source-first
research-model contract.

## Current Canonical Surfaces

The manual eval workbench is the human-judged research workspace. It includes
notebooks, local evidence databases, chat artifacts, feedback, checkpoints,
notes, exports, and runtime history.

- notebook workspace:
  - `make notes`
  - aliases: `make notebook`, `make nb`
- integrated manual-eval warehouse:
  - `.local/runtime_dbs/active/manual_evals.db`
  - rebuild with `make manual-evals-db`
- active chat artifacts:
  - `POST /chat`
  - `/chats/*`
  - includes feedback, checkpoints, notes, exports, and personalization rows
- raw current runtime source:
  - `.local/runtime_dbs/active/history.db`
- live strict-gate observability plus tracked lane snapshots:
  - `.local/eval_reports/`
  - `/viz/pass-fail`
  - `/viz/pass-fail/data`

Manual evals and strict OCR gate reports answer different questions:

- manual evals capture human judgment and qualitative notes from the manual
  eval workbench
- OCR gate reports preserve binary fail pressure
- `/viz/pass-fail` keeps the live chart on the active window and uses tracked
  eval files to keep the wider lane map visible below it
- tracked lane cards now expose direct links to:
  - the underlying tracked artifact
  - the promoted research note when that lane has one

Do not flatten one into the other.

## Tracked Gate Contract

- OCR gate reports stay strictly `pass` / `fail`
- OCR candidate cleanup happens upstream of eval:
  - malformed candidates
  - duplicate candidates
  - known-bad inputs
- non-OCR lanes can still use richer staged or thin-lane method surfaces where
  the research question is not simple extraction correctness
- judge detail and qualitative notes can enrich a report, but they do not
  create a third OCR gate state
- thin new lanes can begin as row-local human `pass` / `fail` evidence before
  larger automation
- run-level verdicts are not canonical rollups for the active manual eval
  workbench

## What Is Tracked Here

### Beta 1.0

- curated historical evidence under `docs/eval/beta_1_0/`
- archived build snapshot material under
  `docs/eval/beta_1_0/build_snapshot_polinko-incase/`
- role in the evidence map:
  - left-side/legacy evidence for the Sankey payload

### Beta 2.0

- active-era case files and report snapshots under `docs/eval/beta_2_0/`
- includes OCR, OCR recovery, OCR safety, hallucination, retrieval, file
  search, style, response behaviour, CLIP A/B, and operator burden
- append-only eval trace artifacts stay local under `eval_reports/`; they are
  not auto-promoted into the tracked beta surface
- current non-OCR promoted lane lives in the tracked style surface for
  co-reasoning reliability
- current thin-lane operator burden surface lives in:
  - `docs/eval/beta_2_0/operator_burden_rows.json`
  - summarize with:
    - `make operator-burden-report`
    - the summary now surfaces:
      - pass anchors
      - retained failures
      - evicted failures
  - widen candidate rows locally with:
    - `python3 -m tools.build_behaviour_backlog_from_export --export-root /abs/path/to/CGPT-DATA-EXPORT`
- role in the evidence map:
  - right-side/current evidence for the Sankey payload

### Beta 2.3

- frozen method-boundary snapshot under `docs/eval/beta_2_3/`
- source boundary:
  - `2026-05-16`
- snapshot role:
  - preserve the current Beta 2.3 read before broad cleanup/refactor work
  - record high-level OCR generalization intake counts
  - point to the tracked research notes and prior operational evidence files
  - hand off into the staged pre-Beta 2.4 research-model contract
- entry points:
  - [Beta 2.3 eval snapshot](./beta_2_3/README.md)
  - [Beta 2.3 snapshot manifest](./beta_2_3/research_snapshot_manifest.json)
  - [Pre-Beta 2.4 research model contract](../research/pre-beta-2-4-research-model-contract-2026-05-19.md)

## What Stays Local

- live runtime databases under `.local/runtime_dbs/active/`
- archived runtime databases under `.local/runtime_dbs/archive/`
- export-mined candidate backlogs under `.local/eval_cases/`
- full Beta 1.0 local snapshot databases and runtime state
- private exports, scratch screenshots, and raw local audit material

Do not commit the full Beta 1.0 snapshot wholesale. Promote only curated
evidence or explicitly approved artifacts.

## Interpretation Rule

- compare Beta 1.0 and Beta 2.0 by role, not by artifact neatness
- treat transcripts, screenshots, and raw reports as source evidence
- let decisions and public notes interpret the evidence, not replace it
