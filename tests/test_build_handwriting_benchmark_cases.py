import json
import tempfile
import unittest
from pathlib import Path

from tools.build_handwriting_benchmark_cases import build_handwriting_benchmark_cases


class BuildHandwritingBenchmarkCasesTests(unittest.TestCase):
    def test_builds_strict_ranked_handwriting_subset(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            review_path = root / "review.json"
            handwriting_cases_path = root / "handwriting_cases.json"
            output_cases_path = root / "benchmark_cases.json"

            review_payload = {
                "episodes": [
                    {
                        "conversation_id": "conv-low",
                        "image_path": "/tmp/a.png",
                        "lane": "handwriting",
                        "confidence": "medium",
                        "emit_status": "emitted",
                        "anchor_terms_count": 3,
                        "chosen_phrases": ["a", "b"],
                    },
                    {
                        "conversation_id": "conv-top",
                        "image_path": "/tmp/b.png",
                        "lane": "handwriting",
                        "confidence": "high",
                        "emit_status": "emitted",
                        "anchor_terms_count": 6,
                        "chosen_phrases": ["a", "b", "c"],
                    },
                    {
                        "conversation_id": "conv-typed",
                        "image_path": "/tmp/c.png",
                        "lane": "typed",
                        "confidence": "high",
                        "emit_status": "emitted",
                        "anchor_terms_count": 8,
                        "chosen_phrases": ["x"],
                    },
                ]
            }
            handwriting_cases_payload = {
                "cases": [
                    {"id": "h1", "image_path": "/tmp/a.png", "must_contain_any": ["one", "two", "three"]},
                    {"id": "h2", "image_path": "/tmp/b.png", "must_contain_any": ["one", "two", "three", "four"]},
                    {"id": "h3", "image_path": "/tmp/c.png", "must_contain_any": ["one", "two", "three", "four"]},
                ]
            }
            review_path.write_text(json.dumps(review_payload), encoding="utf-8")
            handwriting_cases_path.write_text(json.dumps(handwriting_cases_payload), encoding="utf-8")

            summary = build_handwriting_benchmark_cases(
                review_path=review_path,
                handwriting_cases_path=handwriting_cases_path,
                output_cases_path=output_cases_path,
                top_k=2,
                min_anchor_terms=3,
            )
            self.assertEqual(summary["candidate_count"], 2)
            self.assertEqual(summary["selected_count"], 2)

            output = json.loads(output_cases_path.read_text(encoding="utf-8"))
            self.assertEqual(len(output["cases"]), 2)
            self.assertEqual(output["cases"][0]["id"], "h2")
            self.assertEqual(output["cases"][1]["id"], "h1")

    def test_fallback_keeps_best_case_when_strict_filter_is_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            review_path = root / "review.json"
            handwriting_cases_path = root / "handwriting_cases.json"
            output_cases_path = root / "benchmark_cases.json"

            review_payload = {
                "episodes": [
                    {
                        "conversation_id": "conv-top",
                        "image_path": "/tmp/top.png",
                        "lane": "handwriting",
                        "confidence": "medium",
                        "emit_status": "emitted",
                        "anchor_terms_count": 4,
                        "chosen_phrases": ["foo"],
                    }
                ]
            }
            handwriting_cases_payload = {
                "cases": [
                    {"id": "h-top", "image_path": "/tmp/top.png", "must_contain_any": ["one", "two"]},
                ]
            }
            review_path.write_text(json.dumps(review_payload), encoding="utf-8")
            handwriting_cases_path.write_text(json.dumps(handwriting_cases_payload), encoding="utf-8")

            summary = build_handwriting_benchmark_cases(
                review_path=review_path,
                handwriting_cases_path=handwriting_cases_path,
                output_cases_path=output_cases_path,
                top_k=3,
                min_anchor_terms=3,
            )
            self.assertEqual(summary["candidate_count"], 1)
            self.assertEqual(summary["selected_count"], 1)

            output = json.loads(output_cases_path.read_text(encoding="utf-8"))
            self.assertEqual([case["id"] for case in output["cases"]], ["h-top"])


if __name__ == "__main__":
    unittest.main()
