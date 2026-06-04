# src/xtrllm/core/base.py
from abc import ABC, abstractmethod
from pydantic import BaseModel


class LLMClient(ABC):
    @abstractmethod
    def complete(self, system_prompt: str, user_prompt: str, schema: type[BaseModel]) -> BaseModel:
        """Send prompt to LLM, return validated Pydantic object."""
        ...


class BaseTask(ABC):
    name: str
    version: str = "v1"
    schema: type[BaseModel]
    system_prompt: str
    skip_if_logged: bool = True

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for attr in ("name", "schema", "system_prompt"):
            if not hasattr(cls, attr):
                raise TypeError(f"{cls.__name__} must define '{attr}'")

    @abstractmethod
    def build_prompt(self, *args, **kwargs) -> str:
        """Build the user prompt from input arguments."""
        ...
