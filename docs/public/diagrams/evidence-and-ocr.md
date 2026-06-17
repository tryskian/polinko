<!-- @format -->

# Evidence And OCR Diagrams

These diagrams collect the current OCR signal shape, operator-burden signal, and
tracked evidence-map surfaces.

## OCR Progress Funnel

![OCR Progress Funnel](ocr-progress-funnel.svg)

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

![Current OCR Signal Shape](current-ocr-signal-shape.svg)

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

## Operator Burden Signal Shape

![Operator Burden Signal Shape](operator-burden-signal-shape.svg)

```mermaid
flowchart TD
  A["Operator burden lane\n2026-05-12"] --> B["Pass anchors\n4 rows"]
  A --> C["Retained fail pressure\n2 rows\ninterpretive / advisory drift"]
  A --> D["Evicted duplicate pressure\n1 row\narchive-quoted clone"]
  A --> E["Backlog read\n9 conversations\n8 families"]
  E --> F["Current top slice is duplicate-heavy"]
  F --> G["No new row promotion earned\nwait for distinct task shape or improve visibility"]

  classDef pass fill:#EEF7EE,stroke:#59A14F,color:#1F1F1F;
  classDef fail fill:#FBEEEE,stroke:#E15759,color:#1F1F1F;
  classDef evidence fill:#EEF7F6,stroke:#76B7B2,color:#1F1F1F;
  classDef bridge fill:#FBF5E8,stroke:#F28E2B,color:#1F1F1F;

  class A,B pass;
  class C,D fail;
  class E,F,G evidence;
```

## Polinko Evidence Sankey

![Polinko Evidence Sankey](polinko-evidence-sankey.svg)

Static D3 Sankey generated from tracked eval evidence. It shows how Beta 1.0
manual evals flow through manual outcomes and signal classes into the current
OCR lane weighting surface.

## Beta Evidence Map

![Beta Evidence Map](beta-evidence-map.svg)

```mermaid
flowchart LR
  B1["Beta 1.0 manual + screenshot evals"] --> X["Binary transition logic"]
  X --> B2["Current OCR binary gate reports"]

  B1 --> W["manual_evals.db"]
  B2 --> R[".local/eval_reports/"]
  W --> P["Evidence Sankey payload"]
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
