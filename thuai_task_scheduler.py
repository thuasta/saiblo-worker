from typing import Dict, List
import asyncio

from base_task import BaseTask
from base_task_scheduler import BaseTaskScheduler
from compile_task import CompileTask
from judge_task import JudgeTask
import uuid

COMPILATION_TASK_PARALLELISM = 5
JUDGE_TASK_PARALLELISM = 2

class ThuaiTaskScheduler(BaseTaskScheduler):
    """Concrete implementation of a task scheduler."""
    
    _compilation_tasks: Dict[str, CompileTask]
    _judge_tasks: Dict[str, JudgeTask]
    _compilation_tasks_queue: asyncio.Queue
    _judge_tasks_queue: asyncio.Queue
    _compilation_tasks_loop: asyncio.Task
    _judge_tasks_loop: asyncio.Task
    

    def __init__(self) -> None:
        """Initialize the task scheduler."""
        self._compilation_tasks = {}
        self._judge_tasks = {}
        self._compilation_tasks_queue = asyncio.Queue()
        self._judge_tasks_queue = asyncio.Queue()

    async def clean(self) -> None:
        """Cleans up scheduled tasks."""
        self._compilation_tasks = {}
        self._judge_tasks = {}
        self._compilation_tasks_queue = asyncio.Queue()
        self._judge_tasks_queue = asyncio.Queue()

    async def list(self) -> List[BaseTask]:
        """Lists all the tasks that have been scheduled."""
        return list(self._compilation_tasks.values()) + list(self._judge_tasks.values())

    async def schedule(self, task: BaseTask) -> str:
        """Schedules a task."""
        # generate uuid for the task
        task_id = str(uuid.uuid4())
        # distinguish the type of task
        if isinstance(task, CompileTask):
            self._compilation_tasks[task_id] = task
            self._compilation_tasks_queue.put_nowait(task)
            task_id = "compilation_task_{}".format(task_id)
        elif isinstance(task, JudgeTask):
            self._judge_tasks[task_id] = task
            self._judge_tasks_queue.put_nowait(task)
            task_id = "judge_task_{}".format(task_id)
        else:
            raise ValueError("Invalid task type.")
        print("Scheduled task: {}".format(task_id))
        return task_id
    
    async def task_loop(self, scheduled_tasks_queue: asyncio.Queue) -> None:
        """Loop for executing compilation tasks."""
        print("Task loop started.")
        while True:
            tasks = []
            # get the tasks from the queue
            for _ in range(COMPILATION_TASK_PARALLELISM):
                try:
                    task: BaseTask = scheduled_tasks_queue.get_nowait()
                    tasks.append(task.execute())
                except asyncio.QueueEmpty:
                    break
            if not tasks:
                await asyncio.sleep(1)
                continue
            # wait for the tasks to finish
            print("Waiting for tasks {} to finish.".format(tasks))
            await asyncio.gather(*tasks)

    async def start(self) -> None:
        """Starts the task scheduler and begins executing tasks."""
        self._compilation_tasks_loop = asyncio.create_task(self.task_loop(self._compilation_tasks_queue))
        self._judge_tasks_loop = asyncio.create_task(self.task_loop(self._judge_tasks_queue))
        await self._compilation_tasks_loop
        await self._judge_tasks_loop
