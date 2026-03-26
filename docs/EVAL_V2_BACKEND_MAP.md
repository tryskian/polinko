# Eval V2 Backend Map

## Scope

This map is derived from the current repository implementation on 26 March 2026.
It is intentionally code-first and excludes deprecated narrative docs as a source
of truth.

Primary sources:

- `api/app_factory.py`
- `core/history_store.py`
- `core/vector_store.py`
- `Makefile`
- `tools/eval_*.py`
- `tools/eval_trace_artifacts.py`

## Runtime Topology

1. `server.py` loads config and creates FastAPI app via `create_app(...)`.
2. `api/app_factory.py` owns HTTP contracts and eval/feedback orchestration.
3. `core/history_store.py` persists chat, feedback, and checkpoint records in SQLite.
4. `core/vector_store.py` persists retrieval memory vectors in SQLite.
5. `tools/eval_*.py` executes harnesses against API endpoints and writes reports/traces.

## API Surface (Current)

| Method | Path | Handler |
| --- | --- | --- |
| GET | `/health` | `health` |
| GET | `/metrics` | `metrics` |
| GET | `/chats` | `list_chats` |
| POST | `/chats` | `create_chat` |
| GET | `/chats/{session_id}/messages` | `list_chat_messages` |
| GET | `/chats/{session_id}/feedback` | `list_chat_feedback` |
| POST | `/chats/{session_id}/feedback` | `submit_chat_feedback` |
| GET | `/chats/{session_id}/feedback/checkpoints` | `list_eval_checkpoints` |
| POST | `/chats/{session_id}/feedback/checkpoints` | `submit_eval_checkpoint` |
| GET | `/chats/{session_id}/export` | `export_chat` |
| POST | `/skills/ocr` | `run_ocr` |
| POST | `/skills/pdf_ingest` | `pdf_ingest` |
| POST | `/skills/file_search` | `file_search` |
| PATCH | `/chats/{session_id}` | `rename_chat` |
| DELETE | `/chats/{session_id}` | `delete_chat` |
| POST | `/chats/{session_id}/deprecate` | `deprecate_chat` |
| POST | `/chats/{session_id}/notes` | `add_note` |
| POST | `/chats/{session_id}/personalization` | `set_chat_personalization` |
| GET | `/chats/{session_id}/personalization` | `get_chat_personalization` |
| GET | `/chats/{session_id}/collaboration` | `get_chat_collaboration` |
| POST | `/chats/{session_id}/collaboration/handoff` | `handoff_chat_collaboration` |
| POST | `/chat` | `chat` |
| POST | `/session/reset` | `reset_session` |

## Eval and Feedback Persistence Surfaces

SQLite (`core/history_store.py`):

- `message_feedback`
  - keyed by `(session_id, message_id)`
  - stores `outcome`, `positive_tags`, `negative_tags`, `status`, notes/actions
- `eval_checkpoints`
  - stores `checkpoint_id`, `session_id`, and summary counts

File-based evidence logs (`api/app_factory.py`):

- `docs/portfolio/raw_evidence/INBOX/eval_submissions.jsonl`
- `docs/portfolio/raw_evidence/INBOX/eval_checkpoints.jsonl`
- `docs/portfolio/raw_evidence/INBOX/feedback_actions.md`

Trace artifacts (`tools/eval_trace_artifacts.py`):

- default path: `docs/portfolio/raw_evidence/INBOX/eval_trace_artifacts.jsonl`
- schema version: `polinko.eval_trace.v1`

## Current Feedback Logic (Important)

Current API validation is already binary for outcome values:

- accepted: `pass`, `fail`
- rejected: everything else

Current checkpoint counting uses dual-stream tag arithmetic:

- `pass_count` increments when `positive_tags` exist
- `fail_count` increments when `negative_tags` exist
- one entry can increment both counts

This is the main behaviour to normalise in Eval V2.

## Eval Harness Surface

Entry points (Makefile):

- `eval-retrieval` -> `tools.eval_retrieval`
- `eval-file-search` -> `tools.eval_file_search`
- `eval-ocr` -> `tools.eval_ocr`
- `eval-ocr-recovery` -> `tools.eval_ocr_recovery`
- `eval-style` -> `tools.eval_style`
- `eval-hallucination` -> `tools.eval_hallucination`
- `eval-clip-ab` -> `tools.eval_clip_ab`
- `eval-inbox` -> `tools.eval_inbox`
- `eval-reports`, `eval-reports-parallel`
- `quality-gate`, `quality-gate-deterministic`, `backend-gate`

Eval harness endpoints exercised:

- `/health`
- `/chat`
- `/chats`
- `/chats/{session_id}`
- `/chats/{session_id}/personalization`
- `/skills/ocr`
- `/skills/pdf_ingest`
- `/skills/file_search`

## Current-Risk Hotspots

1. Checkpoint arithmetic is ambiguous because one row can count as both pass and fail.
2. Legacy evidence buckets (`PASS/MIXED/FAIL`) can conflict with binary API semantics.
3. Eval artefacts are split across SQLite and JSONL/Markdown logs without one canonical aggregation model.
4. Gate runs depend on local server lifecycle/ports; concurrent runs can collide without explicit port isolation.
