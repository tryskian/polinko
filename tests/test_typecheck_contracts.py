import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


class TypecheckContractTests(unittest.TestCase):
    def test_mypy_target_uses_active_source_and_tool_surface(self) -> None:
        config = _read("mypy.ini")
        checks_makefile = _read("makefiles/checks.mk")

        self.assertIn("files = src, tools", config)
        self.assertIn("docs/eval/", config)
        self.assertIn("docs/peanut/", config)
        self.assertIn("tests/", config)
        self.assertIn("type-check:", checks_makefile)
        self.assertIn("$(PYTHON) -m mypy --config-file mypy.ini", checks_makefile)

    def test_typecheck_is_part_of_ci_and_closeout(self) -> None:
        build_makefile = _read("makefiles/build.mk")
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
            'run_step "end-git-check" make --no-print-directory end-git-check',
            closeout,
        )
        self.assertGreater(
            closeout.index('run_step "end-git-check"'),
            closeout.index('run_step "security-checks"'),
        )
        self.assertIn("expected branch $BRANCH", git_check)
        self.assertIn("rerunning make end", git_check)
        self.assertIn("current branch must be `main`", start_reference)
        self.assertIn("skips final clean-main Git closeout", start_reference)

    def test_runbook_make_end_summary_matches_closeout_order(self) -> None:
        runbook = _read("docs/runtime/RUNBOOK.md")

        self.assertIn("background-stop, and final clean-main", runbook)
        self.assertNotIn("clean-main Git check, transcript", runbook)

    def test_pyright_is_repo_owned_advisory_editor_check(self) -> None:
        package = json.loads(_read("package.json"))
        checks_makefile = _read("makefiles/checks.mk")
        build_makefile = _read("makefiles/build.mk")
        ci_workflow = _read(".github/workflows/ci.yml")
        state = _read("docs/governance/STATE.md")

        self.assertEqual(package["devDependencies"]["pyright"], "1.1.410")
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
