import argparse
from collections import defaultdict
import json
import os
import sys
import time
from collections.abc import Callable
from typing import Any
import urllib.error
import urllib.parse
import urllib.request

DotenvLoader = Callable[..., bool]

try:
    from dotenv import load_dotenv as _load_dotenv
except ImportError:  # pragma: no cover - dotenv is part of the app env.
    load_dotenv: DotenvLoader | None = None
else:
    load_dotenv = _load_dotenv


API_BASE_URL = "https://api.openai.com/v1"
USAGE_KINDS = {
    "audio_speeches",
    "audio_transcriptions",
    "code_interpreter_sessions",
    "completions",
    "embeddings",
    "file_search_calls",
    "images",
    "moderations",
    "vector_stores",
    "web_search_calls",
}
USAGE_FIELD_ORDER = (
    "num_model_requests",
    "input_tokens",
    "output_tokens",
    "input_cached_tokens",
    "input_audio_tokens",
    "output_audio_tokens",
    "num_sessions",
    "usage_bytes",
    "images",
    "seconds",
)
RATE_LIMIT_FIELD_ORDER = (
    "max_requests_per_1_minute",
    "max_tokens_per_1_minute",
    "max_requests_per_1_day",
    "max_images_per_1_minute",
    "max_audio_megabytes_per_1_minute",
    "batch_1_day_max_input_tokens",
)


def _env(name: str, default: str) -> str:
    raw_value = os.getenv(name)
    if raw_value is None or not raw_value.strip():
        return default
    normalized = raw_value.strip()
    if (
        len(normalized) >= 2
        and normalized[0] == normalized[-1]
        and normalized[0] in {'"', "'"}
    ):
        return normalized[1:-1].strip()
    return normalized


def _env_int(name: str, default: int) -> int:
    value = _env(name, str(default))
    try:
        parsed = int(value)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer.") from exc
    if parsed < 1:
        raise RuntimeError(f"{name} must be >= 1.")
    return parsed


def _env_float(name: str, default: float) -> float:
    value = _env(name, str(default))
    try:
        parsed = float(value)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be a number.") from exc
    if parsed <= 0:
        raise RuntimeError(f"{name} must be > 0.")
    return parsed


