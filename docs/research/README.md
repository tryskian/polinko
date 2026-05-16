<!-- @format -->

# Research Surface

This folder is the compact research surface for reviewers who want the current
method read, one machine-readable manifest, and direct links into tracked eval
evidence.

It is intentionally curated. Polinko keeps local operational artefacts under
`.local/`; this folder only promotes a small tracked subset that is stable
enough to read in public.

## Current Read

- `Beta 2.2` is the current method beta:
  - release outcomes stay `pass` / `fail`
  - post-fail disposition stays `retain` / `evict`
  - the first gate proves contract correctness before richer interpretation
- OCR is the mature green lane:
  - growth stability: `25/25` stable, `0` flaky
  - fail-history cohort: `0` active cases
  - runtime OCR follow-up: parked
- co-reasoning is the first promoted non-OCR lane:
  - tracked style pass: `14/14`
  - one-hour deterministic soak: `19/21` pass cycles
- the broad gate is holding across:
  - uncertainty-boundary stability: `21/21` pass cycles, `0` fail cycles
  - hallucination-boundary coverage: `9/9` pass across `9` tracked cases
- operator burden is the active thin lane:
  - `4` pass rows
  - `2` retained fail rows
  - `1` evicted fail row
  - widened backlog: `9` conversations / `8` families

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
  - [Beta 2.2 snapshot](./beta_2_2_2026-05-08.md)
  - [Beta 2.2 stability soak](./beta-2-2-stability-soak-20260509.md)
  - [Uncertainty-boundary stability](./uncertainty-boundary-stability-20260509.md)
- mature green lane:
  - [OCR progress snapshot](./ocr-progress-20260508.md)
  - [OCR representative case](./ocr-representative-case.md)
- promoted non-OCR lane:
  - [Co-reasoning promotion snapshot](./co-reasoning-promotion-20260508.md)
  - [Hallucination-boundary promotion](./hallucination-boundary-promotion-20260512.md)
- operationalized support lanes:
  - [Response behaviour eval snapshot](./response-behaviour-20260425.md)
  - [Eval evidence map](../eval/README.md)
- active thin lane:
  - [Operator burden seed](./operator-burden-seed-20260509.md)
  - [Operator burden row promotion](./operator-burden-promotion-20260509.md)
  - [Operator burden mining update](./operator-burden-mining-20260509.md)
  - [Operator burden signal shape](./operator-burden-signal-shape-20260512.md)
- backlog context:
  - [Behaviour backlog snapshot](./behaviour-backlog-20260508.md)

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
