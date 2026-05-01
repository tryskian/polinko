import tempfile
import unittest
from pathlib import Path

from tools.eval_ocr_common import build_chat_attachment
from tools.eval_ocr_common import build_data_url
from tools.eval_ocr_common import build_ocr_request_input
from tools.eval_ocr_common import load_attachment_input


class OcrCommonTests(unittest.TestCase):
    def test_load_attachment_input_uses_placeholder_defaults_without_image(self) -> None:
        raw_bytes, mime_type, source_name, text_hint = load_attachment_input(
            image_path_raw="",
            source_name="",
            mime_type=None,
            text_hint="  hinted text  ",
            placeholder_bytes=b"x",
            placeholder_mime_type="image/png",
            placeholder_source_name="fallback.png",
        )

        self.assertEqual(raw_bytes, b"x")
        self.assertEqual(mime_type, "image/png")
        self.assertEqual(source_name, "fallback.png")
        self.assertEqual(text_hint, "hinted text")

    def test_load_attachment_input_reads_file_and_infers_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = Path(tmpdir) / "sample.png"
            image_path.write_bytes(b"png-bytes")

            raw_bytes, mime_type, source_name, text_hint = load_attachment_input(
                image_path_raw=str(image_path),
                source_name="",
                mime_type=None,
                text_hint=None,
                placeholder_bytes=b"x",
                placeholder_mime_type="image/png",
                placeholder_source_name="fallback.png",
            )

        self.assertEqual(raw_bytes, b"png-bytes")
        self.assertEqual(mime_type, "image/png")
        self.assertEqual(source_name, "sample.png")
        self.assertIsNone(text_hint)

    def test_build_data_url_encodes_bytes(self) -> None:
        self.assertEqual(
            build_data_url(raw_bytes=b"ab", mime_type="text/plain"),
            "data:text/plain;base64,YWI=",
        )

    def test_build_chat_attachment_preserves_ocr_attachment_shape(self) -> None:
        self.assertEqual(
            build_chat_attachment(
                data_base64="YWJj",
                mime_type="image/png",
                source_name="scan.png",
                text_hint="hinted text",
                visual_context_hint="blue awning sign",
            ),
            {
                "data_base64": "YWJj",
                "mime_type": "image/png",
                "source_name": "scan.png",
                "text_hint": "hinted text",
                "visual_context_hint": "blue awning sign",
                "memory_scope": "global",
            },
        )

    def test_build_ocr_request_input_uses_placeholder_bytes_when_no_image(self) -> None:
        data_base64, mime_type = build_ocr_request_input(
            image_path_raw="",
            mime_type=None,
            placeholder_bytes=b"0",
            placeholder_mime_type="application/octet-stream",
        )

        self.assertEqual(data_base64, "MA==")
        self.assertEqual(mime_type, "application/octet-stream")

    def test_build_ocr_request_input_reads_file_and_encodes_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = Path(tmpdir) / "sample.png"
            image_path.write_bytes(b"png-bytes")

            data_base64, mime_type = build_ocr_request_input(
                image_path_raw=str(image_path),
                mime_type=None,
                placeholder_bytes=b"0",
                placeholder_mime_type="application/octet-stream",
            )

        self.assertEqual(data_base64, "cG5nLWJ5dGVz")
        self.assertEqual(mime_type, "image/png")


if __name__ == "__main__":
    unittest.main()
