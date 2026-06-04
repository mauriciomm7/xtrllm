# src\xtrllm\tasks\uio26fil\eu_primary_law.py
from pydantic import BaseModel
from xtrllm.core.base import BaseTask

# DEFINE STRUCTURED OUTPUT
class SentimentValenceSchema(BaseModel):
    label: bool


SYS_MSG = """ 
"""

class SentimentValenceTask(BaseTask):
    name = "eu_primary_law"
    version = "v1"
    schema = SentimentValenceSchema
    system_prompt = SYS_MSG

    def build_prompt(self, snippet_text: str) -> str:
        return f"""TEXT TO ANALYZE: 
    {snippet_text}
    """.strip()
