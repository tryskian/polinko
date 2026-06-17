<!-- @format -->

# Refactor Journey Diagrams

These diagrams show the refactor journey by lane: first evidence baseline,
runtime/package movement, manual-eval workbench preservation, and docs/closeout
propagation.

## Refactor Journey: Evidence First

![Refactor Journey: Evidence First](refactor-journey-evidence-first.svg)

```mermaid
flowchart LR
  A["Start surface:\nBeta 2.3 research state"] --> B["Freeze snapshot:\ndocs/eval/beta_2_3/"]
  B --> C["Promote public evidence:\ndocs/public/DIAGRAMS.md\nand docs/public/EVIDENCE.md"]
  C --> D["Keep private notes local:\ndocs/peanut/"]
  D --> E["Refactor against stable evidence\ninstead of moving research target"]

  classDef source fill:#EEF4FB,stroke:#4E79A7,color:#1F1F1F;
  classDef bridge fill:#FBF5E8,stroke:#F28E2B,color:#1F1F1F;
  classDef pass fill:#EEF7EE,stroke:#59A14F,color:#1F1F1F;
  classDef evidence fill:#EEF7F6,stroke:#76B7B2,color:#1F1F1F;

  class A source;
  class B,C,D evidence;
  class E pass;
```

## Refactor Journey: Runtime Package Boundary

![Refactor Journey: Runtime Package Boundary](refactor-journey-runtime-package-boundary.svg)

```mermaid
flowchart TD
  A["Package rail:\npyproject.toml"] --> B["Runtime package:\nsrc/polinko/"]
  B --> C["Config moved:\nsrc/polinko/config.py"]
  B --> D["API moved:\nsrc/polinko/api/"]
  B --> E["Core moved:\nsrc/polinko/core/"]
  B --> F["CLI moved:\nsrc/polinko/cli.py"]
  F --> G["Launcher IA:\nmain.py for chat\nserver.py for ASGI compatibility"]
  C --> H["Retire root config.py"]
  D --> I["Retire root api/"]
  E --> J["Retire root core/"]
  G --> K["Keep behaviour stable\nwhile names and imports settle"]

  classDef source fill:#EEF4FB,stroke:#4E79A7,color:#1F1F1F;
  classDef bridge fill:#FBF5E8,stroke:#F28E2B,color:#1F1F1F;
  classDef pass fill:#EEF7EE,stroke:#59A14F,color:#1F1F1F;
  classDef evidence fill:#EEF7F6,stroke:#76B7B2,color:#1F1F1F;

  class A,B source;
  class C,D,E,F,G bridge;
  class H,I,J evidence;
  class K pass;
```

## Refactor Journey: Manual Eval Workbench

![Refactor Journey: Manual Eval Workbench](refactor-journey-manual-eval-workbench.svg)

```mermaid
flowchart TD
  A["Manual eval workbench\nstays active"] --> B["Preserve chats:\n/chat and /chats/*"]
  A --> C["Preserve local evidence:\nmanual_evals.db\nnotebooks\nruntime history"]
  A --> D["Source-first APIs:\n/manual-evals/surface\n/viz/pass-fail/data"]
  D --> E["Schema and freshness:\nsummary_unit\nschema_version\ndata_freshness"]
  E --> F["Read-only CLI packets:\nstatus, health,\nfeedback, OCR retry"]
  F --> G["Shared parser, router,\nand dispatch helpers"]
  G --> H["Focused tests protect\nroute order, defaults,\nand schema contracts"]

  classDef source fill:#EEF4FB,stroke:#4E79A7,color:#1F1F1F;
  classDef bridge fill:#FBF5E8,stroke:#F28E2B,color:#1F1F1F;
  classDef pass fill:#EEF7EE,stroke:#59A14F,color:#1F1F1F;
  classDef evidence fill:#EEF7F6,stroke:#76B7B2,color:#1F1F1F;

  class A source;
  class B,C evidence;
  class D,E,F,G bridge;
  class H pass;
```

## Refactor Journey: Docs And Closeout

![Refactor Journey: Docs And Closeout](refactor-journey-docs-and-closeout.svg)

```mermaid
flowchart LR
  A["Kernel lands"] --> B["Update current truth:\ndocs/governance/STATE.md"]
  B --> C{"Durable decision?"}
  C -->|"Yes"| D["Record:\ndocs/governance/DECISIONS.md"]
  C -->|"No"| E["Keep in handoff\nor branch history"]
  D --> F["Refresh operator procedure:\ndocs/runtime/RUNBOOK.md\nwhen commands change"]
  E --> G["Local continuity:\ndocs/peanut/governance/SESSION_HANDOFF.md"]
  F --> H["Validation and PR"]
  G --> H
  H --> I["Squash merge"]
  I --> J["Final gate on synced main:\nmake end"]

  classDef source fill:#EEF4FB,stroke:#4E79A7,color:#1F1F1F;
  classDef bridge fill:#FBF5E8,stroke:#F28E2B,color:#1F1F1F;
  classDef pass fill:#EEF7EE,stroke:#59A14F,color:#1F1F1F;
  classDef evidence fill:#EEF7F6,stroke:#76B7B2,color:#1F1F1F;

  class A,B,F,G,H source;
  class C bridge;
  class D,E evidence;
  class I,J pass;
```
