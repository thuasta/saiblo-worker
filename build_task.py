"""Contains the task for building agents."""

import logging
from typing import Optional

from base_agent_code_fetcher import BaseAgentCodeFetcher
from base_compile_result_sender import BaseCompileResultSender
from base_docker_image_builder import BaseDockerImageBuilder
from base_task import BaseTask


class BuildTask(BaseTask):
    """Task for building agents."""

    _builder: BaseDockerImageBuilder
    _code_id: str
    _fetcher: BaseAgentCodeFetcher
    _result: Optional[str] = None
    _sender: Optional[BaseCompileResultSender]

    def __init__(
        self,
        code_id: str,
        fetcher: BaseAgentCodeFetcher,
        builder: BaseDockerImageBuilder,
        sender: BaseCompileResultSender = None,
    ):
        self._code_id = code_id

        self._fetcher = fetcher
        self._builder = builder
        self._sender = sender

    async def execute(self) -> str:
        """Runs the task.

        Returns:
            The tag of the built image
        """
        tar_file_path = await self._fetcher.fetch(self._code_id)
        try:
            self._result = await self._builder.build(tar_file_path, self._code_id)
            if self._sender:
                await self._sender.send(self._code_id, True, "")
        except Exception as e:
            logging.error(f"Failed to build agent {self._code_id}: {e}")
            if self._sender:
                await self._sender.send(self._code_id, False, str(e))
            # raise e
        return self._result

    @property
    def result(self) -> Optional[str]:
        """The tag of the built image"""
        return self._result
