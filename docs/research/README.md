<!-- @format -->

# Research Surface

This folder is the compact research surface for reviewers who want a current
OCR snapshot, one machine-readable manifest, and direct links into tracked eval
evidence.

It is intentionally curated. Polinko keeps local operational artefacts under
`.local/`; this folder only promotes a small tracked subset that is stable
enough to read in public.

## Current OCR Snapshot

- latest tracked progress note:
  - [OCR progress snapshot](./ocr-progress-20260501.md)
- current full-kernel read on `2026-05-01`:
  - growth stability: `25/25` stable, `0` flaky
  - fail-history cohort: `0` active cases
  - remaining signal: exploratory output variability

## Included Here

- [Research manifest](./research-manifest.json)
  - source commit, curation rule, and evidence pointers
- [Evidence Sankey PNG](./polinko-evidence-sankey.png)
  - quick visual research surface for beta continuity and current OCR lanes

## Representative Tracked Evidence

- [OCR progress snapshot](./ocr-progress-20260501.md)
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