def _csv_values(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def _admin_key(env_name: str) -> str:
    if load_dotenv is not None:
        load_dotenv(dotenv_path=".env")
    value = _env(env_name, "")
    if not value:
        raise RuntimeError(
            f"{env_name} is required for OpenAI organization usage, costs, "
            "and rate-limit summary targets."
        )
    return value


def _format_number(value: float) -> str:
    if value == int(value):
        return f"{int(value):,}"
    return f"{value:,.4f}".rstrip("0").rstrip(".")


def _request_json(
    *,
    args: argparse.Namespace,
    path: str,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    admin_key = _admin_key(args.admin_key_env)
    query = urllib.parse.urlencode(params or {}, doseq=True)
    url = f"{args.base_url.rstrip('/')}/{path.lstrip('/')}"
    if query:
        url = f"{url}?{query}"
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {admin_key}",
            "Content-Type": "application/json",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            status = getattr(response, "status", 200)
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        status = exc.code
        body = exc.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"OpenAI API request failed: {exc.reason}") from exc
    if status < 200 or status >= 300:
        detail = body.strip()[:500]
        suffix = f": {detail}" if detail else ""
        raise RuntimeError(f"OpenAI API request failed: HTTP {status}{suffix}")
    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise RuntimeError("OpenAI API returned non-JSON response.") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("OpenAI API returned an unexpected JSON shape.")
    return payload


def _collect_page_data(
    *,
    args: argparse.Namespace,
    path: str,
    params: dict[str, Any],
) -> dict[str, Any]:
    collected: list[Any] = []
    current_params = dict(params)
    pages = 0
    latest_payload: dict[str, Any] = {}
    while True:
        pages += 1
        if pages > 20:
            raise RuntimeError("OpenAI API pagination exceeded 20 pages.")
        latest_payload = _request_json(args=args, path=path, params=current_params)
        data = latest_payload.get("data", [])
        if not isinstance(data, list):
            raise RuntimeError("OpenAI API page did not include a data list.")
        collected.extend(data)
        next_page = latest_payload.get("next_page")
        if not latest_payload.get("has_more") or not isinstance(next_page, str):
            break
        current_params["page"] = next_page
    latest_payload["data"] = collected
    latest_payload["has_more"] = False
    return latest_payload


def _collect_list_data(
    *,
    args: argparse.Namespace,
    path: str,
    params: dict[str, Any],
) -> dict[str, Any]:
    collected: list[Any] = []
    current_params = dict(params)
    pages = 0
    latest_payload: dict[str, Any] = {}
    while True:
        pages += 1
        if pages > 20:
            raise RuntimeError("OpenAI API pagination exceeded 20 pages.")
        latest_payload = _request_json(args=args, path=path, params=current_params)
        data = latest_payload.get("data", [])
        if not isinstance(data, list):
            raise RuntimeError("OpenAI API list did not include a data list.")
        collected.extend(data)
        last_id = latest_payload.get("last_id")
        if not latest_payload.get("has_more") or not isinstance(last_id, str):
            break
        current_params["after"] = last_id
    latest_payload["data"] = collected
    latest_payload["has_more"] = False
    return latest_payload


def _time_params(*, days: int, bucket_width: str, group_by: str) -> dict[str, Any]:
    end_time = int(time.time())
    params: dict[str, Any] = {
        "start_time": end_time - (days * 24 * 60 * 60),
        "end_time": end_time,
        "bucket_width": bucket_width,
    }
    groups = _csv_values(group_by)
    if groups:
        params["group_by"] = groups
    return params


def _iter_results(buckets: list[Any]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for bucket in buckets:
        if not isinstance(bucket, dict):
            continue
        bucket_results = bucket.get("results", [])
        if not isinstance(bucket_results, list):
            continue
        for result in bucket_results:
            if isinstance(result, dict):
                results.append(result)
    return results


def _print_costs(payload: dict[str, Any], *, days: int) -> None:
    buckets = payload.get("data", [])
    if not isinstance(buckets, list):
        buckets = []

    totals: defaultdict[str, float] = defaultdict(float)
    for result in _iter_results(buckets):
        amount = result.get("amount", {})
        if not isinstance(amount, dict):
            continue
        value = amount.get("value")
        currency = str(amount.get("currency") or "unknown").upper()
        if isinstance(value, int | float) and not isinstance(value, bool):
            totals[currency] += float(value)

    print(f"OpenAI costs: last {days}d")
    if not totals:
        print("  No cost rows returned.")
        return
    for currency, value in sorted(totals.items()):
        print(f"  {currency}: {_format_number(value)}")


def _print_usage(payload: dict[str, Any], *, kind: str, days: int) -> None:
    buckets = payload.get("data", [])
    if not isinstance(buckets, list):
        buckets = []

    totals: defaultdict[str, float] = defaultdict(float)
    for result in _iter_results(buckets):
        for key, value in result.items():
            if isinstance(value, int | float) and not isinstance(value, bool):
                totals[key] += float(value)

    print(f"OpenAI usage: {kind} last {days}d")
    if not totals:
        print("  No usage rows returned.")
        return
    seen: set[str] = set()
    for field in USAGE_FIELD_ORDER:
        if field in totals:
            print(f"  {field}: {_format_number(totals[field])}")
            seen.add(field)
    for field in sorted(set(totals) - seen):
        print(f"  {field}: {_format_number(totals[field])}")


def _print_limits(payload: dict[str, Any], *, project_id: str) -> None:
    rows = payload.get("data", [])
    if not isinstance(rows, list):
        rows = []

    print(f"OpenAI project limits: {project_id}")
    if not rows:
        print("  No project rate limits returned.")
        return
    for row in rows:
        if not isinstance(row, dict):
            continue
        model = row.get("model") or row.get("id") or "unknown"
        parts = []
        for field in RATE_LIMIT_FIELD_ORDER:
            value = row.get(field)
            if isinstance(value, int | float) and not isinstance(value, bool):
                parts.append(f"{field}={_format_number(float(value))}")
        suffix = ", ".join(parts) if parts else "no numeric limits returned"
        print(f"  {model}: {suffix}")


def _emit(payload: dict[str, Any], *, json_output: bool, printer: Any) -> None:
    if json_output:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        printer(payload)


def run_costs(args: argparse.Namespace) -> int:
    params = _time_params(
        days=args.days,
        bucket_width=args.bucket_width,
        group_by=args.group_by,
    )
    payload = _collect_page_data(args=args, path="/organization/costs", params=params)
    _emit(
        payload,
        json_output=args.json,
        printer=lambda item: _print_costs(item, days=args.days),
    )
    return 0


def run_usage(args: argparse.Namespace) -> int:
    if args.kind not in USAGE_KINDS:
        allowed = ", ".join(sorted(USAGE_KINDS))
        raise RuntimeError(
            f"Unsupported usage kind '{args.kind}'. Use one of: {allowed}."
        )
    params = _time_params(
        days=args.days,
        bucket_width=args.bucket_width,
        group_by=args.group_by,
    )
    payload = _collect_page_data(
        args=args,
        path=f"/organization/usage/{args.kind}",
        params=params,
    )
    _emit(
        payload,
        json_output=args.json,
        printer=lambda item: _print_usage(item, kind=args.kind, days=args.days),
    )
    return 0


def run_limits(args: argparse.Namespace) -> int:
    project_id = args.project_id.strip()
    if not project_id:
        raise RuntimeError("OPENAI_PROJECT_ID or --project-id is required for limits.")
    payload = _collect_list_data(
        args=args,
        path=f"/organization/projects/{project_id}/rate_limits",
        params={"limit": args.limit},
    )
    _emit(
        payload,
        json_output=args.json,
        printer=lambda item: _print_limits(item, project_id=project_id),
    )
    return 0


def run_summary(args: argparse.Namespace) -> int:
    cost_params = _time_params(
        days=args.cost_days,
        bucket_width=args.cost_bucket_width,
        group_by=args.cost_group_by,
    )
    cost_payload = _collect_page_data(
        args=args, path="/organization/costs", params=cost_params
    )

    usage_args = argparse.Namespace(**vars(args))
    usage_args.days = args.usage_days
    usage_args.bucket_width = args.usage_bucket_width
    usage_args.group_by = args.usage_group_by
    usage_args.kind = args.usage_kind
    if usage_args.kind not in USAGE_KINDS:
        allowed = ", ".join(sorted(USAGE_KINDS))
        raise RuntimeError(
            f"Unsupported usage kind '{usage_args.kind}'. Use one of: {allowed}."
        )
    usage_params = _time_params(
        days=usage_args.days,
        bucket_width=usage_args.bucket_width,
        group_by=usage_args.group_by,
    )
    usage_payload = _collect_page_data(
        args=args,
        path=f"/organization/usage/{usage_args.kind}",
        params=usage_params,
    )

    if args.json:
        payload: dict[str, Any] = {
            "costs": cost_payload,
            "usage": usage_payload,
        }
        project_id = args.project_id.strip()
        if project_id:
            payload["limits"] = _collect_list_data(
                args=args,
                path=f"/organization/projects/{project_id}/rate_limits",
                params={"limit": args.limit},
            )
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    _print_costs(cost_payload, days=args.cost_days)
    print("")
    _print_usage(usage_payload, kind=usage_args.kind, days=args.usage_days)
    project_id = args.project_id.strip()
    if project_id:
        print("")
        limits_payload = _collect_list_data(
            args=args,
            path=f"/organization/projects/{project_id}/rate_limits",
            params={"limit": args.limit},
        )
        _print_limits(limits_payload, project_id=project_id)
    else:
        print("")
        print("OpenAI project limits: skipped (set OPENAI_PROJECT_ID).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Print OpenAI organization usage, costs, and project limits."
    )
    parser.add_argument("--base-url", default=_env("OPENAI_API_BASE_URL", API_BASE_URL))
    parser.add_argument(
        "--admin-key-env", default=_env("OPENAI_ADMIN_KEY_ENV", "OPENAI_ADMIN_KEY")
    )
    parser.add_argument(
        "--timeout", type=float, default=_env_float("OPENAI_ACCOUNT_TIMEOUT", 30.0)
    )
    parser.add_argument("--json", action="store_true", help="Print raw JSON payloads.")

    subparsers = parser.add_subparsers(dest="command", required=True)

    costs = subparsers.add_parser("costs", help="Print organization costs.")
    costs.add_argument("--days", type=int, default=_env_int("OPENAI_COST_DAYS", 30))
    costs.add_argument("--bucket-width", default=_env("OPENAI_COST_BUCKET_WIDTH", "1d"))
    costs.add_argument("--group-by", default=_env("OPENAI_COST_GROUP_BY", ""))
    costs.set_defaults(func=run_costs)

    usage = subparsers.add_parser("usage", help="Print organization usage.")
    usage.add_argument("--kind", default=_env("OPENAI_USAGE_KIND", "completions"))
    usage.add_argument("--days", type=int, default=_env_int("OPENAI_USAGE_DAYS", 7))
    usage.add_argument(
        "--bucket-width", default=_env("OPENAI_USAGE_BUCKET_WIDTH", "1d")
    )
    usage.add_argument("--group-by", default=_env("OPENAI_USAGE_GROUP_BY", ""))
    usage.set_defaults(func=run_usage)

    limits = subparsers.add_parser("limits", help="Print project rate limits.")
    limits.add_argument("--project-id", default=_env("OPENAI_PROJECT_ID", ""))
    limits.add_argument(
        "--limit", type=int, default=_env_int("OPENAI_LIMITS_PAGE_SIZE", 100)
    )
    limits.set_defaults(func=run_limits)

    summary = subparsers.add_parser("summary", help="Print account summary.")
    summary.add_argument(
        "--cost-days", type=int, default=_env_int("OPENAI_COST_DAYS", 30)
    )
    summary.add_argument(
        "--cost-bucket-width", default=_env("OPENAI_COST_BUCKET_WIDTH", "1d")
    )
    summary.add_argument("--cost-group-by", default=_env("OPENAI_COST_GROUP_BY", ""))
    summary.add_argument(
        "--usage-kind", default=_env("OPENAI_USAGE_KIND", "completions")
    )
    summary.add_argument(
        "--usage-days", type=int, default=_env_int("OPENAI_USAGE_DAYS", 7)
    )
    summary.add_argument(
        "--usage-bucket-width", default=_env("OPENAI_USAGE_BUCKET_WIDTH", "1d")
    )
    summary.add_argument("--usage-group-by", default=_env("OPENAI_USAGE_GROUP_BY", ""))
    summary.add_argument("--project-id", default=_env("OPENAI_PROJECT_ID", ""))
    summary.add_argument(
        "--limit", type=int, default=_env_int("OPENAI_LIMITS_PAGE_SIZE", 100)
    )
    summary.set_defaults(func=run_summary)

    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
        return args.func(args)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
