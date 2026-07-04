<!-- @format -->

# Refactor Journey Diagrams

These diagrams show the refactor journey by lane: first evidence baseline,
runtime/package movement, automation-backed contracts, manual-eval workbench
preservation, logged research-prompt evals, and documentation pocket routing.

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

## Refactor Journey: Automation-Backed Contracts

![Refactor Journey: Automation-Backed Contracts](refactor-journey-automation-backed-contracts.svg)

```mermaid
flowchart TD
  A["CI runner refactor:\nshared build gates"] --> B["Operator friction signal:\nrepeated shell-style failures"]
  B --> C["Promote as repo contract:\nmake scripts-check"]
  C --> D["Cover active execution surfaces:\nshell helpers\nMake recipe files"]
  D --> E["Allow safe output patterns:\nquoted heredoc Markdown"]
  E --> F["Focused contract tests:\nshell scripts\nMakefile integration"]
  F --> G["Validation path:\npr-preflight\nPR checks\nmain CI"]
  G --> H["Current-truth docs:\nSTATE\nruntime references\nD-395"]
  H --> I["Next automation lane:\nCI failure visibility"]

  classDef source fill:#EEF4FB,stroke:#4E79A7,color:#1F1F1F;
  classDef bridge fill:#FBF5E8,stroke:#F28E2B,color:#1F1F1F;
  classDef pass fill:#EEF7EE,stroke:#59A14F,color:#1F1F1F;
  classDef evidence fill:#EEF7F6,stroke:#76B7B2,color:#1F1F1F;

  class A source;
  class B,C,D bridge;
  class E,F,G pass;
  class H,I evidence;
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

## Refactor Journey: Logged Research-Prompt Eval Bridge

![Refactor Journey: Logged Research-Prompt Eval Bridge](refactor-journey-logged-research-prompt-eval-bridge.svg)

```mermaid
flowchart TD
  A["Manual eval workbench\nand runtime history"] --> B["Reusable research prompt packet"]
  B --> C["Polinko runtime response\nthrough active backend"]
  C --> D["Database-backed eval row:\nprompt\nresponse\nmetadata"]
  D --> E["Human review:\npass/fail or notes"]
  E --> F["Evidence note:\nsource pointer\nreview state"]
  F --> G["Promoted research surfaces:\ntheory map\nfolio\nfuture grants"]
  G --> H["Next portability lane:\nbackend-neutral eval packet"]

  classDef source fill:#EEF4FB,stroke:#4E79A7,color:#1F1F1F;
  classDef bridge fill:#FBF5E8,stroke:#F28E2B,color:#1F1F1F;
  classDef pass fill:#EEF7EE,stroke:#59A14F,color:#1F1F1F;
  classDef evidence fill:#EEF7F6,stroke:#76B7B2,color:#1F1F1F;

  class A,B source;
  class C,D bridge;
  class E,F evidence;
  class G,H pass;
```

## Refactor Journey: Documentation Pockets

![Refactor Journey: Documentation Pockets](refactor-journey-documentation-pockets.svg)

```mermaid
flowchart TD
  A["Kernel lands"] --> B["Classify documentation pocket"]
  B --> C["Governance pocket:\nCHARTER\nSTATE\nDECISIONS"]
  B --> D["Runtime pocket:\nRUNBOOK\nARCHITECTURE\nruntime maps"]
  B --> E["Evidence pocket:\neval\nresearch\npublic docs"]
  B --> F["Local pocket:\ndocs/peanut\nSESSION_HANDOFF"]
  C --> G["Current snapshot:\nSTATE stays compact"]
  C --> H["Durable history:\nDECISIONS only"]
  D --> I["Operational procedure\nand surface maps"]
  E --> J["Source-led public\nand research references"]
  F --> K["Working notes\nand next-session carryover"]
  G --> L["Validation and PR"]
  H --> L
  I --> L
  J --> L
  K --> L
  L --> M["Squash merge"]
  M --> N["Final gate on synced main:\nmake end"]

  classDef source fill:#EEF4FB,stroke:#4E79A7,color:#1F1F1F;
  classDef bridge fill:#FBF5E8,stroke:#F28E2B,color:#1F1F1F;
  classDef pass fill:#EEF7EE,stroke:#59A14F,color:#1F1F1F;
  classDef evidence fill:#EEF7F6,stroke:#76B7B2,color:#1F1F1F;

  class A,B source;
  class C,D,E,F bridge;
  class G,H,I,J,K evidence;
  class L,M,N pass;
```
