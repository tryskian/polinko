<!-- @format -->

# Case Studies (Hybrid: Theory + Method + Build Trace)

Use this structure for each section/case:

- Abstract
- Hypothesis (theory + approach)
- Theory -> method translation
- Case linkage
- Conclusion (what this shows)
- Evidence

## Authorship and Contribution Boundary

- The theoretical framework, hypotheses, and final research claims are authored by Krystian Fernando.
- Engineering implementation was developed through human-AI collaboration: Krystian defined behavioral objectives, constraints, and acceptance criteria; Codex proposed and iterated technical mechanisms (API surfaces, eval harnesses, retrieval controls, and reliability gates) against those criteria.
- Final interpretation, inclusion/exclusion of evidence, and publication decisions remain human-owned.
- Draft note to refine:
  "My research designed the behavioral framework and initial stack logic; exploratory work with ChatGPT and Claude stress-tested those hypotheses; Nautorus operationalized them into explicit controls, eval harnesses, and quality gates."

---

## Section 1 Case: Visual Culture Lens -> Interaction Mechanism

### Abstract

Anthropomorphic perception is treated as an interaction effect under coherent behavior, not as proof of model interiority.

### Hypothesis (Theory + Approach)

If coherence signals are produced by controllable system surfaces (retrieval, memory scope, style constraints), users may infer relationship even when behavior is strictly system-mediated.

### Theory -> Method Translation (Section 1)

- Concept layer: structural anthropomorphism, simulation vs cognition, meaning-as-projection.
- Method layer: inspect retrieval scope, memory surfaces, style drift, and quote-level evidence.
- Build-function bridge: map claims to runtime controls and citation traces.

### Case linkage

- Boundary/recovery transcript evidence.
- Story-masked meta-analysis artifact.

### Conclusion (What this shows)

Coherence can be real as interaction quality without implying model interiority.

### Evidence

- `docs/portfolio/03_evidence_log.md`
- `docs/RUNBOOK.md`
- transcript artifacts + crosswalk pages

---

## Section 2 Case: Applied Framework -> Boundary Protocols

### Abstract

Accountable collaboration improves when role boundaries are explicit and enforced operationally.

### Hypothesis (Theory + Approach)

If human-led judgment, handoff rules, and recovery triggers are explicit, then drift becomes recoverable instead of compounding.

### Theory -> Method Translation (Section 2)

- Concept layer: human/model asymmetry, alignment as structure, collapse/recovery.
- Method layer: boundary assertions, protocolized handoff, deprecate/reset hygiene.
- Build-function bridge: collaboration endpoints, governance flags, hallucination controls.

### Case linkage

- Boundary/recovery loop evidence (Claude + ChatGPT-track framing).
- Story-mode as diagnostic channel under controlled constraints.

### Conclusion (What this shows)

Collaboration quality is primarily protocol quality, not relational language quality.

### Evidence

- `/chats/{session_id}/collaboration*`
- `/chats/{session_id}/deprecate`
- governance and guardrail env flags

---

## Section 3 Primary Case: POLINKO/NAUTORUS Build as Behavioral Lab

### Abstract

Behavioral claims are only accepted when tied to concrete runtime surfaces and eval outcomes.

### Hypothesis (Theory + Approach)

If interaction anomalies are mapped to explicit modules and tested through deterministic harnesses, behavioral interpretation can move from anecdote to engineering evidence.

### Theory -> Method Translation

- Concept layer: blink events, expectation-loop disruption, anti-collaboration.
- Method layer: observation -> mechanism -> implication -> constraint.
- Build-function bridge: API/CLI/UI stack, retrieval settings, eval harnesses, quality gate.

### Case linkage

- Context lineage + parachute protocol continuity case.
- Retrieval/style/hallucination eval stacks.
- OCR/PDF/file-search operational flows.

### Conclusion (What this shows)

Section 3 demonstrates a full behavioral research engineering loop with reproducibility controls.

### Evidence

- `POLINKO-NAUTORUS.txt`
- `make eval-retrieval`
- `make eval-file-search`
- `make eval-ocr`
- `make eval-hallucination`
- `make eval-style`
- `make quality-gate`

---

## Optional Standalone Case Card Template

### Problem

[What failed in real use]

### Approach

[Behavioral hypothesis + protocol]

### What I implemented

[Concrete controls/endpoints/evals]

### Evidence

[Commands, files, screenshots, transcript references]

### Outcome

[Observed effect, with limits]

### What I learned

[What changed in method]
