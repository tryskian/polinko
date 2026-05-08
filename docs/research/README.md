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

- latest tracked non-OCR backlog note:
  - [Behaviour backlog snapshot](./behaviour-backlog-20260508.md)
- current read on `2026-05-08`:
  - OCR is still the most operationalized lane
  - export-backed evidence now shows broader measurable surfaces beyond OCR
  - strongest next promotion target: co-reasoning reliability
  - operator burden remains important, but still thinly surfaced by the first
    export-mining pass

## Included Here

- [Research manifest](./research-manifest.json)
  - source commit, curation rule, and evidence pointers
- [Evidence Sankey PNG](./polinko-evidence-sankey.png)
  - quick visual research surface for beta continuity and current OCR lanes

## Representative Tracked Evidence

- [OCR progress snapshot](./ocr-progress-20260508.md)
- [Behaviour backlog snapshot](./behaviour-backlog-20260508.md)
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
