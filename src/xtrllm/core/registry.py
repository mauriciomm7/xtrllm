# src/xtrllm/core/registry.py
from xtrllm.core.base import BaseTask


class DuplicateTaskError(Exception):
    pass


class TaskRegistry:
    def __init__(self):
        self._tasks: dict[str, tuple[type[BaseTask], str]] = {}
        # self._tasks; stores {task_name: (task_class, source_path)}

    def register(self, task_class: type[BaseTask], source: str) -> None:
        if not hasattr(task_class, "name"):
            raise ValueError(f"Task class '{task_class.__name__}' has no 'name' attribute.")
        
        name = task_class.name

        if name in self._tasks:
            _, registered_source = self._tasks[name]
            if registered_source == source:
                self._tasks[name] = (task_class, source)  # Same source overwrite, don't skip for Iterative DEV
                print(f"Reloaded: {source}" )
                return 
            raise DuplicateTaskError(
                f"Task '{name}' already registered from '{registered_source}'. "
                f"Cannot register again from '{source}'."
            )

        self._tasks[name] = (task_class, source)

    def get(self, name: str) -> type[BaseTask]:
        if name not in self._tasks:
            raise KeyError(f"Task '{name}' not found. Did you call load_tasks()?")
        task_class, _ = self._tasks[name]
        return task_class

    def all(self) -> list[str]:
        return list(self._tasks.keys())

# Global singleton — one registry per session
registry = TaskRegistry()
