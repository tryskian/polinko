<!-- @format -->

# Eval Contract Diagrams

These diagrams describe Polinko’s binary eval contract and the post-fail
evidence loop.

## Polinko Eval Contract

![Polinko Eval Contract](polinko-eval-contract.svg)

```mermaid
flowchart LR
  A["Source evidence"] --> B["Eval row"]
  B --> C{"First gate:\nhard contract correctness"}
  C -->|"PASS"| D["Binary release confidence"]
  C -->|"FAIL"| E["Failure evidence"]
  E --> F{"RETAIN / EVICT"}
  F -->|"RETAIN"| G["Keep row in active lane"]
  F -->|"EVICT"| H["Upstream case or miner correction"]
  D --> I["Richer interpretation\ncan annotate but not rewrite gate"]
  G --> I
  H --> J["Rerun corrected lane"]
  J --> B

  classDef source fill:#EEF4FB,stroke:#4E79A7,color:#1F1F1F;
  classDef bridge fill:#FBF5E8,stroke:#F28E2B,color:#1F1F1F;
  classDef pass fill:#EEF7EE,stroke:#59A14F,color:#1F1F1F;
  classDef fail fill:#FBEEEE,stroke:#E15759,color:#1F1F1F;
  classDef evidence fill:#EEF7F6,stroke:#76B7B2,color:#1F1F1F;

  class A,B source;
  class C,F bridge;
  class D,G,J pass;
  class E fail;
  class H,I evidence;
```

## Polinko Post-Fail Gate Stack

![Polinko Post-Fail Gate Stack](polinko-post-fail-gate-stack.svg)

```mermaid
flowchart LR
  A["Eval row"] --> B{"PASS / FAIL"}
  B -->|"PASS"| C["Retain confidence"]
  B -->|"FAIL"| D["Failure evidence"]
  D --> E{"RETAIN / EVICT"}
  E -->|"RETAIN"| F["Keep row in active lane"]
  F --> G["Accumulate more judged signal"]
  G --> A
  E -->|"EVICT"| H["Upstream case or scope correction"]
  H --> I["Rerun corrected lane"]
  I --> A

  classDef source fill:#EEF4FB,stroke:#4E79A7,color:#1F1F1F;
  classDef bridge fill:#FBF5E8,stroke:#F28E2B,color:#1F1F1F;
  classDef pass fill:#EEF7EE,stroke:#59A14F,color:#1F1F1F;
  classDef fail fill:#FBEEEE,stroke:#E15759,color:#1F1F1F;
  classDef evidence fill:#EEF7F6,stroke:#76B7B2,color:#1F1F1F;

  class A source;
  class B,E bridge;
  class C,F,G,I pass;
  class D fail;
  class H evidence;
```

## Polinko Binary Eval Loop

![Polinko Binary Eval Loop](polinko-binary-eval-loop.svg)

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
