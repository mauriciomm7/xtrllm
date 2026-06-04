# src/xtrllm/throttlers/base.py
from abc import ABC, abstractmethod


class BaseThrottler(ABC):
    @abstractmethod
    def __call__(self, index: int) -> None:
        """Called before each row. index is the current row number."""
        ...
