"""Contains the task for building agents."""

from typing import Optional

from base_agent_code_fetcher import BaseAgentCodeFetcher
from base_docker_image_builder import BaseDockerImageBuilder
from base_task import BaseTask


class BuildTask(BaseTask):
    """Task for building agents."""

    _builder: BaseDockerImageBuilder
    _code_id: str
    _fetcher: BaseAgentCodeFetcher
    _result: Optional[str] = None

    def __init__(
        self,
        code_id: str,
        fetcher: BaseAgentCodeFetcher,
        builder: BaseDockerImageBuilder,
    ):
        self._code_id = code_id

        self._fetcher = fetcher
        self._builder = builder

    async def execute(self) -> str:
        """Runs the task.

        Returns:
            The tag of the built image
        """
        tar_file_path = await self._fetcher.fetch(self._code_id)
        self._result = await self._builder.build(tar_file_path)
        return self._result

    @property
    def result(self) -> Optional[str]:
        """The tag of the built image"""
        return self._result
