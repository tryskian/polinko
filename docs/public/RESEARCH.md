<!-- @format -->

# Research

Polinko is a human-led research programme for making AI behaviour legible
through failure-visible evaluation, source grounding, co-reasoning, and
inspectable evidence.

This is the parent research packet. It holds the current question, conclusions,
hypotheses, evidence structure, and active research lanes. Each hypothesis is
one research output within that broader surface.

## Research Question

> What changes when evaluation treats failure as the main signal instead of
> treating pass rate as the main story?

Polinko tests whether failure-visible evaluation can make AI behaviour legible
enough to improve the method without mistaking coherent output for reliable
behaviour.

## Latest Hypothesis

> Lean binary evaluation may improve both reasoning reliability and compute
> efficiency by reducing context clutter and correction churn.

This extends Polinko's earlier minimal-config and binary-eval work into an
energy and compute question. The same structural discipline that reduces drift
may also reduce token churn, failed reruns, overgeneration, and human correction
burden. Reliability, safety, and efficiency may be effects of the same mechanism
rather than separate optimisation tracks.

In this research packet, sustainability means the resource side of unnecessary
inference: extra tokens, retries, reruns, and overlong outputs create compute
work; compute work consumes energy; energy-intensive infrastructure creates
cooling demand; and cooling can require water depending on the system serving
the inference.

The first comparison should hold task shape and acceptance criteria steady
while measuring:

- token usage;
- retries before an accepted output;
- validation reruns;
- human correction burden;
- output length against accepted answer quality.

The hypothesis is staged for a paired comparison between lean binary structure
and instruction-heavy structure. It is a substantive research output grounded
in the work's existing reliability findings and a defined next experiment.

## Current Conclusions

At the current evidence boundary, the work supports these conclusions:

- Failure is a useful signal. Retained mismatches show where the method needs
  to learn, while evicted cases keep bad evidence from distorting the gate.
- Confidence follows evidence. Model behaviour becomes more reliable when it
  re-grounds in source material or the artefact being judged.
- Binary gates protect interpretation. `pass` / `fail`, followed by
  `retain` / `evict` when needed, keeps the operational decision visible before
  richer explanation begins.
- Co-reasoning can be evaluated as a behavioural lane. It is the first promoted
  non-OCR lane, supported by tracked style and soak evidence.
- Source-first traceability is the research method. Claims become promotable
  when source artefacts, row or case judgements, lane summaries, and repeated
  signal remain connected.

These are research conclusions at the evidence boundary Polinko has reached.
They remain open to extension, qualification, or revision through further
evidence.

## Current Research Read

- `Beta 2.3` is the frozen baseline for the next method beta.
- OCR is the mature green lane and now moves into broader generalisation
  pressure.
- Co-reasoning is the first promoted non-OCR lane.
- Uncertainty-boundary, hallucination-boundary, retrieval-grounding, and
  response-behaviour surfaces are operationalised.
- Operator burden is an active thin lane with real evidence and a deliberately
  narrow claim boundary.
- `pre-Beta 2.4` stages a source-first research-model contract in which row and
  case evidence remain visible before lane-level claims are promoted.

The tracked counts, exclusions, and source notes live in the
[Research Surface](../research/README.md) and [Evidence](EVIDENCE.md).

## Hypotheses, Evidence, and Conclusions

Polinko uses hypotheses as testable research claims. Their status records the
evidence they have earned:

- `staged` or `thin` hypotheses identify active research pressure;
- `operationalised` hypotheses have repeatable evaluation surfaces;
- `promoted` hypotheses have repeated signal strong enough to support a current
  research conclusion.

[Current Hypotheses](HYPOTHESIS.md) records those claims and their status.
[Evidence](EVIDENCE.md) records what supports, qualifies, or changes them.

## Evidence Structure

Polinko keeps the research chain inspectable:

1. Source artefacts from the runtime, evals, notebooks, databases, chats, and
   transcripts.
2. Row-level or case-level judgements with explicit exclusions.
3. Lane summaries that preserve counts, examples, and failure pressure.
4. Research conclusions promoted from repeated lane signal.

Source code and tests define the runtime contract. Eval docs and report schemas
define the evidence contract. Beta snapshots preserve the method as it changes.
Diagrams are research instruments, and curated notes connect findings back to
their source material.

## Reading Path

1. [Polinko in Brief](IN_BRIEF.md): the shortest current read.
2. [Method & Authorship](METHOD.md): research ownership and AI role.
3. [Current Hypotheses](HYPOTHESIS.md): claims and evidence status.
4. [Evidence](EVIDENCE.md): evidence rules and tracked proof.
5. [Research Surface](../research/README.md): current lanes and source notes.
6. [Diagrams](DIAGRAMS.md): visual research structures.
