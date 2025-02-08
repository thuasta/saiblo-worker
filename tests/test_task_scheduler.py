"""Tests for task_scheduler module."""

import asyncio
import unittest

from saiblo_worker.base_task import BaseTask
from saiblo_worker.task_scheduler import TaskScheduler


class _TestTask(BaseTask):
    async def execute(self) -> None:
        pass

    @property
    def result(self) -> None:
        pass


class _TestTaskThrow(BaseTask):
    async def execute(self) -> None:
        raise RuntimeError()

    @property
    def result(self) -> None:
        pass


class TestTaskScheduler(unittest.IsolatedAsyncioTestCase):
    """Tests for TaskScheduler class."""

    async def test_idle_no_pending_tasks(self):
        """Test property idle when there are no pending tasks."""
        # Arrange.
        task_scheduler = TaskScheduler()

        # Act.
        result = task_scheduler.idle

        # Assert.
        self.assertTrue(result)

    async def test_idle_pending_tasks(self):
        """Test property idle when there are pending tasks."""
        # Arrange.
        task_scheduler = TaskScheduler()
        await task_scheduler.schedule(_TestTask())

        # Act.
        result = task_scheduler.idle

        # Assert.
        self.assertFalse(result)

    async def test_clean_pending_tasks(self):
        """Test clean() when there are pending tasks."""
        # Arrange.
        task_scheduler = TaskScheduler()
        await task_scheduler.schedule(_TestTask())

        # Act.
        await task_scheduler.clean()

        # Assert.
        self.assertTrue(task_scheduler.idle)

    async def test_clean_done_tasks(self):
        """Test clean() when there are done tasks."""
        # Arrange.
        task_scheduler = TaskScheduler()
        await task_scheduler._done_tasks.put(  # pylint: disable=protected-access
            _TestTask()
        )

        # Act.
        await task_scheduler.clean()

        # Assert.
        self.assertTrue(task_scheduler.idle)

    async def test_pop_done_task(self):
        """Test pop_done_task()."""
        # Arrange.
        task_scheduler = TaskScheduler()
        task = _TestTask()
        await task_scheduler._done_tasks.put(task)  # pylint: disable=protected-access

        # Act.
        result = await task_scheduler.pop_done_task()

        # Assert.
        self.assertEqual(result, task)

    async def test_schedule(self):
        """Test schedule()."""
        # Arrange.
        task_scheduler = TaskScheduler()
        task = _TestTask()

        # Act.
        await task_scheduler.schedule(task)

        # Assert.
        self.assertFalse(task_scheduler.idle)

    async def test_start_task_success(self):
        """Test start() when task is successful."""
        # Arrange.
        task_scheduler = TaskScheduler()
        task = _TestTask()
        await task_scheduler.schedule(task)

        # Act.
        asyncio_task = asyncio.create_task(task_scheduler.start())
        await asyncio.sleep(1)
        asyncio_task.cancel()

        # Assert.
        self.assertTrue(task_scheduler.idle)

    async def test_start_task_failure(self):
        """Test start() when task fails."""
        # Arrange.
        task_scheduler = TaskScheduler()
        task = _TestTaskThrow()
        await task_scheduler.schedule(task)

        # Act.
        asyncio_task = asyncio.create_task(task_scheduler.start())
        await asyncio.sleep(1)
        asyncio_task.cancel()

        # Assert.
        self.assertTrue(task_scheduler.idle)
