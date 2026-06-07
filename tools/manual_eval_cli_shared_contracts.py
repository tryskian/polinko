from __future__ import annotations

from pathlib import Path

DEFAULT_DB_PATH = Path(".local/runtime_dbs/active/manual_evals.db")
OCR_RETRY_FEEDBACK_CLOSURE_WAREHOUSE_MUTATION_FIELD = "manual_eval_warehouse"

__all__ = [
    "DEFAULT_DB_PATH",
    "OCR_RETRY_FEEDBACK_CLOSURE_WAREHOUSE_MUTATION_FIELD",
]
