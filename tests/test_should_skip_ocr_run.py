import unittest

from tools.should_skip_ocr_run import should_skip


class ShouldSkipOcrRunTests(unittest.TestCase):
    def test_skip_when_recent_rate_limit_abort(self) -> None:
        payload = {
            "generated_at": 1_000,
            "runs": [
                {"summary": {"aborted_due_to_rate_limit": True}},
            ],
        }
        self.assertTrue(should_skip(payload=payload, backoff_seconds=300, now_epoch=1_200))

    def test_do_not_skip_when_backoff_elapsed(self) -> None:
        payload = {
            "generated_at": 1_000,
            "runs": [
                {"summary": {"aborted_due_to_rate_limit": True}},
            ],
        }
        self.assertFalse(should_skip(payload=payload, backoff_seconds=300, now_epoch=1_400))

    def test_do_not_skip_without_rate_limit_abort(self) -> None:
        payload = {
            "generated_at": 1_000,
            "runs": [
                {"summary": {"aborted_due_to_rate_limit": False}},
            ],
        }
        self.assertFalse(should_skip(payload=payload, backoff_seconds=300, now_epoch=1_100))

    def test_do_not_skip_when_generated_at_missing(self) -> None:
        payload = {
            "runs": [
                {"summary": {"aborted_due_to_rate_limit": True}},
            ],
        }
        self.assertFalse(should_skip(payload=payload, backoff_seconds=300, now_epoch=1_100))


if __name__ == "__main__":
    unittest.main()
