import base64
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from api.manual_evals_surface import build_manual_evals_surface_payload
from tools.build_manual_evals_db import build_manual_evals_db
from tests.test_build_manual_evals_db import _init_history_db

_PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+lmR8AAAAASUVORK5CYII="
)


class ManualEvalsSurfaceTests(unittest.TestCase):
    def test_returns_unavailable_when_db_missing(self) -> None:
        payload = build_manual_evals_surface_payload(
            db_path=Path("/tmp/non-existent-manual-evals.db"),
        )
        self.assertFalse(payload["available"])
        self.assertEqual(payload["summary"]["ocr_runs"], 0)
        self.assertEqual(payload["runs"], [])

    def test_returns_runs_sessions_and_image_preview_fields(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            history_db = root / "history.db"
            output_db = root / "manual_evals.db"
            image_dir = root / "images"
            image_dir.mkdir(parents=True, exist_ok=True)
            (image_dir / "image1.png").write_bytes(_PNG_1X1)

            _init_history_db(history_db)
            build_manual_evals_db(
                history_db=history_db,
                output_db=output_db,
                image_roots=[image_dir],
                include_thumbnails=True,
                thumbnail_size=64,
            )

            payload = build_manual_evals_surface_payload(
                db_path=output_db,
                max_runs=20,
                max_sessions=10,
            )
            self.assertTrue(payload["available"])
            self.assertEqual(payload["summary"]["sessions"], 1)
            self.assertEqual(payload["summary"]["ocr_runs"], 1)
            self.assertEqual(len(payload["sessions"]), 1)
            self.assertEqual(len(payload["runs"]), 1)
            run = payload["runs"][0]
            self.assertEqual(run["run_id"], "ocr-1")
            self.assertEqual(run["session_id"], "chat-1")
            self.assertIn("image", run)
            self.assertIn("session_eval", run)
            self.assertEqual(run["session_eval"]["feedback_count"], 0)
            image = run["image"]
            self.assertTrue(str(image["source_filename"]).endswith("image1.png"))
            self.assertEqual(image["display_filename"], "image1.png")
            self.assertIn(image["status"], {"thumbnail_ready", "resolved_no_pillow", "thumbnail_error"})
            if image["status"] == "thumbnail_ready":
                self.assertTrue(str(image["thumbnail_data_url"]).startswith("data:image/png;base64,"))


if __name__ == "__main__":
    unittest.main()
