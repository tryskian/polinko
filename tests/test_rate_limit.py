import unittest

from core.rate_limit import SlidingWindowRateLimiter


class FakeClock:
    def __init__(self, start: float = 0.0) -> None:
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class SlidingWindowRateLimiterTests(unittest.TestCase):
    def test_cleanup_removes_stale_buckets(self) -> None:
        clock = FakeClock()
        limiter = SlidingWindowRateLimiter(
            window_seconds=60,
            cleanup_interval_seconds=60,
            clock=clock,
        )

        limiter.consume("ip-a", limit_per_minute=2)
        clock.advance(1)
        limiter.consume("ip-b", limit_per_minute=2)
        self.assertEqual(limiter.bucket_count(), 2)

        clock.advance(120)
        limiter.consume("ip-c", limit_per_minute=2)

        self.assertEqual(limiter.bucket_count(), 1)

    def test_retry_after_respects_window_seconds(self) -> None:
        clock = FakeClock()
        limiter = SlidingWindowRateLimiter(
            window_seconds=10,
            cleanup_interval_seconds=10,
            clock=clock,
        )

        first = limiter.consume("client-1", limit_per_minute=1)
        self.assertIsNone(first)

        clock.advance(3)
        retry_after = limiter.consume("client-1", limit_per_minute=1)
        self.assertEqual(retry_after, 7)

        clock.advance(7)
        allowed_again = limiter.consume("client-1", limit_per_minute=1)
        self.assertIsNone(allowed_again)

    def test_limit_zero_is_noop(self) -> None:
        limiter = SlidingWindowRateLimiter()
        result = limiter.consume("client-1", limit_per_minute=0)
        self.assertIsNone(result)
        self.assertEqual(limiter.bucket_count(), 0)


if __name__ == "__main__":
    unittest.main()
