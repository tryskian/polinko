import json
import re
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents import Runner
from openai import APIConnectionError, APIStatusError, AuthenticationError, RateLimitError

from config import load_config
from core.runtime import create_agent, create_run_config
from core.prompts import ACTIVE_PROMPT_VERSION


def _count_words(text: str) -> int:
    return len(text.split())


def _matches_needle(text: str, needle: str) -> bool:
    lower_text = text.lower()
    lower_needle = needle.lower()
    # Treat single-token needles as whole words to avoid false positives
    # (e.g. "our" should not match "your").
    if " " not in lower_needle and re.fullmatch(r"[a-z][a-z'-]*", lower_needle):
        pattern = rf"\b{re.escape(lower_needle)}\b"
        return re.search(pattern, lower_text) is not None
    return lower_needle in lower_text


def _contains_all(text: str, needles: list[str]) -> list[str]:
    missing = []
    for needle in needles:
        if not _matches_needle(text, needle):
            missing.append(needle)
    return missing


def _contains_any(text: str, needles: list[str]) -> list[str]:
    found = []
    for needle in needles:
        if _matches_needle(text, needle):
            found.append(needle)
    return found


def _load_cases(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("cases", [])


def main() -> int:
    try:
        load_config(dotenv_path=".env")
    except RuntimeError as exc:
        print(str(exc))
        return 1

    cases_path = Path("configs/golden_prompts.json")
    if not cases_path.exists():
        print("Missing configs/golden_prompts.json")
        return 1

    cases = _load_cases(cases_path)
    if not cases:
        print("No cases found in configs/golden_prompts.json")
        return 1

    agent = create_agent()
    run_config = create_run_config(store=False)

    print(f"Running {len(cases)} regression checks with prompt {ACTIVE_PROMPT_VERSION}")
    failures = 0

    for case in cases:
        case_id = case.get("id", "unnamed_case")
        prompt = case.get("input", "")
        must_include = case.get("must_include", [])
        must_include_any = case.get("must_include_any", [])
        must_not_include = case.get("must_not_include", [])
        max_words = case.get("max_words")

        print(f"\n--- {case_id} ---")

        try:
            result = Runner.run_sync(agent, prompt, run_config=run_config)
        except AuthenticationError:
            print("FAIL: authentication error")
            failures += 1
            continue
        except RateLimitError:
            print("FAIL: rate limit error")
            failures += 1
            continue
        except APIConnectionError:
            print("FAIL: connection error")
            failures += 1
            continue
        except APIStatusError as exc:
            print(f"FAIL: API status error {exc.status_code}")
            failures += 1
            continue

        output = str(result.final_output).strip()
        output_words = _count_words(output)

        missing = _contains_all(output, must_include)
        found_required_any = _contains_any(output, must_include_any)
        missing_any = bool(must_include_any) and not found_required_any
        found_forbidden = _contains_any(output, must_not_include)
        too_long = isinstance(max_words, int) and output_words > max_words

        case_failed = bool(missing or missing_any or found_forbidden or too_long)
        if case_failed:
            failures += 1
            print("FAIL")
            if missing:
                print(f"  Missing required text: {missing}")
            if missing_any:
                print(f"  Missing one-of required text: {must_include_any}")
            if found_forbidden:
                print(f"  Contains forbidden text: {found_forbidden}")
            if too_long:
                print(f"  Too long: {output_words} words (limit {max_words})")
        else:
            print("PASS")

        print(f"Output ({output_words} words): {output}")

    print("\n=== Summary ===")
    print(f"Failures: {failures} / {len(cases)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
