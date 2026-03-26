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
6. Web UI is deprecated for active eval operations; backend + CLI are canonical.

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

File-based evidence logs:

- runtime no longer writes eval feedback/checkpoint logs to `raw_evidence`
  top-level intake folders.
- archived trace artifacts remain available for audit/history:
  `docs/portfolio/raw_evidence/archive/baseline/eval-trace-records/eval_trace_artifacts.jsonl`

Trace artifacts (`tools/eval_trace_artifacts.py`):

- default path:
  `docs/portfolio/raw_evidence/archive/baseline/eval-trace-records/eval_trace_artifacts.jsonl`
- schema version: `polinko.eval_trace.v1`

## Current Feedback Logic (Important)

Current API validation is binary for outcome values:

- accepted: `pass`, `fail`
- rejected: everything else

Current checkpoint counting is outcome-driven:

- `pass_count = count(outcome == "pass")`
- `fail_count = count(outcome == "fail")`
- `non_binary_count` is an integrity signal and expected to remain `0`

Dual-stream tags remain diagnostic only and do not drive gate arithmetic.

## Eval Harness Surface

Entry points (Makefile):

- `eval-retrieval` -> `tools.eval_retrieval`
- `eval-file-search` -> `tools.eval_file_search`
- `eval-ocr` -> `tools.eval_ocr`
- `eval-ocr-recovery` -> `tools.eval_ocr_recovery`
- `eval-style` -> `tools.eval_style`
- `eval-hallucination` -> `tools.eval_hallucination`
- `eval-clip-ab` -> `tools.eval_clip_ab`
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

1. Stored rows outside binary contract (for example corrupted outcomes or
   malformed tag payload shape) can hard-fail read paths until repaired.
2. Evidence/log artefacts can drift from API contract if they are treated as
   canonical instead of runtime SQLite state.
3. Eval artefacts are split across SQLite and JSONL/Markdown logs without one
   canonical aggregation model.
4. Gate runs depend on local server lifecycle/ports; concurrent runs can
   collide without explicit port isolation.
