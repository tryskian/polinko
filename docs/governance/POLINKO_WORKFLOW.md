# Polinko Workflow

## Purpose

Use this when you want answers, planning, or interpretation without triggering
implementation flow.

## Routing Rules

- Use this thread (codexbeab) for:
  - product/runtime/governance context
  - architecture/process judgement
  - decisions tied to active Polinko build state
- Use a separate agent/thread for:
  - non-blocking side questions
  - external site/content work (`krystian.io`, portfolio copy, narrative framing)
  - tool-specific learning tracks (SQLite viewer workflows, notebook UX)

## Ask Format (No-Execution)

Use this 5-line format when you want answer-only mode:

```text
Mode: answer-only
Objective: <what you need>
Scope: <files/tools/context to use>
Constraints: no code changes, no git actions, no implementation steps
Output: short guidance + examples only
```

## Ask Format (Execution)

Use this format when you want implementation:

```text
Mode: execute
Objective: <change to make>
Scope: <where to change>
Acceptance: <how done is measured>
```

## Copy/Paste Prompts

### SQLite Viewer (answer-only)

```text
Mode: answer-only
Objective: teach me how to query DB Viewer Enhanced for Polinko eval/runtime DBs
Scope: this repo context only
Constraints: no code changes, no git actions
Output: 8-12 practical queries, what each query tells me, and common mistakes
```

### `krystian.io` landing-page refresh (strategy first)

```text
Mode: answer-only
Objective: define a content and structure refresh plan for krystian.io
Scope: role narrative, portfolio positioning, information architecture
Constraints: no code changes yet
Output: page outline, section copy direction, CTA strategy, and visual tone guidance
```

## When To Split Into A New Agent

- Split when the question does not require current branch/runtime state.
- Split when you want uninterrupted implementation to continue here.
- Split when topic is content/research-heavy and not build-critical.

## Ownership Boundary

- Imagineer sets objective, scope, and go/no-go.
- Engineer executes implementation when mode is `execute`.
- In `answer-only` mode, response stays advisory and non-operational.

## DB Viewer Enhanced: `ocr_runs` Query Pack

Use these directly in DB Viewer Enhanced against:
`/Users/tryskian/Github/polinko/.local/runtime_dbs/active/history.db`

### 1) Recent OCR runs (latest first)

```sql
WITH runs AS (
  SELECT
    *,
    CASE
      WHEN created_at > 20000000000 THEN created_at / 1000
      ELSE created_at
    END AS created_ts
  FROM ocr_runs
)
SELECT
  run_id,
  session_id,
  source_name,
  status,
  length(extracted_text) AS extracted_char_count,
  datetime(created_ts, 'unixepoch', 'localtime') AS created_local
FROM runs
ORDER BY created_ts DESC
LIMIT 200;
```

### 2) Status breakdown

```sql
SELECT
  status,
  COUNT(*) AS total_runs
FROM ocr_runs
GROUP BY status
ORDER BY total_runs DESC;
```

### 3) Daily pass/fail trend

```sql
WITH runs AS (
  SELECT
    status,
    CASE
      WHEN created_at > 20000000000 THEN created_at / 1000
      ELSE created_at
    END AS created_ts
  FROM ocr_runs
)
SELECT
  date(datetime(created_ts, 'unixepoch', 'localtime')) AS run_day,
  status,
  COUNT(*) AS total_runs
FROM runs
GROUP BY run_day, status
ORDER BY run_day DESC, status;
```

### 4) Failure cohort (latest)

```sql
WITH runs AS (
  SELECT
    *,
    CASE
      WHEN created_at > 20000000000 THEN created_at / 1000
      ELSE created_at
    END AS created_ts
  FROM ocr_runs
)
SELECT
  run_id,
  session_id,
  source_name,
  status,
  substr(extracted_text, 1, 180) AS extracted_preview,
  datetime(created_ts, 'unixepoch', 'localtime') AS created_local
FROM runs
WHERE lower(status) <> 'ok'
ORDER BY created_ts DESC
LIMIT 200;
```

### 5) OCR load by session

```sql
WITH runs AS (
  SELECT
    *,
    CASE
      WHEN created_at > 20000000000 THEN created_at / 1000
      ELSE created_at
    END AS created_ts
  FROM ocr_runs
)
SELECT
  r.session_id,
  c.title AS chat_title,
  COUNT(*) AS total_runs,
  SUM(CASE WHEN lower(r.status) <> 'ok' THEN 1 ELSE 0 END) AS non_ok_runs,
  datetime(MAX(r.created_ts), 'unixepoch', 'localtime') AS latest_run_local
FROM runs r
LEFT JOIN chats c ON c.session_id = r.session_id
GROUP BY r.session_id, c.title
ORDER BY total_runs DESC, latest_run_local DESC;
```

### 6) Source files with repeated failures

```sql
SELECT
  source_name,
  COUNT(*) AS fail_runs
FROM ocr_runs
WHERE lower(status) <> 'ok'
GROUP BY source_name
HAVING COUNT(*) >= 2
ORDER BY fail_runs DESC, source_name;
```

### 7) OCR output length distribution by status

```sql
SELECT
  status,
  COUNT(*) AS runs,
  ROUND(AVG(length(extracted_text)), 1) AS avg_chars,
  MIN(length(extracted_text)) AS min_chars,
  MAX(length(extracted_text)) AS max_chars
FROM ocr_runs
GROUP BY status
ORDER BY runs DESC;
```

### 8) Link OCR run to source/result message content

```sql
WITH runs AS (
  SELECT
    *,
    CASE
      WHEN created_at > 20000000000 THEN created_at / 1000
      ELSE created_at
    END AS created_ts
  FROM ocr_runs
)
SELECT
  r.run_id,
  r.session_id,
  r.source_name,
  r.status,
  datetime(r.created_ts, 'unixepoch', 'localtime') AS created_local,
  substr(sm.content, 1, 140) AS source_message_preview,
  substr(rm.content, 1, 140) AS result_message_preview
FROM runs r
LEFT JOIN chat_messages sm ON sm.message_id = r.source_message_id
LEFT JOIN chat_messages rm ON rm.message_id = r.result_message_id
ORDER BY r.created_ts DESC
LIMIT 200;
```
