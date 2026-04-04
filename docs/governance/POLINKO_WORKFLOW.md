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

## DB Viewer Enhanced: Runtime Query Pack

Use these directly in DB Viewer Enhanced.

### Active DB paths

- `history`: `/Users/tryskian/Github/polinko/.local/runtime_dbs/active/history.db`
- `memory`: `/Users/tryskian/Github/polinko/.local/runtime_dbs/active/memory.db`
- `vector`: `/Users/tryskian/Github/polinko/.local/runtime_dbs/active/vector.db`
- `eval_viz`: `/Users/tryskian/Github/polinko/.local/runtime_dbs/active/eval_viz.db`

### A) `history.db` (chat/runtime + OCR)

`/viz/pass-fail` is a local-only, visual-forward pulse surface. It uses
`history.db` as the source of truth for the moving chart itself. The chart
reads recent `ocr_runs`, classifies each row into `typed` / `handwriting` /
`illustration` in `api/eval_viz.py`, and then buckets those runs into a
smaller stacked lane strip for near-real-time, insight-first viewing. Raw
`ocr_runs` rows do not store a lane column directly.

#### 1) Recent OCR runs (latest first)

```sql
WITH runs AS (
  SELECT
    *,
    CASE WHEN created_at > 20000000000 THEN created_at / 1000 ELSE created_at END AS created_ts
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

#### 2) OCR status trend by day

```sql
WITH runs AS (
  SELECT
    status,
    CASE WHEN created_at > 20000000000 THEN created_at / 1000 ELSE created_at END AS created_ts
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

#### 3) OCR failures with source/result previews

```sql
WITH runs AS (
  SELECT
    *,
    CASE WHEN created_at > 20000000000 THEN created_at / 1000 ELSE created_at END AS created_ts
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
WHERE lower(r.status) <> 'ok'
ORDER BY r.created_ts DESC
LIMIT 200;
```

#### 3c) Recent OCR runs for pulse chart inspection

Use this when you want to inspect the raw rows that feed the pulse chart before
lane classification and bucketing happen in application code.

```sql
WITH runs AS (
  SELECT
    run_id,
    session_id,
    source_name,
    status,
    length(extracted_text) AS extracted_char_count,
    CASE WHEN created_at > 20000000000 THEN created_at / 1000 ELSE created_at END AS created_ts
  FROM ocr_runs
)
SELECT
  run_id,
  session_id,
  source_name,
  status,
  extracted_char_count,
  datetime(created_ts, 'unixepoch', 'localtime') AS created_local
FROM runs
ORDER BY created_ts DESC
LIMIT 120;
```

#### 3b) OCR trace-link completeness (attach-aware)

`source_message_id` / `result_message_id` are optional when OCR runs are not
attached to chat. Use this to see resolved references without inventing fake
chat message IDs.

```sql
SELECT
  run_id,
  session_id,
  source_name,
  status,
  source_message_id,
  result_message_id,
  CASE
    WHEN source_message_id IS NOT NULL AND trim(source_message_id) <> '' THEN source_message_id
    ELSE 'ocr://' || run_id || '/source'
  END AS source_ref_resolved,
  CASE
    WHEN result_message_id IS NOT NULL AND trim(result_message_id) <> '' THEN result_message_id
    ELSE 'ocr://' || run_id || '/result'
  END AS result_ref_resolved
FROM ocr_runs
ORDER BY created_at DESC
LIMIT 300;
```

#### 4) Feedback outcomes by session

```sql
SELECT
  mf.session_id,
  c.title AS chat_title,
  mf.outcome,
  COUNT(*) AS total_feedback,
  datetime(MAX(mf.updated_at), 'unixepoch', 'localtime') AS latest_feedback_local
FROM message_feedback mf
LEFT JOIN chats c ON c.session_id = mf.session_id
GROUP BY mf.session_id, c.title, mf.outcome
ORDER BY latest_feedback_local DESC, total_feedback DESC;
```

#### 5) Checkpoint pass/fail trend per session

```sql
SELECT
  ec.session_id,
  c.title AS chat_title,
  ec.checkpoint_id,
  ec.total_count,
  ec.pass_count,
  ec.fail_count,
  ROUND(100.0 * ec.pass_count / NULLIF(ec.total_count, 0), 1) AS pass_pct,
  datetime(ec.created_at, 'unixepoch', 'localtime') AS created_local
FROM eval_checkpoints ec
LEFT JOIN chats c ON c.session_id = ec.session_id
ORDER BY ec.created_at DESC
LIMIT 300;
```

#### 6) Chats with message volume and last activity

```sql
SELECT
  c.session_id,
  c.title,
  COUNT(m.id) AS total_messages,
  SUM(CASE WHEN m.role = 'user' THEN 1 ELSE 0 END) AS user_messages,
  SUM(CASE WHEN m.role = 'assistant' THEN 1 ELSE 0 END) AS assistant_messages,
  datetime(MAX(m.created_at), 'unixepoch', 'localtime') AS last_message_local
FROM chats c
LEFT JOIN chat_messages m ON m.session_id = c.session_id
GROUP BY c.session_id, c.title
ORDER BY last_message_local DESC;
```

### B) `memory.db` (agent memory lane)

#### 7) Session activity summary

```sql
SELECT
  s.session_id,
  s.created_at AS session_created_utc,
  s.updated_at AS session_updated_utc,
  COUNT(m.id) AS total_messages
FROM agent_sessions s
LEFT JOIN agent_messages m ON m.session_id = s.session_id
GROUP BY s.session_id, s.created_at, s.updated_at
ORDER BY s.updated_at DESC;
```

#### 8) Latest memory messages

```sql
SELECT
  m.id,
  m.session_id,
  substr(m.message_data, 1, 220) AS message_data_preview,
  m.created_at AS created_utc
FROM agent_messages m
ORDER BY m.id DESC
LIMIT 200;
```

### C) `vector.db` (embedding lane)

#### 9) Vector coverage by source type and role

```sql
SELECT
  source_type,
  role,
  COUNT(*) AS rows_count,
  SUM(CASE WHEN active = 1 THEN 1 ELSE 0 END) AS active_rows
FROM message_vectors
GROUP BY source_type, role
ORDER BY rows_count DESC;
```

#### 10) Potential vector wiring gaps

```sql
SELECT
  vector_id,
  session_id,
  role,
  source_type,
  message_id,
  source_ref,
  active,
  datetime(created_at, 'unixepoch', 'localtime') AS created_local
FROM message_vectors
WHERE (message_id IS NULL OR trim(message_id) = '')
  AND active = 1
ORDER BY created_at DESC
LIMIT 200;
```

If this returns rows for non-chat source types, run-time backfill has drifted.

### D) `eval_viz.db` (dashboard-ready eval points + pulse summary source)

`eval_viz.db` remains the evaluated surface. The local pulse page still uses it
for the headline pass-rate summary and latest eval detail rows when recent
`eval_points` exist, but it no longer drives the stacked timeline by itself.

#### 11) Eval outcomes by day and lane

```sql
SELECT
  date(datetime(ts_unix, 'unixepoch', 'localtime')) AS run_day,
  lane,
  lower(outcome) AS outcome,
  COUNT(*) AS points
FROM eval_points
GROUP BY run_day, lane, lower(outcome)
ORDER BY run_day DESC, lane, outcome;
```

#### 12) Latest failing points with evidence pointers

```sql
SELECT
  point_id,
  suite,
  lane,
  outcome,
  source_path,
  origin_file,
  substr(summary, 1, 180) AS summary_preview,
  substr(expected_text, 1, 120) AS expected_preview,
  substr(observed_text, 1, 120) AS observed_preview,
  datetime(ts_unix, 'unixepoch', 'localtime') AS ts_local
FROM eval_points
WHERE lower(outcome) = 'fail'
ORDER BY ts_unix DESC
LIMIT 300;
```

### Common mistakes to avoid

- Opening the wrong DB file for the target query.
- Treating mixed timestamp units as all-seconds.
- Filtering only `status='ok'` and hiding useful fail cohorts.
- Using `INNER JOIN` where `LEFT JOIN` is needed for diagnostics.
- Assuming one DB drives the whole OCR pulse page.
- Reading `eval_viz.db` only and expecting to reconstruct the live OCR timeline.
- Reading `history.db` only and expecting evaluated pass-rate summary/detail rows.
- For `/viz/pass-fail`, the wiring is hybrid:
  `history.db` / `ocr_runs` drive the bucketed lane chart, while `eval_viz.db`
  / `eval_points` drive the headline eval summary when available.
- Forgetting the charter constraints for this surface:
  it is meant to stay local-only, near-real-time, visual-forward, and
  insight-first rather than turning into a dense analytics dashboard.
