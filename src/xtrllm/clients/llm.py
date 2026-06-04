# src/xtrllm/clients/llm.py
import llm
import sqlite_utils
from pydantic import BaseModel
from xtrllm.core.base import LLMClient


class LLMLibClient(LLMClient):
    def __init__(self, model: str):
        self.model = llm.get_model(model) # type: ignore

    def complete(self, system_prompt: str, user_prompt: str, schema: type[BaseModel]) -> BaseModel:
        response = self.model.prompt(
            user_prompt,
            system=system_prompt,
            schema=schema,
        )
        # 
        response.log_to_db(sqlite_utils.Database(llm.user_dir() / "logs.db"))
        return schema.model_validate_json(response.text())
