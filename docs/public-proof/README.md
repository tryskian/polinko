<!-- @format -->

# Public Proof

This folder is the compact proof packet for reviewers who want one visual, one
machine-readable manifest, and direct links into tracked eval evidence.

It is intentionally curated. Polinko keeps local operational artefacts under
`.local/`; this folder only promotes a small tracked subset that is stable
enough to read in public.

## Included Here

- [Proof manifest](./proof-manifest.json)
  - source commit, curation rule, and evidence pointers
- [Evidence Sankey PNG](./polinko-evidence-sankey.png)
  - quick visual proof surface for beta continuity and current OCR lanes

## Representative Tracked Evidence

- [OCR binary eval snapshot](../eval/beta_2_0/ocr-20260328-184147.json)
- [Hallucination eval snapshot](../eval/beta_2_0/hallucination-20260328-184216.json)
- [Architecture diagram](../runtime/architecture.svg)
- [Public diagrams lane](../public/DIAGRAMS.md)

## Reading Rule

Use this folder when you need a fast proof packet. Use
[docs/eval/README.md](../eval/README.md) and
[docs/public/README.md](../public/README.md) when you need the broader research
and evidence context.
