# src/xtrllm/throttlers/fixed.py
import time
from xtrllm.throttlers.base import BaseThrottler
from xtrllm.core.constants import DEFAULT_FIXED_DELAY


class FixedDelayThrottler(BaseThrottler):
    def __init__(self, seconds: float = DEFAULT_FIXED_DELAY):
        self.seconds = seconds

    def __call__(self, index: int) -> None:
        time.sleep(self.seconds)


def fixed_delay(seconds: float = DEFAULT_FIXED_DELAY) -> FixedDelayThrottler:
    return FixedDelayThrottler(seconds)
