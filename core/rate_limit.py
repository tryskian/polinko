import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable


class SlidingWindowRateLimiter:
    def __init__(
        self,
        *,
        window_seconds: int = 60,
        cleanup_interval_seconds: int = 300,
        clock: Callable[[], float] | None = None,
    ) -> None:
        self._window_seconds = max(1, window_seconds)
        self._cleanup_interval_seconds = max(self._window_seconds, cleanup_interval_seconds)
        self._clock = clock or time.time
        self._last_cleanup_at = self._clock()
        self._lock = threading.Lock()
        self._buckets: dict[str, deque[float]] = defaultdict(deque)

    def clear(self) -> None:
        with self._lock:
            self._buckets.clear()

    def bucket_count(self) -> int:
        with self._lock:
            return len(self._buckets)

    @staticmethod
    def _prune_bucket(bucket: deque[float], *, cutoff: float) -> None:
        while bucket and bucket[0] <= cutoff:
            bucket.popleft()

    def _cleanup_stale_buckets(self, *, now: float) -> None:
        if now - self._last_cleanup_at < self._cleanup_interval_seconds:
            return
        cutoff = now - self._window_seconds
        for identifier, bucket in list(self._buckets.items()):
            self._prune_bucket(bucket, cutoff=cutoff)
            if not bucket:
                del self._buckets[identifier]
        self._last_cleanup_at = now

    def consume(self, identifier: str, *, limit_per_minute: int) -> int | None:
        """Returns retry-after seconds when rate-limited, else None."""
        if limit_per_minute <= 0:
            return None

        now = self._clock()
        cutoff = now - self._window_seconds
        with self._lock:
            self._cleanup_stale_buckets(now=now)
            bucket = self._buckets[identifier]
            self._prune_bucket(bucket, cutoff=cutoff)
            if len(bucket) >= limit_per_minute:
                return max(1, int(self._window_seconds - (now - bucket[0])))
            bucket.append(now)
        return None
