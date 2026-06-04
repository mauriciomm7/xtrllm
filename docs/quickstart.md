# Quickstart

## 🛠️ Installation

*Install* the latest stable release directly from PyPI using pip:

```shell
pip install xtrllm
```


## Basic Usage

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

## Swap Providers — Zero Code Changes

```python
LLMXtractor(task="uot25rev/valence_for_entities", model="gpt-4o-mini")
LLMXtractor(task="uot25rev/valence_for_entities", model="claude-3-5-haiku-latest")
LLMXtractor(task="uot25rev/valence_for_entities", model="ollama/llama3")
```

All providers supported via the
[llm plugin ecosystem](https://llm.datasette.io/en/stable/plugins/index.html).

* * *
