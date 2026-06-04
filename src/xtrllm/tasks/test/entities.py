# src/xtrllm/tasks/test/entities.py
from pydantic import BaseModel
from xtrllm.core.base import BaseTask


class EntitiesSchema(BaseModel):
    persons: list[str]
    locations: list[str]
    organizations: list[str]
    count: int


class EntitiesTask(BaseTask):
    name = "entities"
    schema = EntitiesSchema
    system_prompt = "You extract named entities from text. Return persons, locations, and organizations mentioned."

    def build_prompt(self, text: str) -> str:
        return f"Extract all named entities from this text:\n\n{text}"
