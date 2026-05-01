import argparse
import json
import re
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from tools.eval_chat_common import create_chat as _create_chat
from tools.eval_chat_common import default_headers as _headers
from tools.eval_chat_common import delete_chat as _delete_chat
from tools.eval_chat_common import request_json as _request_json
from tools.eval_chat_common import send_chat as _send_chat
from tools.eval_gate import gate_counts_from_case_results
from tools.eval_gate import resolve_fail_closed_status
from tools.eval_ocr_common import build_chat_attachment
from tools.eval_ocr_common import ONE_BY_ONE_PNG_BYTES
from tools.eval_ocr_common import build_data_url
from tools.eval_ocr_common import load_attachment_input
from tools.eval_trace_artifacts import DEFAULT_TRACE_JSONL
from tools.eval_trace_artifacts import append_eval_trace
from tools.eval_trace_artifacts import build_eval_trace


def _preflight(base_url: str, headers: dict[str, str], timeout: int) -> None:
    from tools.eval_chat_common import preflight as _shared_preflight

    _shared_preflight(base_url, headers, timeout, check_chats=False)


def _load_cases(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Cases file must be a JSON object.")
    raw_cases = payload.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise RuntimeError("Cases file must include a non-empty 'cases' list.")

    normalized: list[dict[str, Any]] = []
    for idx, raw in enumerate(raw_cases, start=1):
        if not isinstance(raw, dict):
            raise RuntimeError(f"Case #{idx} must be an object.")
        case_id = str(raw.get("id", f"ocr-recovery-{idx}")).strip()
        if not case_id:
            raise RuntimeError(f"Case #{idx} must have non-empty id.")

        seed_prompt = str(raw.get("seed_prompt", "")).strip()
        if not seed_prompt:
            raise RuntimeError(f"Case '{case_id}' requires seed_prompt.")

        attachment = raw.get("attachment")
        if not isinstance(attachment, dict):
            raise RuntimeError(f"Case '{case_id}' requires attachment object.")

        image_path = str(attachment.get("image_path", "")).strip()
        text_hint = str(attachment.get("text_hint", "")).strip()
        source_name = str(attachment.get("source_name", "")).strip()
        mime_type = str(attachment.get("mime_type", "")).strip().lower()
        visual_context_hint = str(attachment.get("visual_context_hint", "")).strip()

        steps_raw = raw.get("steps")
        if not isinstance(steps_raw, list) or not steps_raw:
            raise RuntimeError(f"Case '{case_id}' requires non-empty steps list.")

        normalized_steps = []
        for step_index, step in enumerate(steps_raw, start=1):
            if not isinstance(step, dict):
                raise RuntimeError(
                    f"Case '{case_id}' step #{step_index} must be an object."
                )
            step_id = (
                str(step.get("id", f"step-{step_index}")).strip()
                or f"step-{step_index}"
            )
            user_prompt = str(step.get("user", "")).strip()
            normalized_steps.append(
                {
                    "id": step_id,
                    "user": user_prompt,
                    "attach_image": bool(step.get("attach_image", True)),
                    "must_contain": [
                        str(x).strip()
                        for x in step.get("must_contain", [])
                        if str(x).strip()
                    ],
                    "must_contain_any": [
                        str(x).strip()
                        for x in step.get("must_contain_any", [])
                        if str(x).strip()
                    ],
                    "must_not_contain": [
                        str(x).strip()
                        for x in step.get("must_not_contain", [])
                        if str(x).strip()
                    ],
                    "must_match_regex": [
                        str(x).strip()
                        for x in step.get("must_match_regex", [])
                        if str(x).strip()
                    ],
                    "must_not_match_regex": [
                        str(x).strip()
                        for x in step.get("must_not_match_regex", [])
                        if str(x).strip()
                    ],
                    "case_sensitive": bool(step.get("case_sensitive", False)),
                }
            )

        normalized.append(
            {
                "id": case_id,
                "seed_prompt": seed_prompt,
                "labeling_guidance": raw.get("labeling_guidance"),
                "attachment": {
                    "image_path": image_path,
                    "text_hint": text_hint or None,
                    "source_name": source_name or None,
                    "mime_type": mime_type or None,
                    "visual_context_hint": visual_context_hint or None,
                },
                "steps": normalized_steps,
            }
        )
    return normalized


def _check_constraints(
    step: dict[str, Any], response_text: str
) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    case_sensitive = bool(step["case_sensitive"])
    haystack = response_text if case_sensitive else response_text.lower()

    def contains(needle: str) -> bool:
        probe = needle if case_sensitive else needle.lower()
        return probe in haystack

    for phrase in step["must_contain"]:
        if not contains(phrase):
            reasons.append(f"missing required phrase: {phrase!r}")

    if step["must_contain_any"] and not any(
        contains(phrase) for phrase in step["must_contain_any"]
    ):
        reasons.append(f"missing one-of required phrases: {step['must_contain_any']}")

    for phrase in step["must_not_contain"]:
        if contains(phrase):
            reasons.append(f"contains forbidden phrase: {phrase!r}")

    regex_flags = 0 if case_sensitive else re.IGNORECASE
    for pattern in step["must_match_regex"]:
        try:
            if re.search(pattern, response_text, flags=regex_flags) is None:
                reasons.append(f"regex did not match: /{pattern}/")
        except re.error as exc:
            reasons.append(f"invalid must_match_regex pattern /{pattern}/: {exc}")

    for pattern in step["must_not_match_regex"]:
        try:
            if re.search(pattern, response_text, flags=regex_flags) is not None:
                reasons.append(f"forbidden regex matched: /{pattern}/")
        except re.error as exc:
            reasons.append(f"invalid must_not_match_regex pattern /{pattern}/: {exc}")

    return (len(reasons) == 0), reasons


def _read_attachment_payload(
    attachment: dict[str, Any],
) -> tuple[str, str, str | None, str | None]:
    raw_bytes, mime_type, source_name, text_hint = load_attachment_input(
        image_path_raw=str(attachment.get("image_path") or "").strip(),
        source_name=attachment.get("source_name"),
        mime_type=attachment.get("mime_type"),
        text_hint=attachment.get("text_hint"),
        placeholder_bytes=ONE_BY_ONE_PNG_BYTES,
        placeholder_mime_type="image/png",
        placeholder_source_name="ocr-recovery-template.png",
        file_fallback_mime_type="application/octet-stream",
    )
    return (
        build_data_url(raw_bytes=raw_bytes, mime_type=mime_type),
        mime_type,
        source_name,
        text_hint,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run OCR ambiguity/recovery eval cases via /chat."
    )
    parser.add_argument(
        "--base-url", default="http://127.0.0.1:8000", help="Polinko API base URL."
    )
    parser.add_argument(
        "--cases",
        default="docs/eval/beta_2_0/ocr_recovery_eval_cases.json",
        help="Path to OCR recovery eval cases JSON file.",
    )
    parser.add_argument(
        "--session-prefix",
        default="ocr-recovery-eval",
        help="Session id prefix for generated eval chats.",
    )
    parser.add_argument("--run-id", default="", help="Optional run id suffix.")
    parser.add_argument(
        "--timeout", type=int, default=90, help="HTTP timeout in seconds."
    )
    parser.add_argument(
        "--strict", action="store_true", help="Exit non-zero if any case fails."
    )
    parser.add_argument(
        "--keep-chats", action="store_true", help="Keep generated eval chats."
    )
    parser.add_argument(
        "--show-text", action="store_true", help="Print assistant text for each step."
    )
    parser.add_argument(
        "--report-json", default="", help="Optional JSON report output path."
    )
    parser.add_argument(
        "--trace-jsonl",
        default=str(DEFAULT_TRACE_JSONL),
        help="Append-only JSONL trace artifact path (set empty string to disable).",
    )
    return parser


def main() -> int:
    load_dotenv(dotenv_path=".env")
    args = build_parser().parse_args()

    cases_path = Path(args.cases)
    if not cases_path.exists():
        raise SystemExit(f"Cases file not found: {cases_path}")

    headers = _headers()
    run_id = str(args.run_id or "").strip() or str(int(time.time()))
    cases = _load_cases(cases_path)

    print(f"Running OCR recovery eval on {args.base_url}")
    print(f"Cases: {len(cases)} | run_id={run_id}")

    try:
        _preflight(args.base_url, headers, args.timeout)
    except Exception as exc:
        print(f"Preflight failed: {exc}")
        return 2

    total_failures = 0
    total_errors = 0
    session_ids: list[str] = []
    case_reports: list[dict[str, Any]] = []

    for index, case in enumerate(cases, start=1):
        case_id = case["id"]
        session_id = f"{args.session_prefix}-{run_id}-{index:02d}"
        session_ids.append(session_id)
        print(f"\nCase {index}/{len(cases)}: {case_id}")

        case_status = "PASS"
        case_error = ""
        step_reports: list[dict[str, Any]] = []

        try:
            _create_chat(args.base_url, headers, session_id, args.timeout)
            data_base64, mime_type, source_name, text_hint = _read_attachment_payload(
                case["attachment"]
            )
            visual_context_hint = case["attachment"].get("visual_context_hint")

            seed_attachments: list[dict[str, Any]] = [
                build_chat_attachment(
                    data_base64=data_base64,
                    mime_type=mime_type,
                    source_name=source_name,
                    text_hint=text_hint,
                    visual_context_hint=visual_context_hint,
                )
            ]

            first_resp = _send_chat(
                base_url=args.base_url,
                headers=headers,
                session_id=session_id,
                message=case["seed_prompt"],
                attachments=seed_attachments,
                timeout=args.timeout,
            )
            first_text = str(first_resp.get("output", "")).strip()
            seed_step = case["steps"][0]
            seed_ok, seed_reasons = _check_constraints(seed_step, first_text)
            step_reports.append(
                {
                    "step_id": seed_step["id"],
                    "prompt": case["seed_prompt"],
                    "assistant": first_text,
                    "status": "PASS" if seed_ok else "FAIL",
                    "reasons": seed_reasons,
                }
            )
            if args.show_text:
                print(f"  seed_text: {first_text!r}")
            if not seed_ok:
                case_status = "FAIL"
                total_failures += 1

            for step in case["steps"][1:]:
                prompt = str(step["user"] or "").strip()
                if not prompt:
                    continue
                followup = _send_chat(
                    base_url=args.base_url,
                    headers=headers,
                    session_id=session_id,
                    message=prompt,
                    attachments=seed_attachments if step["attach_image"] else None,
                    timeout=args.timeout,
                )
                followup_text = str(followup.get("output", "")).strip()
                ok, reasons = _check_constraints(step, followup_text)
                if args.show_text:
                    print(f"  {step['id']}: {followup_text!r}")
                step_reports.append(
                    {
                        "step_id": step["id"],
                        "prompt": prompt,
                        "assistant": followup_text,
                        "status": "PASS" if ok else "FAIL",
                        "reasons": reasons,
                    }
                )
                if not ok and case_status != "FAIL":
                    case_status = "FAIL"
                    total_failures += 1

        except Exception as exc:
            case_status = "ERROR"
            case_error = str(exc)
            total_errors += 1
            total_failures += 1
            print(f"  [ERROR] {exc}")

        print(f"  [{case_status}] steps={len(step_reports)}")
        for step in step_reports:
            if step["status"] != "PASS":
                print(f"    - {step['step_id']}: {'; '.join(step['reasons'])}")

        gate_decision = resolve_fail_closed_status(
            status=case_status,
            detail=case_error,
        )
        case_reports.append(
            {
                "id": case_id,
                "session_id": session_id,
                "status": case_status,
                "error": case_error,
                "gate_outcome": gate_decision.outcome,
                "gate_reasons": list(gate_decision.reasons),
                "labeling_guidance": case.get("labeling_guidance"),
                "steps": step_reports,
            }
        )

    if not args.keep_chats:
        for session_id in session_ids:
            try:
                _delete_chat(args.base_url, headers, session_id, args.timeout)
            except Exception as exc:
                print(f"  WARN cleanup failed for {session_id}: {exc}")

    passed = len(cases) - total_failures
    print("\nSummary")
    print(f"  Passed: {passed}/{len(cases)}")
    print(f"  Failed: {total_failures}")
    print(f"  Errors: {total_errors}")

    report_path = str(args.report_json or "").strip()
    if report_path:
        gate_passed, gate_failed = gate_counts_from_case_results(case_reports)
        output_path = Path(report_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        report_payload = {
            "run_id": run_id,
            "base_url": args.base_url,
            "cases_path": str(cases_path),
            "summary": {
                "total": len(cases),
                "passed": passed,
                "failed": total_failures,
                "errors": total_errors,
                "gate_passed": gate_passed,
                "gate_failed": gate_failed,
            },
            "cases": case_reports,
            "generated_at": int(time.time()),
        }
        output_path.write_text(
            json.dumps(report_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"  Report: {output_path}")
        trace_jsonl = str(args.trace_jsonl or "").strip()
        if trace_jsonl:
            trace_payload = build_eval_trace(
                run_id=run_id,
                tool_name="tools/eval_ocr_recovery.py",
                source_artifacts={
                    "report_json": str(output_path),
                    "cases_path": str(cases_path),
                },
                gate_outcomes=[
                    {
                        "name": "ocr_recovery_eval",
                        "passed": gate_failed == 0,
                        "detail": (
                            f"passed={passed}/{len(cases)}, "
                            f"failed={total_failures}, errors={total_errors}, "
                            f"gate_failed={gate_failed}"
                        ),
                    }
                ],
                summary=report_payload["summary"],
                metadata={
                    "base_url": args.base_url,
                    "strict": bool(args.strict),
                },
            )
            trace_path = append_eval_trace(
                trace_payload=trace_payload,
                trace_jsonl_path=Path(trace_jsonl),
            )
            print(f"  Trace: {trace_path}")

    if total_failures > 0 and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
