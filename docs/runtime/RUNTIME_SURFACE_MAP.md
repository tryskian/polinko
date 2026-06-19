<!-- @format -->

# Runtime Surface Map

Last updated: 2026-06-19

This map shows the local runtime and operator surfaces that need to stay
maintainable during the current refactor. It separates automatic startup,
human-led closeout, CI, background runners, and eval/workbench tooling so each
cleanup kernel can stay scoped.

```mermaid
flowchart TD
  subgraph Startup["Startup and workspace bootstrap"]
    VSCode["VS Code folder-open task"] --> MakeStart["make start"]
    MakeStart --> StartRoutine["tools/start_of_day_routine.sh"]
    StartRoutine --> Doctor["make doctor-env"]
    StartRoutine --> WakeLock["make caffeinate + caffeinate-status"]
    StartRoutine --> ApiSmoke["make api-smoke"]
    ApiSmoke --> SmokeServer["temporary uvicorn server"]
    ApiSmoke --> SmokeDbs["isolated smoke SQLite paths"]
    StartRoutine --> Rehydrate["rehydrate prompt + alignment pause"]
  end

  subgraph Closeout["Closeout and governance gate"]
    EndPreflight["make end-preflight"] --> BranchChecks["branch-local validation"]
    BranchChecks --> ProtectedPr["protected-main PR flow"]
    ProtectedPr --> MainSync["clean synced main"]
    MainSync --> MakeEnd["make end"]
    MakeEnd --> DocsGate["make end-docs-check"]
    MakeEnd --> ScriptGate["make scripts-check"]
    MakeEnd --> TestGate["style, type, docs, package, tests"]
    MakeEnd --> SecurityGate["make security-checks"]
    MakeEnd --> GitGate["make end-git-check"]
  end

  subgraph Runners["Background runner family"]
    ServerDaemon["server-daemon"]
    EvalSidecar["eval-sidecar"]
    PortfolioMockups["portfolio mockups"]
    ManagedCaffeinate["repo-managed caffeinate"]
    RunnerContract["shared PID, liveness, log, and cleanup pattern"]
    ServerDaemon --> RunnerContract
    EvalSidecar --> RunnerContract
    PortfolioMockups --> RunnerContract
    ManagedCaffeinate --> RunnerContract
  end

  subgraph Evals["Manual eval and OCR tooling"]
    ManualWorkbench["manual eval workbench"]
    DbHealth["manual_evals_db_health modules"]
    OcrInventory["read-only OCR inventory"]
    FeedbackDrafts["local decision drafts and previews"]
    EvalAliases["Make eval aliases and wrappers"]
    ManualWorkbench --> DbHealth
    ManualWorkbench --> OcrInventory
    ManualWorkbench --> FeedbackDrafts
    DbHealth --> EvalAliases
    OcrInventory --> EvalAliases
  end

  subgraph CI["CI and dependency automation"]
    GitHubActions["GitHub Actions"]
    Dependabot["Dependabot"]
    DependencyReview["dependency-review"]
    AuditTools["pip-audit and npm audit"]
    GitHubActions --> DependencyReview
    GitHubActions --> AuditTools
    Dependabot --> GitHubActions
  end

  Rehydrate --> Closeout
  Rehydrate --> Runners
  Rehydrate --> Evals
  BranchChecks --> CI
```

## Reading the Map

- Startup should stay narrow: it verifies environment health, starts the
  repo-managed wake lock, runs smoke checks with isolated defaults, and stops
  for alignment.
- Closeout is the complete stop-state contract: branch-local validation is
  preflight, but the final gate is `make end` from clean synced `main`.
- Background runners should converge on one ownership pattern for PID files,
  stale-process handling, logs, and cleanup commands.
- Manual eval and OCR tooling remain active workbench surfaces, but eval runs
  stay separate from startup and read-only inventory commands.
- CI and dependency automation should mirror local gates closely enough that
  failed remote runs point to real fixes, not setup drift.
