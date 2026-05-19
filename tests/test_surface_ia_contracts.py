import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


class SurfaceIaContractTests(unittest.TestCase):
    def test_current_and_target_surface_paths_are_documented(self) -> None:
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

    def test_ambiguous_legacy_surface_paths_are_not_active_directories(self) -> None:
        self.assertFalse((REPO_ROOT / "frontend").exists())
        self.assertFalse((REPO_ROOT / "ui").exists())

    def test_tracked_portfolio_static_output_lives_under_public_portfolio(self) -> None:
        self.assertTrue((REPO_ROOT / "public" / "portfolio" / "index.html").is_file())
        self.assertTrue((REPO_ROOT / "public" / "portfolio" / "assets").is_dir())

    def test_current_portfolio_source_output_and_server_paths_align(self) -> None:
        makefile = _read("Makefile")
        make_config = _read("makefiles/config.mk")
        surfaces_make = _read("makefiles/surfaces.mk")
        vite_config = _read("apps/portfolio/vite.config.js")
        static_builder = _read("tools/build_portfolio_static.py")
        app_factory = _read("api/app_factory.py")

        self.assertIn("include makefiles/config.mk", makefile)
        self.assertIn("FRONTEND_DIR ?= apps/portfolio", make_config)
        self.assertIn("PORTFOLIO_APP_DIR ?= $(FRONTEND_DIR)", make_config)
        self.assertIn("PORTFOLIO_STATIC_DIR ?= public/portfolio", make_config)
        self.assertIn("PORTFOLIO_MOCKUP_DIR ?= docs/peanut/assets/portfolio-mockups", make_config)
        self.assertIn("portfolio-app-install:", surfaces_make)
        self.assertIn("frontend-install: portfolio-app-install", surfaces_make)
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


if __name__ == "__main__":
    unittest.main()
