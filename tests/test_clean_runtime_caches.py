import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from tools import clean_runtime_caches


class CleanRuntimeCachesTests(unittest.TestCase):
    def test_lists_repo_owned_cache_dirs_outside_vendor_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for cache_path in [
                root / "__pycache__",
                root / "src" / "polinko" / "__pycache__",
                root / ".pytest_cache",
                root / ".venv" / "lib" / "__pycache__",
                root / "node_modules" / "pkg" / "__pycache__",
            ]:
                cache_path.mkdir(parents=True)

            found = [
                clean_runtime_caches.repo_relative(path, root=root)
                for path in clean_runtime_caches.iter_runtime_cache_dirs(root)
            ]

        self.assertEqual(
            found, [".pytest_cache", "__pycache__", "src/polinko/__pycache__"]
        )

    def test_apply_removes_repo_owned_cache_dirs_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "tests" / "__pycache__"
            vendor = root / ".venv" / "lib" / "__pycache__"
            target.mkdir(parents=True)
            vendor.mkdir(parents=True)

            removed = clean_runtime_caches.clean_runtime_caches(root=root, apply=True)

            self.assertEqual(
                [
                    clean_runtime_caches.repo_relative(path, root=root)
                    for path in removed
                ],
                ["tests/__pycache__"],
            )
            self.assertFalse(target.exists())
            self.assertTrue(vendor.exists())

    def test_default_cli_lists_cache_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".ruff_cache").mkdir()

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = clean_runtime_caches.main(["--root", str(root)])

        self.assertEqual(code, 0)
        self.assertIn(".ruff_cache", stdout.getvalue())
