"""Contains the task for judging matches."""

import asyncio
from dataclasses import dataclass
from typing import List, Optional

from base_agent_code_fetcher import BaseAgentCodeFetcher
from base_compile_result_sender import BaseCompileResultSender
from base_docker_image_builder import BaseDockerImageBuilder
from base_task import BaseTask
from build_task import BuildTask


@dataclass
class CompileTask(BaseTask):
    """Task for compiling a code and send compile result to server."""

    _code_id: str
    _build_task: BuildTask
    _sender: BaseCompileResultSender
    _result: Optional[str] = None

    def __init__(
        self,
        code_id: str,
        fetcher: BaseAgentCodeFetcher,
        builder: BaseDockerImageBuilder,
        sender: BaseCompileResultSender,
    ):
        self._code_id = code_id
        self._build_task = BuildTask(code_id, fetcher, builder)
        self._sender = sender

    async def execute(self) -> str:
        """Runs the task.

        Returns:
            The code compile result.
            Empty string if compile successfully.
            Error message if compile failed.
        """

        compile_result = await self._build_task.execute()
        if compile_result.split(":")[0] == "E":
            self._result = compile_result[2:]
            await self._sender.send(self._code_id, False, self._result)
            return compile_result[2:]
        self._result = ""
        await self._sender.send(self._code_id, True, self._result)
        return ""

    @property
    def result(self) -> Optional[str]:
        """The code compile result"""
        return self._result
