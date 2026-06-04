# `xtrllm` - Extract Structured Data using LLMs

A lightweight Python framework for portable, versioned, reusable LLM extraction tasks.

``xtrllm`` separates two things every other library conflates:

- **The engine** — prompt → structured output → log (stable, ships with the package)
- **The task** — schema + prompt strategy + edge case handling (yours, lives in your repo)

## 🛠️ Installation

Install the latest stable release directly from PyPI using pip:

```shell
pip install xtrllm
```

## 🗜️ Basic Usage

``xtrllm`` tasks can be defined in one Python file, then loaded and run through an LLMXtractor, with the output validated against the schema before it is returned.

```python
# eulex/tasks/classify_actor.py
from pydantic import BaseModel
from xtrllm.core.base import BaseTask

class ActorLabelSchema(BaseModel):
    value: str

class ClassifyActorTask(BaseTask):
    name = "classify_actor"
    schema = ActorLabelSchema
    system_prompt = "Classify legal and institutional actors."

    def build_prompt(self, text: str) -> str:
        return f"Classify this actor: {text}"
```

Once this is set up you can easily run it:

```python
import xtrllm
from xtrllm import load_tasks, LLMXtractor

load_tasks("eulex/tasks", namespace="eulex")

extractor = LLMXtractor(task="eulex/classify_actor", model="gpt-4.1-mini")
result = extractor("European Commission")

print(result.value)

```

## 🎓 Citation

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

## 🙏 Acknowledgments

This project stands on the shoulders of excellent open-source tools and services:

- 🎨 **Extraction Logo**  
  Icon made by [Freepik](https://www.flaticon.com/authors/freepik) from [Flaticon](https://www.flaticon.com/free-icons/extraction).  

- ⚙️ **CI/CD Automation — GitHub Actions**  
  Powered by [GitHub Actions](https://github.com/features/actions), enabling automated build, test, and deployment pipelines directly within the GitHub ecosystem.

- 🤖 **LLM CLI & Python Library**  
  [`llm`](https://llm.datasette.io/en/stable/) by Simon Willison — A CLI tool and Python library for interacting with OpenAI, Anthropic Claude, Google Gemini, Meta Llama, and local language model APIs.

- 🧩 **Pydantic**  
  Built with [Pydantic](https://docs.pydantic.dev/) — Data validation and settings management using Python type annotations, enabling robust schema enforcement and structured data handling.

## 📄 License

This project is licensed under the [MIT License](assets/LICENSE).
