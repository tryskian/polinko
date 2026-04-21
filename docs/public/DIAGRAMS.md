<!-- @format -->

# Diagrams

This page collects repo-native diagrams and visual evidence pointers. Canonical
runtime and eval contracts remain in `docs/runtime/ARCHITECTURE.md` and
`docs/eval/README.md`.

Static SVG exports generated from this page:

- [Polinko Evidence Sankey (D3)](diagrams/polinko-evidence-sankey.svg)
- [Baseline LLM Product Pipeline](diagrams/baseline-llm-product-pipeline.svg)
- [Polinko Binary Eval Loop](diagrams/polinko-binary-eval-loop.svg)
- [Beta Evidence Map](diagrams/beta-evidence-map.svg)

## Polinko Evidence Sankey (D3)

![Polinko Evidence Sankey](diagrams/polinko-evidence-sankey.svg)

Static D3 Sankey generated from the real `/portfolio/sankey-data` payload. It
shows how Beta 1.0 manual evals flow through manual outcomes and signal
classes into the current OCR lane weighting surface.

## Baseline LLM Product Pipeline

![Baseline LLM Product Pipeline](diagrams/baseline-llm-product-pipeline.svg)

```mermaid
flowchart TD
  A["User input"] --> B["Input guardrails"]
  B --> C["Task / intent router"]
  C --> D["Context builder"]
  D --> E["Prompt + policy assembly"]
  E --> F["Model generation"]
  F --> G["Output guardrails"]
  G --> H["Final response"]

  H --> I["Telemetry / event log"]
  I --> J["Eval events"]
  I --> K["Feedback events"]
  J --> L["State / evidence tables"]
  K --> L
  L --> D
```

## Polinko Binary Eval Loop

![Polinko Binary Eval Loop](diagrams/polinko-binary-eval-loop.svg)

```mermaid
flowchart LR
  A["Source input"] --> B["Runtime output"]
  B --> C["Eval case"]
  C --> D{"Binary gate"}
  D -->|"PASS"| E["Lockset confidence"]
  D -->|"FAIL"| F["Failure signal"]
  F --> G["Manual notes + source evidence"]
  G --> H["Growth lane"]
  H --> C
  E --> I["Release stability signal"]
```

## Beta Evidence Map

![Beta Evidence Map](diagrams/beta-evidence-map.svg)

```mermaid
flowchart LR
  B1["Beta 1.0 manual + screenshot evals"] --> X["Binary transition logic"]
  X --> B2["Current OCR binary gate reports"]

  B1 --> W["manual_evals.db"]
  B2 --> R[".local/eval_reports/"]
  W --> P["/portfolio/sankey-data"]
  R --> P
  P --> V["Repo visuals: Sankey, diagrams, curated notebooks"]
```

## Notebook

- Notebook experiments and query outputs stay local-only under ignored output
  lanes by default.
- Promote only curated, non-private notebook outputs into public docs.
