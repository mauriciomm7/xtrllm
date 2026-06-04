# ``xtrllm``

A lightweight Python framework for portable, versioned, reusable LLM extraction tasks.

xtrllm separates two things every other library conflates:

- **The engine** — prompt → structured output → log (stable, ships with the package)
- **The task** — schema + prompt strategy + edge case handling (yours, lives in your repo)

## 🛠️ Installation

Option 1: Install the latest stable release directly from PyPI using pip:

```shell
pip install xtrllm
```

Option 2: Clone the repository

```shell
# 1. Clone the repo:
git clone https://github.com/mauriciomm7/xtrllm.git
cd xtrllm
# 2. Install using pip
pip install -e .
```

## Quickstart

The `xtrllm` package comes pre-loaded with some example tasks that I built for my own projects. However, the idea of this project is that you will create a costum extraction task for tour project say `eulex/tasks/classify_actor.py`, where a single Python file contains the Pydantic schema, the prompt function, and the task function, which returns the design output as a Pydantic-validated schema.

The workflow is intentionally simple. First, the user loads a task directory containing Python files with Pydantic schemas, prompt builders, and task classes. Next, an `LLMXtractor` instance is initialized with the desired task and language model. When the extractor is called, it submits the input to the model and returns a structured output validated against the predefined Pydantic schema. This validation layer ensures that only outputs conforming to the expected structure are returned, improving reliability and reducing the likelihood of malformed responses propagating through downstream pipelines.

```python
import xtrllm
from xtrllm import load_tasks, LLMXtractor

# LOAD your paper tasks
load_tasks("eulex/tasks", namespace="eulex")

# DEFINE what extractor to run
extractor = LLMXtractor(task="eulex/eu_lawyers", model="gpt-4.1-mini")
result = extractor("Komornik Sądowy przy Sądzie Rejonowym w Szczecinku")

# SEE result
print(result.value)
>>> 'ACT_TYPE_GOV_OFFIC_CIT'
```

In this example, the `eu_lawyers` task classifies an actor into a predefined actor taxonomy. The model determines the appropriate category, while Pydantic validation guarantees that the returned classification is a valid schema-compliant entry before it can be stored or used elsewhere in the system.

## Batch Processing

In principle, you could use a loop to collect results for all the entries you want to process. However, more often than not, you will be working with DataFrames where multiple parameters are passed as inputs and the goal is to return a new output column. For these cases, you can use batch processing.

In this example, I use a tool that classifies whether a given sentence of legal text has positive or negative valence toward a set of entities related to the EU legal order, such as the European Court of Justice, EU law, and related institutions. Here, the function takes two parameters, which are expected to correspond to columns in your DataFrame. Passing them as a dictionary mapping means that you do not need to rename your DataFrame columns manually. For example, if the expected parameter is `snippet_text` but your column is called `txt_snippet`, the mapping resolves this internally.

```python
# LOAD TASKS from directory
from xtrllm import load_tasks, DataFrameLLMXtractor

load_tasks(path=r"C:/uot25rev/tasks", namespace="uot25rev")

# DEFINE batch extractor tool parameter mapping
classify_Sent_LLMXtractor = DataFrameLLMXtractor(
    task="uot25rev/valence_for_entities",
    model="gpt-4.1-mini",
    parameters={
        "snippet_text": "snippet_text",
        "entities_str": "entities_str",
    },
    result_col="valence",
)

# LOAD analysis DataFrame
cmlr_sents_df = pd.read_parquet("C:/uot25rev/data/cmlr_snippets_base.parquet")

# RUN the batch extractor 
result_df = classify_Sent_LLMXtractor.run_parallel(cmlr_sents_df, rpm=1_000)
```

## Logging

By default, every call is auto-logged to `data/llm/logs.db` via the `llm` library.
Never touch it manually — it's the skip-guard source of truth and your full audit trail.
For more information checkout Simon Willison project [datasette](https://llm.datasette.io/en/stable/).

---

## Writing a Task

Each extraction task is defined in a single Python file. A task consists of three components:

1. A **Pydantic schema** that defines the expected output structure.
2. A **task class** that specifies the task name and output schema.
3. A **prompt builder** that converts user inputs into the prompt sent to the language model.

For example:

```python
# tasks/ajps2026/eu_lawyers.py

from pydantic import BaseModel
from typing import Optional
from xtrllm.core.base import BaseTask


class EULawyersSchema(BaseModel):
    lawyers: list[str]
    count: int
    confidence: Optional[float] = None


class EULawyersTask(BaseTask):
    name = "eu_lawyers"
    schema = EULawyersSchema

    system_prompt = ( "You extract the names of lawyers appearing in EU court judgments." )

    def build_prompt(self, text: str, context: str = "") -> str:
        return f"Context: {context}\n\nText: {text}"
```

When this task is executed, the model receives the generated prompt and must return an output that conforms to `EULawyersSchema`. Any response that fails schema validation is automatically rejected, ensuring that downstream code always receives a predictable structure.

Tasks require no manual registration or configuration. Once the task file exists inside a loaded task directory, `load_tasks()` will discover and register it automatically.


## Swap Providers — Zero Code Changes

```python
LLMXtractor(task="ajps2026/eu_lawyers", model="gpt-4o-mini")
LLMXtractor(task="ajps2026/eu_lawyers", model="claude-3-5-haiku-latest")
LLMXtractor(task="ajps2026/eu_lawyers", model="ollama/llama3")
```

All providers supported via the
[llm plugin ecosystem](https://llm.datasette.io/en/stable/plugins/index.html).

## Example for Replication Files

In most cases this will not be a substantial part of the project but just an adidtional tool in a entire processing pipeline. In those cases a possible organization structure can be following:

```
paper_abc/
├── tasks/
│     ├── eu_lawyers.py
│     └── get_citations.py
├── notebooks/
│       ├── main.ipynb
│       └── 
└── results/
```


## 🎓 Citation

If you use this framework in academic research, please cite:

Mandujano Manríquez, M. (2026). `xtrllm`: A lightweight Python framework for portable, versioned, reusable LLM extraction tasks. GitHub: https://github.com/mauriciomm7/xtrllm

```bib
@misc{mandujano2026xtrllm,
  author       = {Mauricio Mandujano Manríquez},
  title        = {``xtrllm``: A lightweight Python framework for portable, versioned, reusable LLM extraction tasks},
  year         = {2026},
  howpublished = {\url{https://github.com/mauriciomm7/xtrllm}},
  note         = {GitHub repository}
}
```

## 📄 License

This project is licensed under the [MIT License](./LICENSE).


<!-- Useful commands:

```shell
# Build Docs
mkdocs build 
mkdocs serve

# Build Package
rm -rf dist build *.egg-info
python -m build
twine upload dist/*
``` -->
