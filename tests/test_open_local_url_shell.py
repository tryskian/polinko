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


if __name__ == "__main__":
    unittest.main()
