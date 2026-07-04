<!-- @format -->

# Refactor Method Diagrams

These diagrams describe the working method used during the current Polinko
refactor.

## Refactor Operating Loop

![Refactor Operating Loop](refactor-operating-loop.svg)

```mermaid
flowchart TD
  A["Talk first"] --> B["Align active kernel"]
  B --> C["Confirm source, scope, and success shape"]
  C --> D["Inspect live repo state"]
  D --> E["Map ownership, overlap,\nand validation coverage"]
  E --> F["Choose smallest coherent refactor slice"]
  F --> G["Implement on feature branch"]
  G --> H["Run focused validation"]
  H --> I{"Pass?"}
  I -->|"Yes"| J["Update docs, decisions, and handoff if needed"]
  I -->|"No"| K["Diagnose from evidence"]
  K --> G
  J --> L["Checkpoint, PR, and merge path"]
  L --> M["Return to clean synced main"]
  M --> N["Run closeout gate"]
  N --> O["Next kernel"]

  classDef source fill:#EEF4FB,stroke:#4E79A7,color:#1F1F1F;
  classDef bridge fill:#FBF5E8,stroke:#F28E2B,color:#1F1F1F;
  classDef pass fill:#EEF7EE,stroke:#59A14F,color:#1F1F1F;
  classDef fail fill:#FBEEEE,stroke:#E15759,color:#1F1F1F;
  classDef evidence fill:#EEF7F6,stroke:#76B7B2,color:#1F1F1F;

  class A,B,C,D,E,F,L,M,N,O bridge;
  class G,J pass;
  class H source;
  class I evidence;
  class K fail;
```

## One Kernel Rule

![One Kernel Rule](one-kernel-rule.svg)

```mermaid
flowchart LR
  A["Current kernel"] --> B["Inspect"]
  B --> C["Edit"]
  C --> D["Validate"]
  D --> E["Document"]
  E --> F["Checkpoint"]

  G["Side idea"] --> H["Queue"]
  H --> F

  I["Stop, wait, or correction"] --> J["Pause"]
  J --> K["Realign"]
  K --> A

  classDef source fill:#EEF4FB,stroke:#4E79A7,color:#1F1F1F;
  classDef bridge fill:#FBF5E8,stroke:#F28E2B,color:#1F1F1F;
  classDef pass fill:#EEF7EE,stroke:#59A14F,color:#1F1F1F;
  classDef fail fill:#FBEEEE,stroke:#E15759,color:#1F1F1F;
  classDef evidence fill:#EEF7F6,stroke:#76B7B2,color:#1F1F1F;

  class A,B,C,D,E,F pass;
  class G,H evidence;
  class I,J,K bridge;
```

## Refactor Source Hierarchy

![Refactor Source Hierarchy](refactor-source-hierarchy.svg)

```mermaid
flowchart TD
  A["Current user correction"] --> B["Active source for next move"]
  C["Live repo state"] --> B
  D["Tracked docs, code, and tests"] --> B
  E["docs/peanut local notes"] --> F["Private/context lane"]
  G["Memory"] --> H["Routing help"]
  I["Archived transcripts and old runtime state"] --> J["Theory evidence until promoted"]

  H --> B
  F --> B
  J --> B

  classDef source fill:#EEF4FB,stroke:#4E79A7,color:#1F1F1F;
  classDef bridge fill:#FBF5E8,stroke:#F28E2B,color:#1F1F1F;
  classDef pass fill:#EEF7EE,stroke:#59A14F,color:#1F1F1F;
  classDef evidence fill:#EEF7F6,stroke:#76B7B2,color:#1F1F1F;

  class A,B,C,D pass;
  class E,F,G,H,I,J evidence;
```

## Refactor Safety Gate

![Refactor Safety Gate](refactor-safety-gate.svg)

```mermaid
flowchart TD
  A["Proposed change"] --> B{"Changes behaviour?"}
  B -->|"Yes"| C["Human-led approval and decision framing"]
  B -->|"No"| D["Mechanical cleanup path"]

  C --> E["Implement with tests"]
  D --> E
  E --> F["Focused checks"]
  F --> G["Full checks when blast radius requires"]
  G --> H["Docs freshness and handoff"]
  H --> I["Merge only when stable"]

  classDef source fill:#EEF4FB,stroke:#4E79A7,color:#1F1F1F;
  classDef bridge fill:#FBF5E8,stroke:#F28E2B,color:#1F1F1F;
  classDef pass fill:#EEF7EE,stroke:#59A14F,color:#1F1F1F;
  classDef fail fill:#FBEEEE,stroke:#E15759,color:#1F1F1F;
  classDef evidence fill:#EEF7F6,stroke:#76B7B2,color:#1F1F1F;

  class A,D,E,F,G,H,I pass;
  class B bridge;
  class C evidence;
```

## Clean Main Closeout

![Clean Main Closeout](clean-main-closeout.svg)

```mermaid
flowchart TD
  A["Feature branch validated"] --> B["Commit"]
  B --> C["Push"]
  C --> D["PR"]
  D --> E["GitHub checks"]
  E --> F{"Checks pass?"}
  F -->|"No"| G["Fix on branch"]
  G --> E
  F -->|"Yes"| H["Squash merge"]
  H --> I["Switch to main"]
  I --> J["Pull fast-forward"]
  J --> K["Run make end"]
  K --> L{"Clean synced main?"}
  L -->|"Yes"| M["Closed kernel"]
  L -->|"No"| N["Resolve before stopping"]
  N --> K

  classDef source fill:#EEF4FB,stroke:#4E79A7,color:#1F1F1F;
  classDef bridge fill:#FBF5E8,stroke:#F28E2B,color:#1F1F1F;
  classDef pass fill:#EEF7EE,stroke:#59A14F,color:#1F1F1F;
  classDef fail fill:#FBEEEE,stroke:#E15759,color:#1F1F1F;
  classDef evidence fill:#EEF7F6,stroke:#76B7B2,color:#1F1F1F;

  class A,B,C,D,E,H,I,J,K,M pass;
  class F,L bridge;
  class G,N fail;
```
