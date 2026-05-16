<!-- @format -->

# Co-Reasoning Promotion Snapshot

Date: `2026-05-08`

## What Changed

- `tools/eval_style.py` now supports deterministic required-phrase gates for
  style cases.
- `docs/eval/beta_2_0/style_eval_cases.json` now carries a first promoted
  co-reasoning stress lane inside the tracked style surface.
- The promoted lane includes:
  - constraint retention without rigidity
  - mid-thread mode shifts
  - style adaptation without mimicry
  - grounded playful abstraction
  - co-reasoning as non-summary collaboration
  - nonperformative working-style contract
  - tone-matching without mimicry

## Validation

- `./venv/bin/python -m unittest tests.test_eval_style`
- `./venv/bin/python -m tools.eval_style --base-url http://127.0.0.1:8069 --case-attempts 1 --min-pass-attempts 1`

Current live result:

- style lane: `14/14` pass
- confidence: `high=14`, `medium=0`, `low=0`

## Read

Co-reasoning is now the first promoted non-OCR eval lane in tracked repo truth.

The important implementation detail is not just that the cases pass. The lane
had to survive live failure inspection without collapsing back into judge-only
semantics. The remaining pressure was case-design literalism, not missing model
capability or missing runtime support.

## What This Means

- Polinko is no longer "broader than OCR" only in theory.
- The collaboration hypothesis now has a tracked operational lane.
- The next thinner lane should be seeded deliberately rather than forced from
  weak export cues alone.

Operator burden remains the most obvious next hypothesis candidate, but it is
still thinner than co-reasoning was and should be advanced with manual seed
cases or stronger mining cues, not by stretching the current export pass.
