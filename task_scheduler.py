"""The implementation of the task scheduler."""

import asyncio
import logging

from base_task import BaseTask
from base_task_scheduler import BaseTaskScheduler


class TaskScheduler(BaseTaskScheduler):
    """The task scheduler"""

    _done_tasks: asyncio.Queue[BaseTask] = asyncio.Queue()
    _pending_tasks: asyncio.Queue[BaseTask] = asyncio.Queue()

    def __init__(self) -> None:
        pass

    @property
    def idle(self) -> bool:
        return self._pending_tasks.empty()

    async def clean(self) -> None:
        while not self._pending_tasks.empty():
            self._pending_tasks.get_nowait()
            self._pending_tasks.task_done()

        while not self._done_tasks.empty():
            self._done_tasks.get_nowait()
            self._done_tasks.task_done()

    async def pop_done_task(self) -> BaseTask:
        task = await self._done_tasks.get()

        self._done_tasks.task_done()

        return task

    async def schedule(self, task: BaseTask) -> None:
        await self._pending_tasks.put(task)

    async def start(self) -> None:
        while True:
            task = await self._pending_tasks.get()

            try:
                await task.execute()
            except Exception as e:  # pylint: disable=broad-except
                logging.error("Task %s failed: %s", type(task).__name__, str(e))

            self._pending_tasks.task_done()

            await self._done_tasks.put(task)
