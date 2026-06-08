# `xtrllm` - Extract Structured Data using LLMs

A lightweight Python framework for portable, versioned, reusable LLM extraction tasks.

`xtrllm` separates two pieces that often get tangled together:

- **The engine** - prompt -> structured output -> validated result
- **The task** - schema + prompt strategy + domain-specific extraction rules

The engine ships with the package. The tasks live wherever your project keeps its extraction logic, and can be loaded at runtime.

## Installation

Install the latest stable release from PyPI:

```shell
pip install xtrllm
```

## Basic Shape

Register a directory of task files, choose a task and model, then call the extractor with the inputs expected by that task.

```python
from xtrllm import LLMXtractor, load_tasks

load_tasks("eulex/tasks", namespace="eulex")

extractor = LLMXtractor(
    task="eulex/classify_actor",
    model="gpt-4.1-mini",
)

result = extractor("Tribunale di Milano")
print(result.model_dump(mode="json"))
# {"actor_type": "ACT_TYPE_NAT_COURT"}
```

Each result is a Pydantic model, so downstream code receives typed, schema-validated data rather than raw model text.

For a complete walkthrough, including a full task definition and batch processing with a DataFrame, see the [Quickstart](quickstart.md).

## Citation

If you use this framework in academic research, please cite:

```tex
@misc{mandujano2026xtrllm,
  author       = {Mauricio Mandujano Manríquez},
  title        = {`xtrllm` - Extract Structured Data using LLMs},
  year         = {2026},
  howpublished = {\url{https://github.com/mauriciomm7/xtrllm}},
  note         = {GitHub repository}
}
```

## Acknowledgments

This project stands on the shoulders of excellent open-source tools and services:

- **Extraction Logo**
  Icon made by [Freepik](https://www.flaticon.com/authors/freepik) from [Flaticon](https://www.flaticon.com/free-icons/extraction).

- **CI/CD Automation - GitHub Actions**
  Powered by [GitHub Actions](https://github.com/features/actions), enabling automated build, test, and deployment pipelines directly within the GitHub ecosystem.

- **LLM CLI & Python Library**
  [`llm`](https://llm.datasette.io/en/stable/) by Simon Willison - a CLI tool and Python library for interacting with OpenAI, Anthropic Claude, Google Gemini, Meta Llama, and local language model APIs.

- **Pydantic**
  Built with [Pydantic](https://docs.pydantic.dev/) - data validation and settings management using Python type annotations, enabling robust schema enforcement and structured data handling.

## License

This project is licensed under the [MIT License](assets/LICENSE).
