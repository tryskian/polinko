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
        vite_config = _read("frontend/vite.config.js")
        static_builder = _read("tools/build_portfolio_static.py")
        app_factory = _read("api/app_factory.py")

        self.assertIn("FRONTEND_DIR ?= frontend", makefile)
        self.assertIn('path.resolve(process.cwd(), "../ui")', vite_config)
        self.assertIn('FRONTEND_DIR = REPO_ROOT / "frontend"', static_builder)
        self.assertIn('UI_DIR = REPO_ROOT / "ui"', static_builder)
        self.assertIn('/ "ui"', app_factory)


if __name__ == "__main__":
    unittest.main()
