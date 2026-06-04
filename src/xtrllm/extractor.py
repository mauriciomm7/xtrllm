# src/xtrllm/extractor.py
from pydantic import BaseModel
from xtrllm.clients.llm import LLMLibClient
from xtrllm.core.engine import ExtractionEngine
from xtrllm.core.registry import registry


class LLMXtractor:
    def __init__(self, task: str, model: str):
        task_class = registry.get(task)
        self.task = task_class()
        self.engine = ExtractionEngine(LLMLibClient(model))

    def __call__(self, *args, **kwargs) -> BaseModel:
        return self.engine.run(self.task, *args, **kwargs)
