# src/xtrllm/core/engine.py
from pydantic import BaseModel
from xtrllm.core.base import BaseTask, LLMClient


class ExtractionEngine:
    def __init__(self, client: LLMClient):
        self.client = client

    def run(self, task: BaseTask, *args, **kwargs) -> BaseModel:
        user_prompt = task.build_prompt(*args, **kwargs)
        return self.client.complete(
            system_prompt=task.system_prompt,
            user_prompt=user_prompt,
            schema=task.schema,
        )
