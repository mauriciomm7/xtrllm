# src/xtrllm/throttlers/adaptive.py
import time
from xtrllm.throttlers.base import BaseThrottler


class AdaptiveThrottler(BaseThrottler):
    """
    Simple adaptive RPM throttler that increases RPM on success and halves it on rate‑limit.

    For pseudo‑maximizing TPM:
    - Set max_rpm ≈ (TPM limit) / (median tokens per request).
    - Example: 4_000_000 TPM and 4_000 tokens/request → max_rpm ≈ 1000.
    """

    def __init__(self, initial_rpm: int, max_rpm: int, min_rpm: int = 100):
        """
        Args:
            initial_rpm (int):
                Starting RPM; usually set close to max_rpm.
            max_rpm (int):
                Maximum allowed RPM (to avoid exceeding TPM limit).
            min_rpm (int, optional):
                Floor RPM after repeated rate‑limits; default 100.
        """
        self.current_rpm = initial_rpm
        self.min_rpm = min_rpm
        self.max_rpm = max_rpm
        self.delay = 60.0 / initial_rpm
        self.consecutive_successes = 0
        self._last_call = 0.0

    def __call__(self, index: int = 1) -> None:
        elapsed = time.monotonic() - self._last_call
        wait = self.delay - elapsed
        if wait > 0:
            time.sleep(wait)
        self._last_call = time.monotonic()

    def on_success(self) -> None:
        self.consecutive_successes += 1
        if self.consecutive_successes >= 10:
            self.current_rpm = min(self.max_rpm, self.current_rpm * 1.1)
            self.delay = 60.0 / self.current_rpm
            self.consecutive_successes = 0

    def on_rate_limit(self) -> None:
        self.current_rpm = max(self.min_rpm, self.current_rpm * 0.5)
        self.delay = 60.0 / self.current_rpm
        self.consecutive_successes = 0


def adaptive_throttler(
    initial_rpm: int,
    max_rpm: int,
    min_rpm: int = 100,
) -> AdaptiveThrottler:
    """Factory that returns an AdaptiveThrottler tuned to max RPM ≈ TPM / median tokens per request.

    Useful defaults:
    - initial_rpm = max_rpm  # start at full allowed rate
    - max_rpm = TPM_LIMIT // MEDIAN_TOKENS_PER_REQUEST
    """
    return AdaptiveThrottler(initial_rpm, max_rpm, min_rpm)
