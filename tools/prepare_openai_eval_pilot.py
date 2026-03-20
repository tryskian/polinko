"""Prepare (and optionally execute) OpenAI Eval pilot wiring from local artifacts.

Manual-first workflow:
- writes create-eval and create-run payload JSON files
- optionally uploads dataset + creates eval + starts run when --execute is set
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Mapping

import requests

from tools.export_openai_eval_dataset import DEFAULT_ITEM_SCHEMA_JSON
from tools.export_openai_eval_dataset import DEFAULT_OUTPUT_JSONL

DEFAULT_EVAL_CREATE_PAYLOAD_JSON = Path(
    "docs/portfolio/raw_evidence/INBOX/openai_eval_create_payload.json"
)
DEFAULT_RUN_CREATE_PAYLOAD_JSON = Path(
    "docs/portfolio/raw_evidence/INBOX/openai_eval_run_payload.json"
)

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_EVAL_NAME = "Polinko Hybrid OpenAI Pilot"
DEFAULT_RUN_NAME = "Polinko Hybrid OpenAI Pilot Run"
DEFAULT_MODEL = "gpt-4.1-mini"

_PILOT_DEV_PROMPT = (
    "You are evaluating an existing local quality trace. "
    "Read the provided JSON fields and output exactly one word: pass or fail. "
    "Use this rule: if summary.outcome is pass then output pass; "
    "if summary.outcome is fail then output fail. "
    "Do not output anything else."
)
_PILOT_USER_TEMPLATE = (
    "tool_name={{ item.tool_name }}\n"
    "summary={{ item.summary }}\n"
    "gate_outcomes={{ item.gate_outcomes }}"
)


class PilotPrepareError(Exception):
    """Raised for invalid pilot setup or API execution errors."""


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise PilotPrepareError(f"Missing JSON file: {path}")
    parsed = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(parsed, Mapping):
        raise PilotPrepareError(f"Expected object JSON: {path}")
    return dict(parsed)


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(dict(payload), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def build_eval_create_payload(
    *,
    eval_name: str,
    item_schema: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "name": eval_name,
        "data_source_config": {
            "type": "custom",
            "item_schema": dict(item_schema),
            "include_sample_schema": True,
        },
        "testing_criteria": [
            {
                "type": "string_check",
                "name": "summary_outcome_match",
                "input": "{{ sample.output_text }}",
                "operation": "eq",
                "reference": "{{ item.summary.outcome }}",
            }
        ],
        "metadata": {
            "source": "polinko-hybrid-openai-pilot",
            "runtime_path": "/chat-unchanged",
            "mode": "tooling-only",
        },
    }


def build_run_create_payload(
    *,
    run_name: str,
    model: str,
    file_id: str,
) -> dict[str, Any]:
    file_id_clean = file_id.strip() or "file-REPLACE_ME"
    return {
        "name": run_name,
        "data_source": {
            "type": "responses",
            "model": model.strip(),
            "input_messages": {
                "type": "template",
                "template": [
                    {"role": "developer", "content": _PILOT_DEV_PROMPT},
                    {"role": "user", "content": _PILOT_USER_TEMPLATE},
                ],
            },
            "source": {"type": "file_id", "id": file_id_clean},
        },
        "metadata": {
            "source": "polinko-hybrid-openai-pilot",
            "runtime_path": "/chat-unchanged",
            "mode": "tooling-only",
        },
    }


def _headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def _upload_dataset(*, dataset_jsonl: Path, base_url: str, api_key: str) -> str:
    if not dataset_jsonl.exists():
        raise PilotPrepareError(f"Missing dataset JSONL: {dataset_jsonl}")
    with dataset_jsonl.open("rb") as handle:
        response = requests.post(
            f"{base_url.rstrip('/')}/files",
            headers={"Authorization": f"Bearer {api_key}"},
            data={"purpose": "evals"},
            files={"file": (dataset_jsonl.name, handle, "application/jsonl")},
            timeout=120,
        )
    if response.status_code >= 400:
        raise PilotPrepareError(
            f"File upload failed ({response.status_code}): {response.text[:500]}"
        )
    parsed = response.json()
    file_id = str(parsed.get("id", "")).strip()
    if not file_id:
        raise PilotPrepareError("Upload succeeded but no file id returned")
    return file_id


def _create_eval(
    *,
    create_payload: Mapping[str, Any],
    base_url: str,
    api_key: str,
) -> str:
    response = requests.post(
        f"{base_url.rstrip('/')}/evals",
        headers=_headers(api_key),
        json=dict(create_payload),
        timeout=120,
    )
    if response.status_code >= 400:
        raise PilotPrepareError(
            f"Create eval failed ({response.status_code}): {response.text[:500]}"
        )
    parsed = response.json()
    eval_id = str(parsed.get("id", "")).strip()
    if not eval_id:
        raise PilotPrepareError("Create eval succeeded but no eval id returned")
    return eval_id


def _create_run(
    *,
    eval_id: str,
    run_payload: Mapping[str, Any],
    base_url: str,
    api_key: str,
) -> tuple[str, str]:
    response = requests.post(
        f"{base_url.rstrip('/')}/evals/{eval_id}/runs",
        headers=_headers(api_key),
        json=dict(run_payload),
        timeout=120,
    )
    if response.status_code >= 400:
        raise PilotPrepareError(
            f"Create run failed ({response.status_code}): {response.text[:500]}"
        )
    parsed = response.json()
    run_id = str(parsed.get("id", "")).strip()
    report_url = str(parsed.get("report_url", "")).strip()
    if not run_id:
        raise PilotPrepareError("Create run succeeded but no run id returned")
    return run_id, report_url


@dataclass(frozen=True)
class PrepareResult:
    eval_payload_path: Path
    run_payload_path: Path
    dataset_jsonl_path: Path
    item_schema_path: Path
    file_id: str
    eval_id: str
    run_id: str
    report_url: str


def run_prepare(
    *,
    dataset_jsonl: Path,
    item_schema_json: Path,
    eval_payload_json: Path,
    run_payload_json: Path,
    eval_name: str,
    run_name: str,
    model: str,
    file_id: str,
    eval_id: str,
    execute: bool,
    upload_dataset: bool,
    api_key_env: str,
    base_url: str,
) -> PrepareResult:
    item_schema = _load_json(item_schema_json)
    eval_payload = build_eval_create_payload(eval_name=eval_name, item_schema=item_schema)

    resolved_file_id = file_id.strip()
    if execute and upload_dataset:
        api_key = os.getenv(api_key_env, "").strip()
        if not api_key:
            raise PilotPrepareError(
                f"Missing API key env var: {api_key_env} (required for --execute --upload-dataset)"
            )
        resolved_file_id = _upload_dataset(
            dataset_jsonl=dataset_jsonl, base_url=base_url, api_key=api_key
        )

    run_payload = build_run_create_payload(
        run_name=run_name,
        model=model,
        file_id=resolved_file_id,
    )
    _write_json(eval_payload_json, eval_payload)
    _write_json(run_payload_json, run_payload)

    resolved_eval_id = eval_id.strip()
    run_id = ""
    report_url = ""
    if execute:
        api_key = os.getenv(api_key_env, "").strip()
        if not api_key:
            raise PilotPrepareError(
                f"Missing API key env var: {api_key_env} (required for --execute)"
            )
        if not resolved_file_id:
            raise PilotPrepareError(
                "Missing --file-id for --execute. Provide --file-id or use --upload-dataset."
            )
        if not resolved_eval_id:
            resolved_eval_id = _create_eval(
                create_payload=eval_payload,
                base_url=base_url,
                api_key=api_key,
            )
        run_id, report_url = _create_run(
            eval_id=resolved_eval_id,
            run_payload=run_payload,
            base_url=base_url,
            api_key=api_key,
        )

    return PrepareResult(
        eval_payload_path=eval_payload_json,
        run_payload_path=run_payload_json,
        dataset_jsonl_path=dataset_jsonl,
        item_schema_path=item_schema_json,
        file_id=resolved_file_id,
        eval_id=resolved_eval_id,
        run_id=run_id,
        report_url=report_url,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare OpenAI Eval pilot create/run payloads from exported local "
            "dataset artifacts (manual-first; execute is opt-in)."
        )
    )
    parser.add_argument(
        "--dataset-jsonl",
        default=str(DEFAULT_OUTPUT_JSONL),
        help="Input exported dataset JSONL file.",
    )
    parser.add_argument(
        "--item-schema-json",
        default=str(DEFAULT_ITEM_SCHEMA_JSON),
        help="Input exported item schema JSON file.",
    )
    parser.add_argument(
        "--eval-payload-json",
        default=str(DEFAULT_EVAL_CREATE_PAYLOAD_JSON),
        help="Output JSON path for create-eval payload.",
    )
    parser.add_argument(
        "--run-payload-json",
        default=str(DEFAULT_RUN_CREATE_PAYLOAD_JSON),
        help="Output JSON path for create-run payload.",
    )
    parser.add_argument("--eval-name", default=DEFAULT_EVAL_NAME)
    parser.add_argument("--run-name", default=DEFAULT_RUN_NAME)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument(
        "--file-id",
        default="",
        help="Uploaded eval dataset file id to use in run payload.",
    )
    parser.add_argument(
        "--eval-id",
        default="",
        help="Reuse existing eval id when executing run creation.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute API calls (upload/create eval/create run).",
    )
    parser.add_argument(
        "--upload-dataset",
        action="store_true",
        help="Upload dataset JSONL to Files API with purpose=evals (implies --execute).",
    )
    parser.add_argument(
        "--api-key-env",
        default="OPENAI_API_KEY",
        help="Environment variable containing API key for --execute.",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help="OpenAI API base URL (default: https://api.openai.com/v1).",
    )
    args = parser.parse_args()

    execute = bool(args.execute or args.upload_dataset)
    try:
        result = run_prepare(
            dataset_jsonl=Path(args.dataset_jsonl),
            item_schema_json=Path(args.item_schema_json),
            eval_payload_json=Path(args.eval_payload_json),
            run_payload_json=Path(args.run_payload_json),
            eval_name=args.eval_name,
            run_name=args.run_name,
            model=args.model,
            file_id=args.file_id,
            eval_id=args.eval_id,
            execute=execute,
            upload_dataset=bool(args.upload_dataset),
            api_key_env=args.api_key_env,
            base_url=args.base_url,
        )
    except PilotPrepareError as exc:
        print(f"NOT_OK: {exc}")
        return 1

    print("OK")
    print(f"Dataset JSONL: {result.dataset_jsonl_path}")
    print(f"Item schema JSON: {result.item_schema_path}")
    print(f"Create-eval payload: {result.eval_payload_path}")
    print(f"Create-run payload: {result.run_payload_path}")
    print(f"File id: {result.file_id or 'file-REPLACE_ME'}")
    if result.eval_id:
        print(f"Eval id: {result.eval_id}")
    if result.run_id:
        print(f"Run id: {result.run_id}")
    if result.report_url:
        print(f"Report URL: {result.report_url}")
    if not execute:
        print("Execution mode: prepare-only (no API calls)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
