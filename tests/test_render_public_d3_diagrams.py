import tempfile
import unittest
from pathlib import Path

from tools.render_public_d3_diagrams import _write_if_changed


class RenderPublicD3DiagramsTests(unittest.TestCase):
    def test_write_if_changed_skips_identical_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "diagram.svg"
            output_path.write_text("<svg>same</svg>\n", encoding="utf-8")
            before = output_path.stat().st_mtime_ns

            changed = _write_if_changed(output_path, "<svg>same</svg>\n")

            self.assertFalse(changed)
            self.assertEqual(output_path.stat().st_mtime_ns, before)

    def test_write_if_changed_updates_different_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "diagram.svg"
            output_path.write_text("<svg>old</svg>\n", encoding="utf-8")

            changed = _write_if_changed(output_path, "<svg>new</svg>\n")

            self.assertTrue(changed)
            self.assertEqual(
                output_path.read_text(encoding="utf-8"), "<svg>new</svg>\n"
            )

    def test_write_if_changed_creates_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "diagram.svg"

            changed = _write_if_changed(output_path, "<svg>new</svg>\n")

            self.assertTrue(changed)
            self.assertEqual(
                output_path.read_text(encoding="utf-8"), "<svg>new</svg>\n"
            )


if __name__ == "__main__":
    unittest.main()
