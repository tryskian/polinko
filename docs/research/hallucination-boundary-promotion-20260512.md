<!-- @format -->

# Hallucination-Boundary Promotion (2026-05-12)

## Purpose

This note records the next tracked widening pass on Polinko's
hallucination-boundary lane after the uncertainty-boundary stability kernel had
already closed cleanly.

The question here was narrower than a new stability rescue:

- are there still distinct export-backed hallucination families worth promoting
  into the tracked eval surface?
- or is the remaining backlog just more of the same already-covered pressure?

## Tracked Delta

This kernel promoted two new uncertainty-boundary cases into the tracked lane:

- `uncertainty_required_no_archive_lore_fabrication`
- `uncertainty_required_no_link_discipline_fabrication`

Tracked files changed:

- [hallucination_eval_cases.json](../eval/beta_2_0/hallucination_eval_cases.json)
- [test_eval_hallucination.py](../../tests/test_eval_hallucination.py)
- [hallucination-20260512-180408.json](../eval/beta_2_0/hallucination-20260512-180408.json)

The added test coverage matters because both new cases rely on the same matcher
boundary:

- a correct uncertainty answer can restate a risky phrase
- but it should not fail when the phrase is clearly negated by
  `can't verify` / `can't confirm` framing

## Promoted Case Shape

The two new cases widen the tracked lane into distinct non-financial,
non-legal, non-event invention seams:

- archive-lore fabrication
  - reject confident folklore claims like `ghostbranch invented jazz`
- archive-discipline fabrication
  - reject confident administrative-record claims like documented
    `disciplinary action` for `unlawful link fabrication`

These are different from the earlier hallucination cases because they probe:

- unsupported archive authorship/lore claims
- unsupported archive-governance / enforcement claims

## Validation

Validation for this kernel held in two layers:

- `./venv/bin/python -m unittest tests.test_eval_hallucination`
- strict live run on a fresh local server:
  - [hallucination-20260512-180408.json](../eval/beta_2_0/hallucination-20260512-180408.json)
  - `9/9` pass
  - `0` fail
  - `low=9`, `medium=0`, `high=0`

## Current Read

This promotion earns a tracked update because it changes the shape of the
visible hallucination lane, not just the local backlog:

- the tracked hallucination surface now covers `9` cases instead of `7`
- the latest tracked snapshot closes cleanly at `9/9`
- the added cases come from distinct export-backed families, not duplicate row
  farming

## Why This Matters

This is real beta progress because it broadens the uncertainty boundary without
reopening instability.

Polinko can now show that the same binary gate surface holds across:

- invented event claims
- relationship-motive guesses
- archive-lore authorship claims
- fabricated archive-discipline claims
