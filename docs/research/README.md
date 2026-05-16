<!-- @format -->

# Research Surface

This folder is the compact research surface for reviewers who want the current
method read, one machine-readable manifest, and direct links into tracked eval
evidence.

It is intentionally curated. Polinko keeps local operational artefacts under
`.local/`; this folder only promotes a small tracked subset that is stable
enough to read in public.

## Current Read

- `Beta 2.3` is the current method beta:
  - release outcomes stay `pass` / `fail`
  - post-fail disposition stays `retain` / `evict`
  - OCR now moves into transcript-mined generalization pressure
- OCR is the mature green lane:
  - growth stability: `25/25` stable, `0` flaky
  - fail-history cohort: `0` active cases
  - current image set is stabilized
  - generalization pressure is next
- co-reasoning is the first promoted non-OCR lane:
  - tracked style pass: `14/14`
  - one-hour deterministic soak: `19/21` pass cycles
- the broad gate is holding across:
  - uncertainty-boundary stability: `21/21` pass cycles, `0` fail cycles
  - hallucination-boundary coverage: `9/9` pass across `9` tracked cases
- operationalized support lanes are holding:
  - retrieval grounding: `12/12` retrieval pass, `5/5` file-search pass
  - response-behaviour stability: `7/7` pass with one recovered first-pass
    wobble
- operator burden is the active thin lane:
  - `4` pass rows
  - `2` retained fail rows
  - `1` evicted fail row
  - widened backlog: `9` conversations / `8` families
- the current lane map is explicit:
  - it is a live research surface, not a closed or finished method claim

## Non-OCR Lane Inventory

- promoted:
  - co-reasoning reliability
- operationalized:
  - uncertainty-boundary and hallucination-boundary coverage
  - retrieval grounding
  - response-behaviour stability
- thin:
  - operator burden
- current promotion read:
  - no additional non-OCR lane currently meets promotion criteria

## Tracked Notes By Role

- method boundary:
  - [Beta 2.3 snapshot](./beta_2_3_2026-05-16.md)
  - [Beta 2.2 snapshot](./beta_2_2_2026-05-08.md)
  - [Beta 2.2 stability soak](./beta-2-2-stability-soak-2026-05-09.md)
  - [Uncertainty-boundary stability](./uncertainty-boundary-stability-2026-05-09.md)
- mature green lane:
  - [OCR progress snapshot](./ocr-progress-2026-05-08.md)
  - [OCR representative case](./ocr-representative-case.md)
- promoted non-OCR lane:
  - [Co-reasoning promotion snapshot](./co-reasoning-promotion-2026-05-08.md)
  - [Hallucination-boundary promotion](./hallucination-boundary-promotion-2026-05-12.md)
- operationalized support lanes:
  - [Retrieval grounding snapshot](./retrieval-grounding-2026-03-28.md)
  - [Response-behaviour stability snapshot](./response-behaviour-stability-2026-04-25.md)
  - [Eval evidence map](../eval/README.md)
- active thin lane:
  - [Operator burden seed](./operator-burden-seed-2026-05-09.md)
  - [Operator burden row promotion](./operator-burden-promotion-2026-05-09.md)
  - [Operator burden mining update](./operator-burden-mining-2026-05-09.md)
  - [Operator burden signal shape](./operator-burden-signal-shape-2026-05-12.md)
- backlog context:
  - [Behaviour backlog snapshot](./behaviour-backlog-2026-05-08.md)

## Included Here

- [Research manifest](./research-manifest.json)
  - source commit, curation rule, and evidence pointers
- [Evidence Sankey PNG](./polinko-evidence-sankey.png)
  - quick visual research surface for beta continuity and current OCR lanes

## Reading Rule

Use this folder when you need a fast research surface. Use
[docs/eval/README.md](../eval/README.md) and
[docs/public/README.md](../public/README.md) when you need the broader research
and evidence context.
