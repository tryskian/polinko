<!-- @format -->

# Diagrams

This page collects the main repo-native diagrams. Start with the current OCR
state, then use the method and continuity diagrams below.

Static SVG exports generated from this page:

- [OCR Progress Funnel](diagrams/ocr-progress-funnel.svg)
- [Current OCR Signal Shape](diagrams/current-ocr-signal-shape.svg)
- [Polinko Evidence Sankey (D3)](diagrams/polinko-evidence-sankey.svg)
- [Polinko Binary Eval Loop](diagrams/polinko-binary-eval-loop.svg)
- [Beta Evidence Map](diagrams/beta-evidence-map.svg)

Current dated progress note:

- [OCR Progress Snapshot (2026-05-08)](../research/ocr-progress-20260508.md)
- [Prior OCR Progress Snapshot (2026-05-01)](../research/ocr-progress-20260501.md)

## OCR Progress Funnel

![OCR Progress Funnel](diagrams/ocr-progress-funnel.svg)

```mermaid
flowchart LR
  A["Transcript mining\n54 OCR-framed episodes"] --> B["Strict emitted cases\n23"]
  B --> C["Growth case set\n25"]
  C --> D["Batched replay\n25/25 pass"]
  D --> E["Growth stability\n5 runs\n25 stable\n0 flaky"]
  E --> F["Fail cohort\n0 fail-history cases"]
  E --> G["Exploratory focus\n16 cases"]
  G --> H["Focus stability\n3 runs\n16 stable\n0 flaky"]

  classDef source fill:#EEF4FB,stroke:#4E79A7,color:#1F1F1F;
  classDef bridge fill:#FBF5E8,stroke:#F28E2B,color:#1F1F1F;
  classDef pass fill:#EEF7EE,stroke:#59A14F,color:#1F1F1F;
  classDef evidence fill:#EEF7F6,stroke:#76B7B2,color:#1F1F1F;

  class A,B source;
  class C,D,G bridge;
  class E,F,H pass;
```

## Current OCR Signal Shape

![Current OCR Signal Shape](diagrams/current-ocr-signal-shape.svg)

```mermaid
flowchart TD
  A["Current OCR lane\n2026-05-08"] --> B["Fail pressure\n0 active failing cases"]
  A --> C["Decision stability\n25/25 growth stable\n16/16 focus stable"]
  A --> D["Exploratory variability\n16 growth cases\n10 focus cases"]
  D --> E["Runtime OCR\nparked"]
  D --> F["If OCR reopens\ncase-design-only watchlist\n2 cases"]

  classDef pass fill:#EEF7EE,stroke:#59A14F,color:#1F1F1F;
  classDef bridge fill:#FBF5E8,stroke:#F28E2B,color:#1F1F1F;
  classDef evidence fill:#EEF7F6,stroke:#76B7B2,color:#1F1F1F;

  class A,B,C,E pass;
  class D,F evidence;
```

## Polinko Evidence Sankey (D3)

![Polinko Evidence Sankey](diagrams/polinko-evidence-sankey.svg)

Static D3 Sankey generated from the real `/portfolio/sankey-data` payload. It
shows how Beta 1.0 manual evals flow through manual outcomes and signal
classes into the current OCR lane weighting surface.

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

## Reference Note

The older baseline product-pipeline diagram is no longer a primary public
surface. It was useful as category framing, but the current OCR diagrams are
the more meaningful front-door visual signal.

## Notebook

- Notebook experiments and query outputs stay local-only under ignored output
  lanes by default.
- Promote only curated, non-private notebook outputs into public docs.
