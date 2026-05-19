<!-- @format -->

# Pre-Beta 2.4 Research Model Contract

Date: `2026-05-19`

Status: `staged`

## Boundary

`Beta 2.3` is the frozen baseline. Its eval snapshot lives under
`docs/eval/beta_2_3/` and remains the source for the current method read.

`pre-Beta 2.4` names the next research-model contract before new evidence is
cut. The first evidence folder is cut when a real pulse exists.

The active question is whether Polinko can move from lane snapshots to bounded
research pulses while preserving row evidence and the manual eval workbench as
source material.

## Contract

- OCR remains case-level `pass` / `fail` under broader generalization pressure.
- OCR post-fail handling can still use `retain` / `evict` case governance.
- Non-OCR research pulses can use run-level `PASS` / `FAIL`.
- Rows inside a pulse stay inspectable evidence labels:
  - `anchor`
  - `counted seam`
  - `excluded noise`
- The pulse verdict stays readable against both raw and counted rows.

## Evidence Stack

The research model has four layers:

1. Source artifacts from active workbench and eval surfaces.
2. Item-level labels that preserve row evidence.
3. Pulse-level verdict for bounded non-OCR runs.
4. Promotion claim only after a repeated pulse shape stabilizes.

Canonical source surfaces include:

- `POST /chat`
- `/chats/*`
- `.local/runtime_dbs/active/manual_evals.db`
- `.local/runtime_dbs/active/history.db`
- tracked eval reports and research notes under `docs/eval/` and
  `docs/research/`

The staged contract sits above these sources and keeps them canonical.

## First Kernel Shape

The first pre-Beta 2.4 pulse should be small, predetermined, and auditable.

It should record:

- raw row count
- counted row count
- excluded rows with narrow reasons
- row labels before the run verdict
- final pulse verdict

A new `docs/eval/beta_2_4/` evidence folder should be cut when real evidence
exists.

## Decision Rule

A pre-Beta 2.4 pulse can inform the next beta only when the evidence stack stays
traceable from source artifact to row label to pulse verdict. If that chain
breaks, the result remains local diagnostic material rather than promoted beta
evidence.
