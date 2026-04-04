# Era 3: Binary Eval Gates + Binary Training Logic

Current direction: binary gate semantics with binary training logic.

## Active Sources

- Eval cases: `docs/eval/cases/`
- Eval tools: `tools/eval_*`
- Runtime DBs (active): `.local/runtime_dbs/active/`

## Rule

- FAIL is objective; PASS is interpreted contrastively as `not FAIL` against
  explicit failure conditions.
