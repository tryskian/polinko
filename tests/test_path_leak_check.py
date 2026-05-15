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
        proc = subprocess.CompletedProcess(args=["git", "ls-files", "-z"], returncode=0, stdout=git_output)
        with mock.patch("tools.path_leak_check.subprocess.run", return_value=proc):
            files = path_leak_check._tracked_files()

        self.assertEqual([path.relative_to(path_leak_check.ROOT).as_posix() for path in files], ["docs/ok.md"])

    def test_main_fails_when_tracked_leak_found(self) -> None:
        fake_file = path_leak_check.ROOT / "docs" / "sample.md"
        with mock.patch("tools.path_leak_check._tracked_files", return_value=[fake_file]):
            with mock.patch(
                "tools.path_leak_check._scan_paths",
                return_value=["docs/sample.md:1: macos-home: /Users/alice/secret"],
            ):
                with contextlib.redirect_stdout(io.StringIO()):
                    status = path_leak_check.main(["--scope", "tracked"])

        self.assertEqual(status, 1)


if __name__ == "__main__":
    unittest.main()
