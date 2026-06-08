# Quickstart

This guide shows the basic `xtrllm` workflow:

1. Define a task as a normal Python file.
2. Load the task directory.
3. Run the task with `LLMXtractor`.
4. Scale the same task over a DataFrame with `DataFrameLLMXtractor`.

## Installation

Install the latest stable release from PyPI:

```shell
pip install xtrllm
```

## Define A Task

An `xtrllm` task is a small Python class that combines three things:

- a Pydantic schema for the structured output
- a system prompt with the task rules
- a `build_prompt()` method that turns Python inputs into the user prompt

For example, a project might keep the following task at `eulex/tasks/classify_actor.py`.

```python
from typing import Literal
from pydantic import BaseModel
from xtrllm.core.base import BaseTask

class EulexDBActorSchema(BaseModel):
    actor_type: Literal[
        "ACT_TYPE_EU_INST",
        "ACT_TYPE_NAT_COURT",
        "ACT_TYPE_GOV_INST_NAT",
        "ACT_TYPE_GOV_OFFIC_CIT",
        "ACT_TYPE_GOV_OFFIC_NAT",
        "ACT_TYPE_PERSON",
        "ACT_TYPE_UNSPEC",
    ]


SYS_MSG = """
You are an expert in classifying actors into predefined institutional categories.

# Task
Classify the given actor into EXACTLY ONE predefined actor type.

# Rules
- Choose the single best matching category.
- Prefer the most specific category available.
- If uncertain, choose ACT_TYPE_UNSPEC.

# Examples
- "Tribunale di Milano" -> ACT_TYPE_NAT_COURT
- "Procura della Repubblica presso il Tribunale di Cagliari" -> ACT_TYPE_GOV_INST_NAT
- "Komornik Sądowy przy Sądzie Rejonowym w Szczecinku" -> ACT_TYPE_GOV_OFFIC_CIT
- "Präsidentin des Landesgerichts Feldkirch" -> ACT_TYPE_GOV_OFFIC_NAT
"""

class EulexDBClassifyActorsTask(BaseTask):
    name = "classify_actor"
    version = "v1"
    schema = EulexDBActorSchema
    system_prompt = SYS_MSG

    def build_prompt(self, actor_name: str, context: str = "") -> str:
        return f"""
ACTOR:
{actor_name}

CONTEXT (if available):
{context}

Classify this actor.
""".strip()
```

The task name is set by the class attribute `name`. When loaded with a namespace, `classify_actor` becomes available as `eulex/classify_actor`.

## Run One Extraction

Use `load_tasks()` to register every task file in a directory, then initialize `LLMXtractor` with the task name and model.

```python
from xtrllm import LLMXtractor, load_tasks

load_tasks("eulex/tasks", namespace="eulex")

extractor = LLMXtractor(
    task="eulex/classify_actor",
    model="gpt-4.1-mini",
)

result = extractor("Tribunale di Milano")

print(result.actor_type)
# ACT_TYPE_NAT_COURT

print(result.model_dump(mode="json"))
# {"actor_type": "ACT_TYPE_NAT_COURT"}
```

The returned value is the Pydantic model defined by the task schema. You can access fields directly or serialize the model for storage.

## Batch Processing

For tabular workflows, `DataFrameLLMXtractor` maps DataFrame columns onto the parameters expected by the task's `build_prompt()` method.

This example uses the `uot25rev` sentiment-valence task. The source file is `valence_for_entities.py`, but the registered task name in the source code is `sentiment_valence`, so the task is addressed as `uot25rev/sentiment_valence`.

```python
import pandas as pd

from xtrllm import DataFrameLLMXtractor, load_tasks

load_tasks("uot25rev/tasks", namespace="uot25rev")

df = pd.DataFrame(
    {
        "txt_snippet": [
            "It is particularly unrealistic of THE COMMISSION to expect acceptance of the plan.",
            "THE COMMISSION submitted its proposal to the Council.",
        ],
        "entities": [
            "THE COMMISSION",
            "THE COMMISSION",
        ],
    }
)

classify_valence = DataFrameLLMXtractor(
    task="uot25rev/sentiment_valence",
    model="gpt-4.1-mini",
    parameters={
        "snippet_text": "txt_snippet",
        "entities_str": "entities",
    },
    result_col="valence",
)

result_df = classify_valence.run_parallel(df, rpm=1_000)
```

`parameters` maps task input names to DataFrame column names. In this example, the task expects `snippet_text` and `entities_str`, while the DataFrame columns are named `txt_snippet` and `entities`.

## Swap Providers

Models are routed through the [`llm` plugin ecosystem](https://llm.datasette.io/en/stable/plugins/index.html), so provider changes usually only require changing the model string.

```python
LLMXtractor(task="uot25rev/sentiment_valence", model="gpt-4o-mini")
LLMXtractor(task="uot25rev/sentiment_valence", model="claude-3-5-haiku-latest")
LLMXtractor(task="uot25rev/sentiment_valence", model="ollama/llama3")
```
