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
            "docs/peanut/assets/tumbles/portfolio/",
            "apps/portfolio/",
            "public/portfolio/",
            "docs/peanut/assets/portfolio-mockups/",
        ):
            self.assertIn(path, surface_ia)

    def test_current_portfolio_source_output_and_server_paths_align(self) -> None:
        makefile = _read("Makefile")
        surfaces_make = _read("makefiles/surfaces.mk")
        vite_config = _read("frontend/vite.config.js")
        static_builder = _read("tools/build_portfolio_static.py")
        app_factory = _read("api/app_factory.py")

        self.assertIn("FRONTEND_DIR ?= frontend", makefile)
        self.assertIn("PORTFOLIO_APP_DIR ?= $(FRONTEND_DIR)", makefile)
        self.assertIn("PORTFOLIO_STATIC_DIR ?= ui", makefile)
        self.assertIn("$(PORTFOLIO_APP_DIR)/package.json", surfaces_make)
        self.assertIn("POLINKO_PORTFOLIO_STATIC_DIR", surfaces_make)
        self.assertIn("$(PORTFOLIO_STATIC_DIR)", surfaces_make)
        self.assertIn("POLINKO_PORTFOLIO_STATIC_DIR", vite_config)
        self.assertIn('path.resolve(__dirname, "../ui")', vite_config)
        self.assertIn(
            'PORTFOLIO_APP_DIR = _repo_path_from_env("POLINKO_PORTFOLIO_APP_DIR", "frontend")',
            static_builder,
        )
        self.assertIn(
            'PORTFOLIO_STATIC_DIR = _repo_path_from_env("POLINKO_PORTFOLIO_STATIC_DIR", "ui")',
            static_builder,
        )
        self.assertIn(
            'portfolio_static_dir = _repo_path_from_env("POLINKO_PORTFOLIO_STATIC_DIR", "ui")',
            app_factory,
        )


if __name__ == "__main__":
    unittest.main()
