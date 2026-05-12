<!-- @format -->

# Research Surface

This folder is the compact research surface for reviewers who want the current
OCR state, the broader hypothesis/evidence picture, one machine-readable
manifest, and direct links into tracked eval evidence.

It is intentionally curated. Polinko keeps local operational artefacts under
`.local/`; this folder only promotes a small tracked subset that is stable
enough to read in public.

## Current OCR Snapshot

- latest tracked progress note:
  - [OCR progress snapshot](./ocr-progress-20260508.md)
- current OCR read on `2026-05-08`:
  - growth stability: `25/25` stable, `0` flaky
  - fail-history cohort: `0` active cases
  - focus stability: `16/16` stable
  - runtime OCR follow-up: parked
  - remaining signal: low-pressure exploratory variability and a case-design-only
    watchlist

## Current Non-OCR Read

- latest tracked non-OCR notes:
  - [Co-reasoning signal shape](./co-reasoning-signal-shape-20260512.md)
  - [Response-behaviour signal shape](./response-behaviour-signal-shape-20260512.md)
  - [Hallucination-boundary signal shape](./hallucination-boundary-signal-shape-20260512.md)
  - [Retrieval grounding signal shape](./retrieval-grounding-signal-shape-20260512.md)
  - [Operator burden signal shape](./operator-burden-signal-shape-20260512.md)
  - [Hallucination-boundary promotion](./hallucination-boundary-promotion-20260512.md)
  - [Beta 2.2 snapshot](./beta-2-2-20260508.md)
  - [Beta 2.2 stability soak](./beta-2-2-stability-soak-20260509.md)
  - [Uncertainty-boundary stability kernel](./uncertainty-boundary-stability-20260509.md)
  - [Co-reasoning promotion snapshot](./co-reasoning-promotion-20260508.md)
  - [Behaviour backlog snapshot](./behaviour-backlog-20260508.md)
  - [Operator burden row promotion](./operator-burden-promotion-20260509.md)
  - [Operator burden mining update](./operator-burden-mining-20260509.md)
  - [Operator burden seed](./operator-burden-seed-20260509.md)
- current read on `2026-05-12`:
  - current serious method beta is `Beta 2.2`
  - OCR remains one mature method lane
  - co-reasoning is now the first promoted non-OCR lane
  - tracked style stress surface now closes `14/14` in the latest tracked snapshot
  - one-hour deterministic beta soak now closes at `19/21` pass cycles
  - former dominant style pressure did not recur in the broad gate
  - the uncertainty-boundary stability kernel has now closed cleanly with:
    - resumed soak total: `3961s`
    - `21/21` pass cycles
    - `0` fail cycles
    - `0` recurring failure signals
  - tracked hallucination-boundary coverage is now wider and still green:
    - latest tracked snapshot: `9/9` pass
    - tracked case count: `9`
    - new distinct seams: archive-lore and archive-discipline fabrication
    - current signal-shape surface is now explicit
  - retrieval grounding now has fresh tracked snapshots across both visible branches:
    - retrieval recall: `12/12` pass
    - file search: `5/5` pass
  - response behaviour now has a fresh current tracked snapshot:
    - latest tracked snapshot: `7/7` pass
    - current signal-shape surface is now explicit
  - broad-gate pressure is no longer concentrated in the uncertainty contracts
  - current broad gate is holding across style, uncertainty, co-reasoning, and response behaviour
  - operator burden now has a seeded thin-lane row surface:
    - `4` pass rows
    - `2` retained fail rows
    - `1` evicted fail row
    - widened export-backed backlog: `9` conversations / `8` families
    - current top backlog slice is duplicate-heavy and does not presently earn
      more distinct row promotion

## Included Here

- [Research manifest](./research-manifest.json)
  - source commit, curation rule, and evidence pointers
- [Evidence Sankey PNG](./polinko-evidence-sankey.png)
  - quick visual research surface for beta continuity and current OCR lanes

## Representative Tracked Evidence

- [Hallucination-boundary promotion](./hallucination-boundary-promotion-20260512.md)
- [Hallucination-boundary signal shape](./hallucination-boundary-signal-shape-20260512.md)
- [Response-behaviour signal shape](./response-behaviour-signal-shape-20260512.md)
- [Co-reasoning signal shape](./co-reasoning-signal-shape-20260512.md)
- [Retrieval grounding signal shape](./retrieval-grounding-signal-shape-20260512.md)
- [Operator burden signal shape](./operator-burden-signal-shape-20260512.md)
- [Beta 2.2 snapshot](./beta-2-2-20260508.md)
- [Beta 2.2 stability soak](./beta-2-2-stability-soak-20260509.md)
- [Uncertainty-boundary stability kernel](./uncertainty-boundary-stability-20260509.md)
- [OCR progress snapshot](./ocr-progress-20260508.md)
- [Co-reasoning promotion snapshot](./co-reasoning-promotion-20260508.md)
- [Behaviour backlog snapshot](./behaviour-backlog-20260508.md)
- [Operator burden row promotion](./operator-burden-promotion-20260509.md)
- [Operator burden mining update](./operator-burden-mining-20260509.md)
- [Operator burden seed](./operator-burden-seed-20260509.md)
- [Prior OCR progress snapshot](./ocr-progress-20260501.md)
- [OCR representative case](./ocr-representative-case.md)
- [OCR binary eval snapshot](../eval/beta_2_0/ocr-20260328-184147.json)
- [OCR safety eval snapshot](./ocr-safety-20260425.md)
- [Response behaviour eval snapshot](./response-behaviour-20260425.md)
- [Response behaviour tracked snapshot](../eval/beta_2_0/response-behaviour-20260512-195350.json)
- [Hallucination eval snapshot](../eval/beta_2_0/hallucination-20260512-191438.json)
- [Retrieval eval snapshot](../eval/beta_2_0/retrieval-20260512-190149.json)
- [File-search eval snapshot](../eval/beta_2_0/file-search-20260512-190149.json)
- [Architecture diagram](../runtime/architecture.svg)
- [Public diagrams lane](../public/DIAGRAMS.md)

## Reading Rule

Use this folder when you need a fast research surface. Use
[docs/eval/README.md](../eval/README.md) and
[docs/public/README.md](../public/README.md) when you need the broader research
and evidence context.
