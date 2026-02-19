import json
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from agents import Agent, ModelSettings, RunConfig, Runner
from openai import APIConnectionError, APIStatusError, AuthenticationError, RateLimitError

from prompts import ACTIVE_PROMPT, ACTIVE_PROMPT_VERSION


def _count_words(text: str) -> int:
    return len(text.split())


def _contains_all(text: str, needles: list[str]) -> list[str]:
    lower_text = text.lower()
    missing = []
    for needle in needles:
        if needle.lower() not in lower_text:
            missing.append(needle)
    return missing


def _contains_any(text: str, needles: list[str]) -> list[str]:
    lower_text = text.lower()
    found = []
    for needle in needles:
        if needle.lower() in lower_text:
            found.append(needle)
    return found


def _load_cases(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("cases", [])


def main() -> int:
    load_dotenv(dotenv_path=".env")
    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY is not set.")
        return 1

    cases_path = Path("golden_prompts.json")
    if not cases_path.exists():
        print("Missing golden_prompts.json")
        return 1

    cases = _load_cases(cases_path)
    if not cases:
        print("No cases found in golden_prompts.json")
        return 1

    agent = Agent(
        name="Polinko Repositining System",
        instructions=ACTIVE_PROMPT,
        model="gpt-5-chat-latest",
    )
    run_config = RunConfig(
        model_settings=ModelSettings(
            temperature=1.0,
            top_p=1.0,
            store=False,
        )
    )

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
