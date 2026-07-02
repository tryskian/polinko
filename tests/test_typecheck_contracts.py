import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def _read_makefile_source(relative_path: str, seen: set[Path] | None = None) -> str:
    if seen is None:
        seen = set()
    path = REPO_ROOT / relative_path
    resolved_path = path.resolve()
    if resolved_path in seen:
        return ""
    seen.add(resolved_path)

    text = path.read_text(encoding="utf-8")
    source_texts = [text]
    for line in text.splitlines():
        if line.startswith("include "):
            for include_path in line.removeprefix("include ").split():
                source_texts.append(_read_makefile_source(include_path, seen))
    return "\n".join(source_texts)


class TypecheckContractTests(unittest.TestCase):
    def test_mypy_target_uses_active_source_and_tool_surface(self) -> None:
        config = _read("mypy.ini")
        checks_makefile = _read_makefile_source("makefiles/checks.mk")

        self.assertIn("files = src, tools", config)
        self.assertIn("docs/eval/", config)
        self.assertIn("docs/peanut/", config)
        self.assertIn("tests/", config)
        self.assertIn("type-check:", checks_makefile)
        self.assertIn("$(PYTHON) -m mypy --config-file mypy.ini", checks_makefile)

    def test_typecheck_is_part_of_ci_and_closeout(self) -> None:
        build_makefile = _read_makefile_source("makefiles/build.mk")
        ci_workflow = _read(".github/workflows/ci.yml")
        closeout = _read("tools/end_of_day_routine.sh")
        state = _read("docs/governance/STATE.md")

        self.assertIn("ci-python-type-check", build_makefile)
        self.assertIn("python-type-check:", ci_workflow)
        self.assertIn("ci-python-type-check", closeout)
        self.assertIn("make type-check", state)

    def test_closeout_enforces_clean_synced_main_after_validation(self) -> None:
        closeout = _read("tools/end_of_day_routine.sh")
        git_check = _read("tools/check_end_git_clean.sh")
        start_reference = _read("docs/runtime/START_END_REFERENCE.md")

        self.assertIn("END_SKIP_GIT_CHECK", closeout)
        self.assertIn(
            'run_step "git-prune-stale-refs" make --no-print-directory git-prune-stale-refs',
            closeout,
        )
        self.assertIn(
            'run_step "github-health" make --no-print-directory github-health',
            closeout,
        )
        self.assertIn(
            'run_step "end-git-check" make --no-print-directory end-git-check',
            closeout,
        )
        self.assertGreater(
            closeout.index('run_step "git-prune-stale-refs"'),
            closeout.index('run_step "github-health"'),
        )
        self.assertGreater(
            closeout.index('run_step "github-health"'),
            closeout.index('"security-checks"'),
        )
        self.assertGreater(
            closeout.index('run_step "end-git-check"'),
            closeout.index('run_step "git-prune-stale-refs"'),
        )
        self.assertIn("expected branch $BRANCH", git_check)
        self.assertIn("rerunning make end", git_check)
        self.assertIn("current branch must be `main`", start_reference)
        self.assertIn(
            "leaves final clean-main Git closeout for the real session close",
            start_reference,
        )

    def test_runbook_make_end_summary_matches_closeout_order(self) -> None:
        runbook = _read("docs/runtime/RUNBOOK.md")

        self.assertIn("script/path checks, risk-scan", runbook)
        self.assertIn("`make end-stop`, GitHub health, stale-ref prune, and", runbook)
        self.assertIn("final clean-main Git check", runbook)
        self.assertNotIn("clean-main Git check, transcript", runbook)

    def test_pyright_is_repo_owned_advisory_editor_check(self) -> None:
        package = json.loads(_read("package.json"))
        package_lock = json.loads(_read("package-lock.json"))
        checks_makefile = _read_makefile_source("makefiles/checks.mk")
        build_makefile = _read_makefile_source("makefiles/build.mk")
        ci_workflow = _read(".github/workflows/ci.yml")
        state = _read("docs/governance/STATE.md")
        pyright_version = package["devDependencies"]["pyright"]

        self.assertEqual(
            package_lock["packages"][""]["devDependencies"]["pyright"],
            pyright_version,
        )
        self.assertEqual(
            package_lock["packages"]["node_modules/pyright"]["version"],
            pyright_version,
        )
        self.assertEqual(
            package["scripts"]["typecheck:pyright"],
            "pyright --project pyrightconfig.json",
        )
        self.assertIn("pyright-check:", checks_makefile)
        self.assertIn("npm run typecheck:pyright", checks_makefile)
        self.assertNotIn("ci-pyright", build_makefile)
        self.assertNotIn("pyright-check", ci_workflow)
        self.assertIn("advisory/editor check", state)


if __name__ == "__main__":
    unittest.main()
