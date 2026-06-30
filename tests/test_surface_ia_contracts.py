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
    def test_portfolio_surfaces_are_archived_for_porting(self) -> None:
        surface_ia = _read("docs/runtime/SURFACE_IA.md")
        make_config = _read_make_source("makefiles/config.mk")
        surfaces_make = _read_make_source("makefiles/surfaces.mk")
        app_factory = _read("src/polinko/api/app_factory.py")
        dependabot = _read(".github/dependabot.yml")
        precommit = _read(".pre-commit-config.yaml")

        self.assertIn(".archive/quarantine/portfolio-2026-06-29/", surface_ia)
        for token in (
            "`apps/portfolio/`",
            "`public/portfolio/`",
            "`/portfolio`",
            "`make portfolio`",
            "archived portfolio static builder helper",
            "archived portfolio mockup runner helper",
            "`netlify.toml`",
        ):
            self.assertIn(token, surface_ia)

        for archive_only_token in (
            "PORTFOLIO_APP_DIR",
            "PORTFOLIO_STATIC_DIR",
            "POLINKO_PORTFOLIO_STATIC_DIR",
            "portfolio-build",
            "portfolio-mockups",
            'directory: "/apps/portfolio"',
            "public/portfolio/assets",
        ):
            self.assertNotIn(archive_only_token, make_config + surfaces_make)
            self.assertNotIn(archive_only_token, dependabot + precommit)

        self.assertNotIn('"/portfolio"', app_factory)
        self.assertNotIn('"/assets"', app_factory)

    def test_archive_surface_paths_are_absent_from_active_web_directories(
        self,
    ) -> None:
        self.assertFalse((REPO_ROOT / "frontend").exists())
        self.assertFalse((REPO_ROOT / "ui").exists())
        self.assertFalse((REPO_ROOT / "apps" / "portfolio" / "package.json").exists())
        self.assertFalse((REPO_ROOT / "public" / "portfolio" / "index.html").exists())

    def test_evidence_sankey_helper_stays_active(self) -> None:
        surface_ia = _read("docs/runtime/SURFACE_IA.md")
        renderer = _read("tools/render_public_d3_diagrams.py")

        self.assertIn("src/polinko/api/evidence_sankey.py", surface_ia)
        self.assertIn("build_evidence_sankey_payload", renderer)
        self.assertNotIn("portfolio_sankey", renderer)

    def test_manual_eval_workbench_scope_is_documented(self) -> None:
        surface_ia = _read("docs/runtime/SURFACE_IA.md")

        for expected in (
            "The manual eval workbench is the human-judged research workspace",
            "`make notes`",
            "`make notebook`",
            "`make nb`",
            "`.local/notebooks/`",
            "`.local/runtime_dbs/active/manual_evals.db`",
            "`.local/runtime_dbs/active/history.db`",
            "`POST /chat`",
            "`/chats/*`",
            "Automated eval reports, strict OCR gates, and tracked beta snapshots",
            "Chat-facing manual eval routes stay in the API workbench",
        ):
            self.assertIn(expected, surface_ia)

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
