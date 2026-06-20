import contextlib
import io
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools import path_leak_check


class PathLeakCheckTests(unittest.TestCase):
    def test_scan_file_reports_local_path_leak(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "sample.md"
            path.write_text("see /Users/alice/secret/file.txt\n", encoding="utf-8")

            findings = path_leak_check._scan_file(path)

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0][0], 1)
        self.assertEqual(findings[0][1], "macos-home")

    def test_scan_file_ignores_placeholder_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "sample.md"
            path.write_text("use /abs/path/to/polinko instead\n", encoding="utf-8")

            findings = path_leak_check._scan_file(path)

        self.assertEqual(findings, [])

    def test_scan_file_reports_home_relative_leak(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "sample.md"
            path.write_text("open ~/.codex/config.toml first\n", encoding="utf-8")

            findings = path_leak_check._scan_file(path)

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0][0], 1)
        self.assertEqual(findings[0][1], "home-relative")

    def test_tracked_files_filters_binary_like_suffixes(self) -> None:
        git_output = b"docs/ok.md\x00docs/skip.png\x00"
        proc = subprocess.CompletedProcess(
            args=["git", "ls-files", "-z"], returncode=0, stdout=git_output
        )
        with mock.patch("tools.path_leak_check.subprocess.run", return_value=proc):
            files = path_leak_check._tracked_files()

        self.assertEqual(
            [path.relative_to(path_leak_check.ROOT).as_posix() for path in files],
            ["docs/ok.md"],
        )

    def test_local_config_files_limit_audit_to_runtime_config_surfaces(self) -> None:
        with mock.patch("tools.path_leak_check.ROOT", Path("/repo")):
            with mock.patch("tools.path_leak_check._files_under_roots") as scan_roots:
                path_leak_check._local_config_files()

        scan_roots.assert_called_once_with(path_leak_check.LOCAL_CONFIG_ROOTS)

    def test_main_fails_when_tracked_leak_found(self) -> None:
        fake_file = path_leak_check.ROOT / "docs" / "sample.md"
        with mock.patch(
            "tools.path_leak_check._tracked_files", return_value=[fake_file]
        ):
            with mock.patch(
                "tools.path_leak_check._scan_paths",
                return_value=["docs/sample.md:1: macos-home: /Users/alice/secret"],
            ):
                with contextlib.redirect_stdout(io.StringIO()):
                    status = path_leak_check.main(["--scope", "tracked"])

        self.assertEqual(status, 1)

    def test_main_uses_local_config_scope_for_local_runtime_config(self) -> None:
        with mock.patch(
            "tools.path_leak_check._local_config_files", return_value=[]
        ) as local_config_files:
            with contextlib.redirect_stdout(io.StringIO()):
                status = path_leak_check.main(["--scope", "local-config"])

        self.assertEqual(status, 0)
        local_config_files.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
