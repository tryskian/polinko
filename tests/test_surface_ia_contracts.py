import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def _read_make_source(relative_path: str, seen: set[Path] | None = None) -> str:
    if seen is None:
        seen = set()
    path = (REPO_ROOT / relative_path).resolve()
    if path in seen:
        return ""
    seen.add(path)

    text = path.read_text(encoding="utf-8")
    source_texts = [text]
    for match in re.finditer(r"^include\s+(.+)$", text, re.MULTILINE):
        for include_path in match.group(1).split():
            source_texts.append(_read_make_source(include_path, seen))
    return "\n".join(source_texts)


class SurfaceIaContractTests(unittest.TestCase):
    def test_current_and_retired_surface_paths_are_documented(self) -> None:
        surface_ia = _read("docs/runtime/SURFACE_IA.md")

        for path in (
            "frontend/",
            "ui/",
            "apps/portfolio/",
            "public/portfolio/",
            "docs/peanut/assets/tumbles/portfolio/",
            "docs/peanut/assets/portfolio-mockups/",
        ):
            self.assertIn(path, surface_ia)

    def test_manual_eval_workbench_scope_is_documented(self) -> None:
        surface_ia = _read("docs/runtime/SURFACE_IA.md")

        for expected in (
            "The manual eval workbench is the human-judged research workspace",
            "`make notes`",
            "`make notebook`",
            "`make nb`",
            "`.local/runtime_dbs/active/manual_evals.db`",
            "`.local/runtime_dbs/active/history.db`",
            "`POST /chat`",
            "`/chats/*`",
            "Automated eval reports, strict OCR gates, and tracked beta snapshots",
            "Do not move chat-facing manual eval routes",
        ):
            self.assertIn(expected, surface_ia)

    def test_ambiguous_legacy_surface_paths_are_not_active_directories(self) -> None:
        self.assertFalse((REPO_ROOT / "frontend").exists())
        self.assertFalse((REPO_ROOT / "ui").exists())

    def test_tracked_portfolio_static_output_lives_under_public_portfolio(self) -> None:
        self.assertTrue((REPO_ROOT / "public" / "portfolio" / "index.html").is_file())
        self.assertTrue((REPO_ROOT / "public" / "portfolio" / "assets").is_dir())

    def test_current_portfolio_source_output_and_server_paths_align(self) -> None:
        makefile = _read("Makefile")
        make_config = _read_make_source("makefiles/config.mk")
        surfaces_make = _read("makefiles/surfaces.mk")
        vite_config = _read("apps/portfolio/vite.config.js")
        static_builder = _read("tools/build_portfolio_static.py")
        app_factory = _read("src/polinko/api/app_factory.py")

        self.assertIn("include makefiles/config.mk", makefile)
        self.assertIn("PORTFOLIO_APP_DIR ?= apps/portfolio", make_config)
        self.assertIn("PORTFOLIO_APP_DIR ?= $(FRONTEND_DIR)", make_config)
        self.assertIn("FRONTEND_DIR ?= $(PORTFOLIO_APP_DIR)", make_config)
        self.assertIn("PORTFOLIO_STATIC_DIR ?= public/portfolio", make_config)
        self.assertIn(
            "PORTFOLIO_MOCKUP_DIR ?= docs/peanut/assets/portfolio-mockups", make_config
        )
        self.assertIn("portfolio-install:", surfaces_make)
        self.assertIn(
            "portfolio-app-install frontend-install: portfolio-install", surfaces_make
        )
        self.assertIn("Legacy alias: use make portfolio-install.", surfaces_make)
        self.assertIn("Legacy alias: use make portfolio-build.", surfaces_make)
        self.assertIn("$(PORTFOLIO_APP_DIR)/package.json", surfaces_make)
        self.assertIn("POLINKO_PORTFOLIO_STATIC_DIR", surfaces_make)
        self.assertIn("$(PORTFOLIO_STATIC_DIR)", surfaces_make)
        self.assertIn("POLINKO_PORTFOLIO_STATIC_DIR", vite_config)
        self.assertIn('path.resolve(repoRoot, "public/portfolio")', vite_config)
        self.assertIn(
            'PORTFOLIO_APP_DIR = _repo_path_from_env("POLINKO_PORTFOLIO_APP_DIR", "apps/portfolio")',
            static_builder,
        )
        self.assertIn(
            '"public/portfolio"',
            static_builder,
        )
        self.assertIn(
            '"public/portfolio"',
            app_factory,
        )

    def test_manual_eval_trace_labels_are_not_ui_named(self) -> None:
        backfill = _read("tools/backfill_eval_trace_artifacts.py")

        self.assertIn(
            'tool_name="manual_eval_workbench/eval_submission"',
            backfill,
        )
        self.assertIn(
            '"manual_eval_workbench_submission"',
            backfill,
        )
        self.assertNotIn('"ui/eval_submission"', backfill)
        self.assertNotIn('"ui_eval_submission"', backfill)


if __name__ == "__main__":
    unittest.main()
