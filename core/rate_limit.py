import threading
import time
from collections import defaultdict, deque


class SlidingWindowRateLimiter:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._buckets: dict[str, deque[float]] = defaultdict(deque)

    def clear(self) -> None:
        with self._lock:
            self._buckets.clear()

    def consume(self, identifier: str, *, limit_per_minute: int) -> int | None:
        """Returns retry-after seconds when rate-limited, else None."""
        if limit_per_minute <= 0:
            return None

        now = time.time()
        cutoff = now - 60.0
        with self._lock:
            bucket = self._buckets[identifier]
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()
            if len(bucket) >= limit_per_minute:
                return max(1, int(60 - (now - bucket[0])))
            bucket.append(now)
        return None

