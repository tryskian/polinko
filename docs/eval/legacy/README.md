# Legacy Eval Eras

This folder preserves historical eval eras so they remain referenceable without
polluting active runtime/eval wiring.

## Era Map

1. `eval gates + traditional training logic`
   - path: `docs/eval/legacy/1_eval_gates_traditional_training_logic/`
2. `binary eval gates + traditional training logic`
   - path: `docs/eval/legacy/2_binary_gates_traditional_training_logic/`
3. `binary eval gates + binary training logic` (current direction)
   - path: `docs/eval/legacy/3_binary_gates_binary_training_logic/`

## Notes

- Legacy artefacts are documentation/reference inputs only.
- Active runtime eval flow remains under:
  - `docs/eval/cases/`
  - `tools/eval_*`
  - `.local/runtime_dbs/active/`
