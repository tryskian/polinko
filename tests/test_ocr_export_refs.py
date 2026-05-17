import os
import tempfile
import unittest
from pathlib import Path

from tools.ocr_export_refs import resolve_export_ref
from tools.ocr_export_refs import to_export_ref
from tools.ocr_export_refs import to_repo_ref


class OcrExportRefsTests(unittest.TestCase):
    def test_export_ref_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir)
            image_path = export_root / "assets" / "sample.png"
            image_path.parent.mkdir(parents=True, exist_ok=True)
            image_path.write_bytes(b"png")

            ref = to_export_ref(image_path, export_root=export_root)
            self.assertEqual(ref, "assets/sample.png")
            self.assertEqual(resolve_export_ref(ref, export_root=export_root), image_path.resolve())

    def test_resolve_export_ref_uses_env_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir)
            image_path = export_root / "assets" / "sample.png"
            image_path.parent.mkdir(parents=True, exist_ok=True)
            image_path.write_bytes(b"png")

            old = os.environ.get("CGPT_EXPORT_ROOT")
            os.environ["CGPT_EXPORT_ROOT"] = str(export_root)
            try:
                self.assertEqual(resolve_export_ref("assets/sample.png"), image_path.resolve())
            finally:
                if old is None:
                    os.environ.pop("CGPT_EXPORT_ROOT", None)
                else:
                    os.environ["CGPT_EXPORT_ROOT"] = old

    def test_repo_ref_is_relative_inside_repo(self) -> None:
        repo_path = Path(__file__).resolve()
        ref = to_repo_ref(repo_path)
        self.assertTrue(ref.startswith("tests/"))


if __name__ == "__main__":
    unittest.main()
