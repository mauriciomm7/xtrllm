# src/xtrllm/throttlers/rpm.py
import time
from xtrllm.throttlers.base import BaseThrottler
from xtrllm.core.constants import DEFAULT_RPM


class RPMThrottler(BaseThrottler):
    def __init__(self, rpm: int = DEFAULT_RPM):
        self.min_interval = 60.0 / rpm
        self._last_call = 0.0

    def __call__(self, index: int) -> None:
        elapsed = time.monotonic() - self._last_call
        wait = self.min_interval - elapsed
        if wait > 0:
            time.sleep(wait)
        self._last_call = time.monotonic()


def rpm_throttler(rpm: int = DEFAULT_RPM) -> RPMThrottler:
    return RPMThrottler(rpm)
