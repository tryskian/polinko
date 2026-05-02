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

Current dated progress note:

- [OCR Progress Snapshot (2026-05-01)](../research/ocr-progress-20260501.md)

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

  classDef source fill:#EEF4FB,stroke:#4E79A7,color:#1F1F1F;
  classDef bridge fill:#FBF5E8,stroke:#F28E2B,color:#1F1F1F;
  classDef evidence fill:#EEF7F6,stroke:#76B7B2,color:#1F1F1F;

  class A,D,F,H source;
  class B,C,E,G bridge;
  class I,J,K,L evidence;
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

  classDef source fill:#EEF4FB,stroke:#4E79A7,color:#1F1F1F;
  classDef bridge fill:#FBF5E8,stroke:#F28E2B,color:#1F1F1F;
  classDef pass fill:#EEF7EE,stroke:#59A14F,color:#1F1F1F;
  classDef fail fill:#FBEEEE,stroke:#E15759,color:#1F1F1F;
  classDef evidence fill:#EEF7F6,stroke:#76B7B2,color:#1F1F1F;

  class A,B source;
  class C,D,H bridge;
  class E,I pass;
  class F fail;
  class G evidence;
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

  classDef legacy fill:#EEF4FB,stroke:#4E79A7,color:#1F1F1F;
  classDef bridge fill:#FBF5E8,stroke:#F28E2B,color:#1F1F1F;
  classDef current fill:#F6EEF7,stroke:#B07AA1,color:#1F1F1F;
  classDef evidence fill:#EEF7F6,stroke:#76B7B2,color:#1F1F1F;

  class B1,W legacy;
  class X bridge;
  class B2,R current;
  class P,V evidence;
```

## Notebook

- Notebook experiments and query outputs stay local-only under ignored output
  lanes by default.
- Promote only curated, non-private notebook outputs into public docs.
