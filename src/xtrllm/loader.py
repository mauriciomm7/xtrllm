# src/xtrllm/loader.py
import importlib.util
import inspect
from pathlib import Path

from xtrllm.core.base import BaseTask
from xtrllm.core.registry import registry


def load_tasks(path: str, namespace: str | None = None) -> None:
    task_dir = Path(path).resolve()

    if not task_dir.exists():
        raise FileNotFoundError(f"Task directory not found: {task_dir}")

    if not task_dir.is_dir():
        raise NotADirectoryError(f"Expected a task directory, got: {task_dir}")

    ns = namespace or task_dir.name

    for file in sorted(task_dir.glob("*.py")):
        if file.name.startswith("_"):
            continue

        source = str(file.resolve())
        module_name = f"xtrllm._tasks.{ns}.{file.stem}"

        spec = importlib.util.spec_from_file_location(module_name, file)
        if spec is None or spec.loader is None:
            continue  # guard — skip unloadable files

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore

        for _, obj in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(obj, BaseTask)
                and obj is not BaseTask
                and hasattr(obj, "name")
            ):
                # Guard against double-namespacing on repeated load_tasks() calls
                if "/" not in obj.name:
                    obj.name = f"{ns}/{obj.name}"
                registry.register(obj, source=source)
