"""Contains the base classes for task schedulers."""

from abc import ABC, abstractmethod
from typing import List

from base_task import BaseTask


class BaseTaskScheduler(ABC):
    """Abstract base class for task schedulers."""

    @abstractmethod
    async def clean(self) -> None:
        """Cleans up scheduled tasks."""
        raise NotImplementedError

    @abstractmethod
    async def list(self) -> List[BaseTask]:
        """Lists all the tasks that have been scheduled.

        Returns:
            A list of tasks
        """
        raise NotImplementedError

    @abstractmethod
    async def schedule(self, task: BaseTask) -> str:
        """Schedules a task.

        If there are already some tasks running, the task will be scheduled after the current tasks
        are finished.

        Args:
            task: The task to schedule

        Returns:
            The ID of the scheduled task
        """
        raise NotImplementedError

    @abstractmethod
    async def start(self) -> None:
        """Starts the task scheduler.

        This method should be called to start the task scheduler and begin executing tasks. This
        method will block forever.
        """
        raise NotImplementedError
