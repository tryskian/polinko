<!-- @format -->

# Behaviour Backlog Snapshot (2026-05-08)

## Purpose

This note records the first export-backed pass on Polinko's non-OCR behaviour
lanes.

It exists to answer a simple question:

> Is there enough real transcript evidence to operationalize broader Polinko
> hypotheses beyond OCR?

## Method

- Source: ChatGPT export search index plus the existing behaviour/eval export
  indexes under `.local/eval_cases/`
- Tool: `python3 -m tools.build_behaviour_backlog_from_export`
- Output shape:
  - local-only JSON backlog
  - local-only Markdown backlog
  - ranked candidate families by hypothesis lane

This pass stays local at the raw-candidate level. The tracked note only records
the lane-level result.

## Snapshot

- export search conversations scanned: `129`
- indexed behaviour conversations already in the repo-local export surface: `71`

Lane counts from the first backlog pass:

- co-reasoning reliability: `18` candidate conversations / `14` conversation
  families
- operator burden shift: `1` candidate conversation / `1` family
- hallucination boundary: `33` candidate conversations / `24` families
- retrieval grounding: `47` candidate conversations / `40` families
- OCR confidence boundary: `15` candidate conversations / `10` families

## Read

The repo does have materially more to evaluate than the current OCR lane.

The strongest next non-OCR promotion target is co-reasoning reliability:

- it maps directly to an existing project hypothesis
- it has enough export-backed candidate families to support real case curation
- it is broader than OCR while still staying close to Polinko's collaboration
  claim

Operator burden remains important, but the first mining pass only surfaced one
clear candidate family. That means the hypothesis is still real, but the export
cue surface is thinner and needs either:

- manual seeding
- stronger lane-specific cues
- or a more targeted miner pass later

Retrieval grounding and hallucination boundary already have stronger existing
eval surfaces in the repo, so the new backlog matters less as a first promotion
target there.

## Outcome

- confirmed: Polinko has a real multi-lane export-backed evidence surface
- confirmed: OCR is not the only mature or mineable lane
- next promotion target: co-reasoning reliability
- deferred: operator-burden operationalization until better mining cues or
  manual seed cases are added
