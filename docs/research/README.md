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
  - [Beta 2.2 snapshot](./beta-2-2-20260508.md)
  - [Co-reasoning promotion snapshot](./co-reasoning-promotion-20260508.md)
  - [Behaviour backlog snapshot](./behaviour-backlog-20260508.md)
  - [Operator burden row promotion](./operator-burden-promotion-20260509.md)
  - [Operator burden mining update](./operator-burden-mining-20260509.md)
  - [Operator burden seed](./operator-burden-seed-20260509.md)
- current read on `2026-05-09`:
  - current serious method beta is `Beta 2.2`
  - OCR remains one mature method lane
  - co-reasoning is now the first promoted non-OCR lane
  - tracked style stress surface currently passes `14/14` on the live pass
  - operator burden now has a seeded thin-lane row surface:
    - `3` pass rows
    - `2` retained fail rows
    - widened export-backed backlog: `9` conversations / `8` families

## Included Here

- [Research manifest](./research-manifest.json)
  - source commit, curation rule, and evidence pointers
- [Evidence Sankey PNG](./polinko-evidence-sankey.png)
  - quick visual research surface for beta continuity and current OCR lanes

## Representative Tracked Evidence

- [Beta 2.2 snapshot](./beta-2-2-20260508.md)
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
- [Hallucination eval snapshot](../eval/beta_2_0/hallucination-20260328-184216.json)
- [Architecture diagram](../runtime/architecture.svg)
- [Public diagrams lane](../public/DIAGRAMS.md)

## Reading Rule

Use this folder when you need a fast research surface. Use
[docs/eval/README.md](../eval/README.md) and
[docs/public/README.md](../public/README.md) when you need the broader research
and evidence context.
