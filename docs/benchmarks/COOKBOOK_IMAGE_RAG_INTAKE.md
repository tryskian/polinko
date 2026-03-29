# Cookbook Intake: Image Understanding with RAG

## Source

- OpenAI cookbook example:
  `https://developers.openai.com/cookbook/examples/multimodal/image_understanding_with_rag`

## Cookbook Queue Context

Prioritized now:

1. Doing RAG on PDFs using File Search in the Responses API
2. Structured Outputs
3. Image Understanding with RAG (this intake)
4. Data Extraction and Transformation in ELT Workflows (GPT-4o OCR alternative)
5. Exploring Model Graders for Reinforcement Fine-Tuning
6. Custom LLM-as-Judge hallucination checks (Braintrust) [P1]
7. Multimodal retrieval A/B with CLIP embeddings [P2]

Deferred include-later track:

1. Prompt Caching 101/201
2. Realtime eval guide
3. Realtime out-of-band transcription
4. RAG with graph DB
5. Search reranking with cross-encoders

## Objective

Adopt the cookbook pattern as a bounded Polinko kernel to improve multimodal
retrieval quality across handwriting, typed text, and illustration-heavy images,
without introducing model-training drift.

## Problem Fit (Polinko)

- Current strength: OCR lanes are stable and deterministic.
- Current gap: image context beyond plain OCR text is underused in retrieval.
- Target: better answer quality when meaning depends on visual layout, symbols,
  sketches, or mixed text-and-image cues.

## Scope (This Intake Only)

1. Keep the existing binary eval contract (`pass`/`fail`) unchanged.
2. Keep OCR extraction as the primary baseline path.
3. Add one multimodal RAG retrieval path as a feature-flagged adapter.
4. Evaluate both paths on the same fixed case set for parity and uplift.

## Out Of Scope

- No fine-tuning or weight updates.
- No UI rebuild.
- No changes to governance model beyond recording results in current docs.

## Minimal Integration Slice

1. Data contract
   - input: image (plus optional OCR text)
   - retrieval context: file-search hits + image-aware grounding payload
   - output: answer + cited support
2. Runtime contract
   - one adapter behind a feature flag:
     - `baseline`: OCR-first retrieval
     - `candidate`: image-understanding RAG retrieval
3. Eval contract
   - same cases and rubric for both arms
   - compare by lane:
     - handwriting
     - typed
     - illustration

## Acceptance Criteria

- No regression on typed lane versus current baseline.
- Measurable uplift on at least one of:
  - handwriting lane
  - illustration lane
- Deterministic validation still passes:
  - `make build-audit`
  - `make lint-docs`
  - `make test`
  - OCR lane eval commands in current runbook

## Risk Controls

- Keep one canonical prompt shape per arm to limit confounders.
- Keep case split fixed during comparison runs.
- Log all deltas as lane-level metrics, not anecdotal examples.
- Human go/no-go remains explicit before broad rollout.

## Execution Plan

1. Baseline lock
   - freeze current lane metrics from transcript-derived OCR cases
2. Candidate wiring
   - implement feature-flagged multimodal RAG adapter
3. A/B evaluation
   - run lane evals on matched inputs
4. Decision
   - keep / adjust / retire candidate path

## Success Signal

This intake is successful when the candidate path improves multimodal accuracy
on hard cases with no typed-lane regression and no increase in maintenance
overhead.
