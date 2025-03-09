"""Contains the base classes for tasks."""

from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseTask(ABC):
    """Abstract base class for tasks."""

    @property
    @abstractmethod
    def result(self) -> Optional[Any]:
        """The task execution result."""

    @abstractmethod
    def __str__(self) -> str:
        """Returns a string representation of the task."""

    @abstractmethod
    async def execute(self) -> Any:
        """Runs the task.

        Returns:
            The task execution result
        """
