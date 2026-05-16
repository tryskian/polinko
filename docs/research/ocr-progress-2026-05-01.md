<!-- @format -->

# OCR Progress Snapshot

- Run date: `2026-05-01`
- Kernel: `make ocrkernel CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT`
- Lane: `ocr_growth`
- Local report artifacts:
  - `.local/eval_cases/ocr_transcript_cases_delta.md`
  - `.local/eval_reports/ocr_growth_batched_summary.md`
  - `.local/eval_reports/ocr_growth_stability.json`
  - `.local/eval_reports/ocr_growth_metrics.md`
  - `.local/eval_reports/ocr_growth_fail_cohort.md`
  - `.local/eval_reports/ocr_focus_stability.json`
  - `.local/eval_reports/ocr_focus_fail_patterns.md`

## Summary

- Transcript OCR episodes: `54`
- Emitted strict cases: `23`
- Growth cases: `25`
- Growth batch replay: `25/25` pass
- Growth stability: `5/5` runs, `25` stable, `0` flaky
- Growth focus stability: `3/3` runs, `16` stable, `0` flaky
- Active fail cohort cases: `0`
- Focus fail patterns: `0/16` failing

## Progress Funnel

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

## Current Signal Shape

```mermaid
flowchart TD
  A["Current OCR growth lane\n2026-05-01"] --> B["Fail pressure\n0 active failing cases"]
  A --> C["Decision stability\n25/25 growth stable\n16/16 focus stable"]
  A --> D["Output variability\n16 growth cases\n11 focus cases"]
  D --> E["Next research kernel\ninspect exploratory variants"]

  classDef pass fill:#EEF7EE,stroke:#59A14F,color:#1F1F1F;
  classDef bridge fill:#FBF5E8,stroke:#F28E2B,color:#1F1F1F;
  classDef evidence fill:#EEF7F6,stroke:#76B7B2,color:#1F1F1F;

  class A,C pass;
  class B pass;
  class D,E evidence;
```

## Most Useful Signal

This kernel did not surface a new failing OCR cohort. The current signal is
clean on strict pass/fail and clean on replay stability. The remaining live OCR
research signal is exploratory output variability, not failing or flaky cases.

That matters because it changes the next move. The next OCR kernel is not
another generator fix. It is a review of the exploratory cases whose output
varies while still passing the current binary gate.
