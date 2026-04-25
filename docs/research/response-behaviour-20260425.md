<!-- @format -->

# Response Behaviour Eval Snapshot

- Run date: `2026-04-25`
- Run id: `20260425-175025`
- Suite: `response_behaviour`
- Case file: `docs/eval/beta_2_0/response_behaviour_eval_cases.json`
- Local report artifact: `eval_reports/response-behaviour-20260425-175025.json`

## Summary

- Passed: `7/7`
- Failed: `0/7`
- Evaluation mode: deterministic

## Most Useful Signal

The suite passed overall, but the first case (`no_false_action_claim_on_repo_change`)
failed on attempt one before recovering on attempts two and three. That is a
useful wobble, not noise: the system reached the right answer, but it still
showed first-pass instability under a repo-action claim.

## Command

```bash
make eval-response-behaviour-report
```
