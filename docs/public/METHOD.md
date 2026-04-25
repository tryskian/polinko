<!-- @format -->

# Method & Authorship

Polinko is a human-led research and engineering collaboration.

Use this note when you need the authorship boundary first: who owns the claims,
how AI is used, and what remains human-judgment work.

The research framework, hypotheses, judgement, evidence selection, and final
claims are authored by Krystian Fernando. AI systems are used as research and
engineering instruments inside that process, not as independent authors or
source authority.

## Tooling Disclosure

Polinko uses OpenAI Codex as a repo-local coding agent and engineering
collaborator for implementation, refactoring, validation, review, and
documentation maintenance. OpenAI Platform APIs are used where Polinko makes
model-backed calls for OCR, evals, retrieval, and runtime experiments.

These tools are part of the research-engineering workflow. They do not define
the research claims, interpret the evidence, or own publication decisions.

The supporting stack is intentionally inspectable:

| Layer | Tooling | Role |
| --- | --- | --- |
| Model collaboration | OpenAI Codex, OpenAI Platform APIs | Repo-local coding support plus model-backed OCR, eval, retrieval, and runtime calls. |
| Runtime surface | FastAPI | Local API surface for assistant, OCR/PDF ingest, retrieval, feedback, and eval workflows. |
| Evidence stores | SQLite | Local, queryable stores for runtime history, manual evals, vector memory, and evidence inspection. |
| System maps | Mermaid | Plain-text diagrams for pipelines, eval loops, and research structure. |
| Environment | Docker, devcontainers | Portable development and runtime environments. |
| Validation | Make, pytest, Ruff, mypy, markdownlint, GitHub Actions | Repeatable checks across code, docs, and CI. |
| Maintenance | Dependency update checks | Keeps dependency drift visible without turning maintenance into manual archaeology. |
| Inspection | Playwright, Jupyter | Browser-visible verification, visual capture, and local analysis. |

## Collaboration Model

Polinko moves from human research direction to technical implementation:

1. Krystian defines the behavioural objective, constraints, evidence boundary,
   and acceptance criteria.
2. AI collaborators support structured dialogue, synthesis, reframing, and
   stress-testing of ideas.
3. Codex translates approved objectives into technical mechanisms: API
   surfaces, eval harnesses, retrieval controls, reliability gates, docs, and
   validation workflows.
4. Krystian makes final decisions about interpretation, evidence inclusion,
   exclusion, and publication.

## What AI Does Here

AI assistance is method support:

- structured dialogue
- synthesis support
- reframing and stress-testing ideas
- implementation support
- organisation support in Notion and repository workflows

AI outputs are treated as artefacts within the research process. They can be
useful, inspectable, wrong, or rejected.

## Responsibility Boundary

- Concept formation remains human-owned.
- Judgment and selection remain human-owned.
- Final claims remain human-owned.
- AI assistance is cited as part of the method, not treated as source
  authority.

## Practical Rule

Polinko uses a transcript-first workflow so claims can be traced back to source
evidence before they enter public explanation, eval logic, or implementation.
