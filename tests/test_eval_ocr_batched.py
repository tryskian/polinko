import unittest

from tools.eval_ocr_batched import BatchPlan
from tools.eval_ocr_batched import _plan_batches


class OcrEvalBatchedPlanningTests(unittest.TestCase):
    def test_plan_batches_default_window(self) -> None:
        plans = _plan_batches(total_cases=95, offset=0, max_cases=0, batch_size=40)
        self.assertEqual(
            plans,
            [
                BatchPlan(offset=0, max_cases=40),
                BatchPlan(offset=40, max_cases=40),
                BatchPlan(offset=80, max_cases=15),
            ],
        )

    def test_plan_batches_with_offset_and_cap(self) -> None:
        plans = _plan_batches(total_cases=142, offset=40, max_cases=60, batch_size=25)
        self.assertEqual(
            plans,
            [
                BatchPlan(offset=40, max_cases=25),
                BatchPlan(offset=65, max_cases=25),
                BatchPlan(offset=90, max_cases=10),
            ],
        )

    def test_plan_batches_offset_beyond_end_is_empty(self) -> None:
        plans = _plan_batches(total_cases=10, offset=20, max_cases=0, batch_size=5)
        self.assertEqual(plans, [])

    def test_plan_batches_rejects_invalid_inputs(self) -> None:
        with self.assertRaises(RuntimeError):
            _plan_batches(total_cases=-1, offset=0, max_cases=0, batch_size=5)
        with self.assertRaises(RuntimeError):
            _plan_batches(total_cases=10, offset=-1, max_cases=0, batch_size=5)
        with self.assertRaises(RuntimeError):
            _plan_batches(total_cases=10, offset=0, max_cases=-1, batch_size=5)
        with self.assertRaises(RuntimeError):
            _plan_batches(total_cases=10, offset=0, max_cases=0, batch_size=0)


if __name__ == "__main__":
    unittest.main()
