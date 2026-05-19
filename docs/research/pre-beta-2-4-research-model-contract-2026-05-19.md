<!-- @format -->

# Pre-Beta 2.4 Research Model Contract

Date: `2026-05-19`

Status: `staged`

## Boundary

`Beta 2.3` is the frozen baseline. Its eval snapshot lives under
`docs/eval/beta_2_3/` and remains the source for the current method read.

`pre-Beta 2.4` names the next research-model contract before new evidence is
cut. The first evidence folder is cut when real evidence exists.

The fail-pressure pulse hypothesis is not being carried forward as the next
method. It remains historical negative evidence because the pulse shape did not
work properly as a stable research surface.

The active question is whether Polinko can move from lane snapshots to
source-first research claims while preserving row evidence and the manual eval
workbench as source material.

## Contract

- OCR remains case-level `pass` / `fail` under broader generalization pressure.
- OCR post-fail handling can still use `retain` / `evict` case governance.
- Non-OCR lanes stay source-first:
  - manual eval judgment
  - chat workbench evidence
  - row-local or case-local `pass` / `fail` where binary judgment is earned
  - qualitative notes where the lane is still thin
- Pulse-level verdicts are not canonical rollups for pre-Beta 2.4.
- Any promotion claim must stay traceable to source artifacts, row/case
  judgment, and repeated lane signal.

## Evidence Stack

The research model has four layers:

1. Source artifacts from active workbench and eval surfaces.
2. Row-level or case-level judgments that preserve source evidence.
3. Lane-level summaries with visible counts, examples, and exclusions.
4. Promotion claim only after repeated lane signal stabilizes.

Canonical source surfaces include:

- `POST /chat`
- `/chats/*`
- `.local/runtime_dbs/active/manual_evals.db`
- `.local/runtime_dbs/active/history.db`
- tracked eval reports and research notes under `docs/eval/` and
  `docs/research/`

The staged contract sits above these sources and keeps them canonical. It does
not replace the workbench, flatten manual evals, or convert thin lanes into
pulse verdicts.

## First Kernel Shape

The first pre-Beta 2.4 kernel should be small, predetermined, and auditable.

It should record:

- source artifacts used
- row or case count
- manual-eval or chat-workbench evidence
- explicit exclusions with narrow reasons
- lane summary before any method claim

A new `docs/eval/beta_2_4/` evidence folder should be cut when real evidence
exists.

## Decision Rule

A pre-Beta 2.4 kernel can inform the next beta only when the evidence stack
stays traceable from source artifact to row/case judgment to lane summary. If
that chain breaks, the result remains local diagnostic material rather than
promoted beta evidence.
