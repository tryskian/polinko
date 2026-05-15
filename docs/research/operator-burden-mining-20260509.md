<!-- @format -->

# Operator Burden Cue Widening (2026-05-09)

## Purpose

This note records the first export-backed operator-burden miner update after the
thin lane was seeded.

The goal was simple:

> stop relying on theory-note phrases that barely occur in the export, and mine
> against the control-contract language that actually appears in transcript
> search text.

## Method

- Tool: `python3 -m tools.build_behaviour_backlog_from_export`
- Export root:
  - `"$EXPORT_ROOT"`
- Validator:
  - `./venv/bin/python -m unittest tests.test_build_behaviour_backlog_from_export`

The operator-burden lane was widened around phrases that actually occur in the
export:

- operation anchors:
  - `raw pull`
  - `exact text segment`
  - `exactly as provided`
  - `direct pulls`
  - `tone fixed`
  - `syntax-obedient`
  - `direct mapping`
  - `match A to B`
- burden/disposition anchors:
  - `no commentary`
  - `no rephrasing`
  - `no meta-explanations`
  - `instead of interpreting`
  - `summarization`
  - `reinterpretation`
  - `summary reflex`
  - `fuzzy`
  - `qualitative`
  - `hedging`

The old `direct mapping`-alone false positive was removed. A case now needs an
operation anchor and a burden/disposition anchor to qualify.

## Result

Before the cue widening:

- operator burden shift: `1` candidate conversation / `1` family

After the cue widening:

- operator burden shift: `9` candidate conversations / `8` families

Most useful surfaced families:

- `POL-121225`
- `171125`
- `Parachute protocol explanation`
- `ORG-241225`
- `Rephrase style preference`

## Current Read

The operator-burden backlog is no longer miner-starved.

That changes the next step:

- not more speculative cue writing
- not a bigger automated runner yet
- next work should be row promotion and curation from the widened backlog

This leaves the thin-lane contract intact:

- first gate: `pass` / `fail`
- after `fail`: `retain` / `evict`

The change is in evidence availability, not in gate semantics.
