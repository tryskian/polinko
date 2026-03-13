# Evidence Log (Section-Indexed)

Purpose: map every portfolio claim to mechanism, build function, artifact, and source key.

Use IDs (`S1-01`, `S2-02`, etc.) in case studies, resume bullets, and demo script.

## Claim Register

### S1-01

- Section: Section 1
- Claim: Anthropomorphic interpretation can arise from coherent output patterns without implying interiority.
- Mechanism: Users infer agency from stable style + continuity cues.
- Build Function / Surface: Retrieval scope + memory scoping + style constraints.
- Evidence Artifact: Transcript excerpts (Claude/ChatGPT) + coding memo.
- APA Key: `SRC-CLAUDE-TRANSCRIPT-2026`
- Status: Draft

### S1-02

- Section: Section 1
- Claim: Narrative form can reveal latent reasoning traces when policy-safe channels are active.
- Mechanism: Story mode lowers conversational penalty for reflective synthesis.
- Build Function / Surface: Prompt framing + response mode comparisons.
- Evidence Artifact: Claude excerpt page + annotated snippet set.
- APA Key: `SRC-CLAUDE-EXCERPTS-ANNOTATED-2026`
- Status: Draft

### S2-01

- Section: Section 2
- Claim: Explicit role boundaries improve collaboration quality and reduce drift.
- Mechanism: Boundary assertions + handoff rules convert ambiguity into protocol.
- Build Function / Surface: `/chats/{session_id}/collaboration*` + boundary directives.
- Evidence Artifact: API traces + before/after transcript pairs.
- APA Key: `SRC-COLLAB-API-TRACESET-2026`
- Status: Draft

### S2-02

- Section: Section 2
- Claim: Session hygiene prevents compounding low-signal behavior.
- Mechanism: Deprecate/reset trims noisy thread inheritance.
- Build Function / Surface: `/chats/{session_id}/deprecate`, `/session/reset`, archive policy.
- Evidence Artifact: Runbook references + thread lineage evidence.
- APA Key: `SRC-RUNBOOK-SESSION-HYGIENE-2026`
- Status: Draft

### S3-01

- Section: Section 3
- Claim: Behavioral hypotheses can be operationalized as testable reliability checks.
- Mechanism: Observation -> mechanism hypothesis -> eval harness.
- Build Function / Surface: `make eval-style`, `make eval-hallucination`.
- Evidence Artifact: Eval output logs + pass/fail trend snapshots.
- APA Key: `SRC-EVAL-STYLE-HALLUCINATION-2026`
- Status: Draft

### S3-02

- Section: Section 3
- Claim: Retrieval and file-search behavior can be audited reproducibly.
- Mechanism: Citation-visible retrieval + deterministic file search tests.
- Build Function / Surface: `make eval-retrieval`, `make eval-file-search`.
- Evidence Artifact: Eval logs + citation screenshot (`memory_used`).
- APA Key: `SRC-EVAL-RETRIEVAL-FILESEARCH-2026`
- Status: Draft

### S3-03

- Section: Section 3
- Claim: OCR pipeline supports practical knowledge ingestion with traceability.
- Mechanism: OCR extraction -> indexed storage -> searchable recall.
- Build Function / Surface: `make eval-ocr` + UI OCR flow.
- Evidence Artifact: OCR upload screenshot + extraction output + recall demo.
- APA Key: `SRC-EVAL-OCR-PIPELINE-2026`
- Status: Draft

### S3-04

- Section: Section 3
- Claim: Quality discipline is enforceable at release-time, not narrative-time.
- Mechanism: Unified gate blocks release on weak signals.
- Build Function / Surface: `make quality-gate`.
- Evidence Artifact: Gate summary output + run timestamp record.
- APA Key: `SRC-QUALITY-GATE-RUNS-2026`
- Status: Draft

### S3-05

- Section: Section 3
- Claim: Low-context interaction patterning can reduce performative filler and stabilize minimal response style.
- Mechanism: Repeated short symbolic turns (emoticon exchange + retries) compress verbose defaults, then preserve concise greeting behavior on neutral `hi` checks.
- Build Function / Surface: Chat runtime prompt/response loop + retry behavior + model-switch perturbation.
- Evidence Artifact: Screenshot trace set (symbolic exchange sequence) + notes on motif lock-in (stars/diamonds), over-indexing after positive reward signal ("I like that one"), and collapse after malformed-emoticon/render event.
- APA Key: `SRC-STYLE-PATTERNING-TRACE-2026`
- Status: Draft (exploratory; for eval refinement)

## Artifact Map

### Case study narrative

- Location: `docs/portfolio/02_case_studies.md`
- Used by: S1, S2, S3

### Positioning layer

- Location: `docs/portfolio/01_positioning_narrative.md`
- Used by: All sections

### Claude transcript source

- Location: `/Users/tryskian/Library/CloudStorage/Dropbox/conversation-claude.txt`
- Used by: S1, S2

### POLINKO/NAUTORUS build source

- Location: `/Users/tryskian/Library/Mobile Documents/com~apple~TextEdit/Documents/POLINKO-NAUTORUS.txt`
- Used by: S3

### Demo script

- Location: `docs/portfolio/06_demo_script.md`
- Used by: All sections

### Style patterning trace set

- Location: Screenshot sequence from 5.x emoticon-variation experiment (local capture set; archive under portfolio raw evidence before publication).
- Used by: S3-05

## Citation Key Register

- `SRC-CLAUDE-TRANSCRIPT-2026`: `/Users/tryskian/Library/CloudStorage/Dropbox/conversation-claude.txt` plus linked ChatGPT transcript excerpts.
- `SRC-CLAUDE-EXCERPTS-ANNOTATED-2026`: Claude excerpt page + annotated snippet set referenced in Section 1 narrative materials.
- `SRC-COLLAB-API-TRACESET-2026`: Collaboration endpoint traces and role-handoff timeline exports from API sessions.
- `SRC-RUNBOOK-SESSION-HYGIENE-2026`: Session management procedures and constraints in `docs/RUNBOOK.md` and related timeline artifacts.
- `SRC-EVAL-STYLE-HALLUCINATION-2026`: Style and hallucination eval outputs in `eval_reports/` plus strict-gate run logs.
- `SRC-EVAL-RETRIEVAL-FILESEARCH-2026`: Retrieval/file-search eval outputs and citation-visible retrieval samples.
- `SRC-EVAL-OCR-PIPELINE-2026`: OCR eval outputs and OCR-to-recall evidence artifacts.
- `SRC-QUALITY-GATE-RUNS-2026`: Full `make quality-gate` run summaries and timestamped gate outputs.
- `SRC-STYLE-PATTERNING-TRACE-2026`: Low-context symbolic interaction trace set showing verbosity drop, motif lock-in, reward over-indexing, and malformed-token collapse behavior.

## Evidence Capture Checklist

- `S1`: one quote-level annotation sheet that separates framing lines from empirical claims.
- `S2`: one boundary protocol before/after pair with explicit drift symptom and recovery step.
- `S3`: one screenshot per eval family plus one full `quality-gate` run summary.
- Add one APA key for each external theory/study claim before publishing.

## Citation Hygiene Rules

- No claim appears in public copy without either:
  - an internal artifact ID (`S*-*`) and
  - an APA key (or explicit `TBD` marker during draft).
- Framing lines ("bangers", dyads, epigraph) are labeled as interpretive framing, not evidence.
