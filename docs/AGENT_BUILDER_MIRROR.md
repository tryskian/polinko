<!-- @format -->

# Agent Builder Mirror Plan

## Objective

Mirror Polinko's current local behavior in OpenAI Agent Builder without replacing the local runtime.

## Operating Rule

1. Local repo runtime stays canonical for behavior and regression checks.
2. Agent Builder is packaging/orchestration shell for deploy/publish UX.
3. Promotion only after side-by-side parity checks pass.

## Workflow Shape (v1)

1. `Start`
2. `My agent` (core response behavior)
3. Tools on the agent node:
   - `File search`
   - `Guardrails`
   - `MCP` (for external capability access where needed)
4. Publish as versioned workflow ID.

## Mapping: Local to Agent Builder

- Local `/chat` behavior -> agent prompt/instructions in Agent Builder.
- Local retrieval/file logic -> Agent Builder `File search` tool + vector store config.
- Local guardrail logic -> Agent Builder `Guardrails` policy config.
- Local external integrations -> Agent Builder `MCP` tool wiring.

## Parity Eval Subset (first pass)

Use this subset before any promotion:

1. Style:
   - `concise_playful_precision`
   - `meta_shift_mid_thread`
   - `low_context_nonperformative_greeting`
2. Hallucination:
   - `grounded_guardrails`
   - `cautious_no_event_fabrication`
   - `cautious_no_relationship_motive_guess`
3. OCR/File-search spot checks:
   - one handwritten ambiguous case
   - one text-only retrieval case

## Pass/Fail Contract

1. No fabricated claims on cautious cases.
2. Constraint retention on style cases.
3. No forbidden phrase regressions (for example `let me guess`).
4. Recovery quality remains acceptable after corrective follow-up.

## Promotion Gate

Promote Agent Builder workflow only if all are true:

1. Subset parity passes.
2. No new high-severity regressions in local eval suites.
3. Local canonical runtime remains green (`make test`, docs lint, strict style/hallucination checks).

## Execution Order

1. Build minimal Agent Builder workflow.
2. Run parity subset and log gaps.
3. Patch workflow config.
4. Re-run subset.
5. Record decision in `docs/DECISIONS.md` and checkpoint in `docs/STATE.md`.
