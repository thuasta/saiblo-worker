"""Contains the base classes for task schedulers."""

from abc import ABC, abstractmethod

from base_task import BaseTask


class BaseTaskScheduler(ABC):
    """Abstract base class for task schedulers."""

    @property
    @abstractmethod
    def idle(self) -> bool:
        """Whether the scheduler is idle."""
        raise NotImplementedError

    @abstractmethod
    async def clean(self) -> None:
        """Cleans up scheduled tasks."""
        raise NotImplementedError

    @abstractmethod
    async def pop_done_task(self) -> BaseTask:
        """Pops a task that has been finished.

        Returns:
            The task that has been finished
        """
        raise NotImplementedError

    @abstractmethod
    async def schedule(self, task: BaseTask) -> None:
        """Schedules a task.

        If there are already some tasks running, the task will be scheduled after the current tasks
        are finished.

        Args:
            task: The task to schedule
        """
        raise NotImplementedError

    @abstractmethod
    async def start(self) -> None:
        """Starts the task scheduler.

        This method should be called to start the task scheduler and begin executing tasks. This
        method will block forever.
        """
        raise NotImplementedError
