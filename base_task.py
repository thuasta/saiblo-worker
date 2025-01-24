"""Contains the base classes for tasks."""

from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseTask(ABC):
    """Abstract base class for tasks."""

    @abstractmethod
    async def execute(self) -> Any:
        """Runs the task.

        Returns:
            The task execution result
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def result(self) -> Optional[Any]:
        """The task execution result."""
        raise NotImplementedError
