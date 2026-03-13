# Portfolio Draft Package (Hybrid)

This folder is a working draft kit for `krystian.io` and role-targeted applications.
It is intentionally not final copy.

Use these files in order:

1. `01_positioning_narrative.md`
2. `02_case_studies.md`
3. `03_evidence_log.md`
4. `04_story_bank.md`
5. `05_resume_linkedin_bullets.md`
6. `06_demo_script.md`

## Primary portfolio stance

Behavioral research engineering:

- Behavioral observation and theory are first.
- Engineering is the implementation trace and validation layer.
- Every major claim maps to mechanism + evidence + build function.

## Lane Separation (Important)

Portfolio is not the theory source of truth.

- Theory lives in `docs/theory/` (hypotheses and falsification only).
- Research lives in `docs/research/` + eval/evidence artifacts.
- Portfolio in `docs/portfolio/` demonstrates implemented outcomes backed by
  research evidence.

Use `docs/WORKSTREAMS.md` as the contract between these lanes.

## Audience modes (same artifacts, different emphasis)

- `Research Engineer` view: tooling, evals, reliability infrastructure.
- `Applied Behavioral Research` view: interaction dynamics, boundary protocols, case interpretation.

Do not build two separate portfolios. Build one canonical set of artifacts with two entry views.

## How to use

- Start rough. Use bullets before prose.
- Keep section structure stable:
  - Abstract
  - Hypothesis (theory + approach)
  - Theory -> method translation
  - Case linkage
  - Conclusion (what this shows)
- Anchor every claim to evidence (tests, eval outputs, docs, transcripts, screenshots, build traces).
- Use framing lines as skeleton cues, not as proof.

## Workbench

Run from repo root:

- `make workbench`
- open `http://127.0.0.1:8020/workbench.html`

Workbench notes:

- Notebook opens in edit mode by default.
- Notebook supports local note pages (`New note`, `Rename note`, `Delete note`).
- Autosave is local (browser storage).
- `Cmd+S` / `Ctrl+S` saves current note/draft immediately.
- `Insert image` embeds the selected image into markdown as a data URL.
