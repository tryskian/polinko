from __future__ import annotations

import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "open_local_url.sh"


class OpenLocalUrlShellTests(unittest.TestCase):
    def run_launcher(
        self, url: str, tool_dir: Path, capture_path: Path
    ) -> subprocess.CompletedProcess[str]:
        opener = tool_dir / "open"
        opener.write_text(
            '#!/bin/sh\nprintf "%s\\n" "$1" > "$OPEN_CAPTURE"\n',
            encoding="utf-8",
        )
        opener.chmod(opener.stat().st_mode | stat.S_IXUSR)

        env = {
            **os.environ,
            "OPEN_CAPTURE": str(capture_path),
            "PATH": str(tool_dir),
        }
        return subprocess.run(
            ["/bin/bash", str(SCRIPT), url],
            cwd=REPO_ROOT,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )

    def run_launcher_with_xdg_open(
        self, url: str, tool_dir: Path
    ) -> subprocess.CompletedProcess[str]:
        opener = tool_dir / "xdg-open"
        opener.write_text("#!/bin/sh\nexit 7\n", encoding="utf-8")
        opener.chmod(opener.stat().st_mode | stat.S_IXUSR)

        env = {
            **os.environ,
            "PATH": str(tool_dir),
        }
        return subprocess.run(
            ["/bin/bash", str(SCRIPT), url],
            cwd=REPO_ROOT,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )

    def run_launcher_with_failing_open(
        self, url: str, tool_dir: Path
    ) -> subprocess.CompletedProcess[str]:
        opener = tool_dir / "open"
        opener.write_text("#!/bin/sh\nexit 9\n", encoding="utf-8")
        opener.chmod(opener.stat().st_mode | stat.S_IXUSR)

        env = {
            **os.environ,
            "PATH": str(tool_dir),
        }
        return subprocess.run(
            ["/bin/bash", str(SCRIPT), url],
            cwd=REPO_ROOT,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )

    def run_launcher_without_system_opener(
        self, url: str, tool_dir: Path
    ) -> subprocess.CompletedProcess[str]:
        env = {
            **os.environ,
            "PATH": str(tool_dir),
        }
        return subprocess.run(
            ["/bin/bash", str(SCRIPT), url],
            cwd=REPO_ROOT,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )

    def test_launcher_accepts_local_urls(self) -> None:
        urls = (
            "http://127.0.0.1:8000/docs",
            "http://127.255.255.255:8000/docs",
            "https://localhost:8000/docs",
            "https://localhost:8000/docs?tab=api",
            "http://[::1]:8000/docs",
            "http://[::1]:8000/docs#health",
        )

        for url in urls:
            with self.subTest(url=url), tempfile.TemporaryDirectory() as tmp:
                tool_dir = Path(tmp)
                capture_path = tool_dir / "opened.txt"

                result = self.run_launcher(url, tool_dir, capture_path)

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(capture_path.read_text(encoding="utf-8").strip(), url)

    def test_launcher_rejects_external_urls_before_launch(self) -> None:
        urls = (
            "https://example.com/docs",
            "http://128.0.0.1/docs",
            "http://127.256.0.1/docs",
            "http://127.0.999.1/docs",
            "http://127.example.com/docs",
            "http://127.0.0.1.example.com/docs",
        )

        for url in urls:
            with self.subTest(url=url), tempfile.TemporaryDirectory() as tmp:
                tool_dir = Path(tmp)
                capture_path = tool_dir / "opened.txt"

                result = self.run_launcher(url, tool_dir, capture_path)

                self.assertEqual(result.returncode, 2)
                self.assertIn("Refusing to launch non-local URL", result.stderr)
                self.assertFalse(capture_path.exists())

    def test_launcher_surfaces_xdg_open_failures(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_launcher_with_xdg_open(
                "http://127.0.0.1:8000/docs", Path(tmp)
            )

        self.assertEqual(result.returncode, 1)
        self.assertIn("Failed to launch local URL with xdg-open", result.stderr)

    def test_launcher_surfaces_open_failures(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_launcher_with_failing_open(
                "http://127.0.0.1:8000/docs", Path(tmp)
            )

        self.assertEqual(result.returncode, 1)
        self.assertIn("Failed to launch local URL with open", result.stderr)

    def test_launcher_prints_local_url_when_no_system_opener_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_launcher_without_system_opener(
                "http://127.0.0.1:8000/docs", Path(tmp)
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.strip(),
            "Open this URL in your browser: http://127.0.0.1:8000/docs",
        )


if __name__ == "__main__":
    unittest.main()
