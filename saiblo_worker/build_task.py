"""Contains the task for building agents."""

import logging
from typing import Optional

from saiblo_worker.base_agent_code_fetcher import BaseAgentCodeFetcher
from saiblo_worker.base_build_result_reporter import BaseBuildResultReporter
from saiblo_worker.base_docker_image_builder import BaseDockerImageBuilder
from saiblo_worker.base_task import BaseTask
from saiblo_worker.build_result import BuildResult


class BuildTask(BaseTask):
    """Task for building agents."""

    _builder: BaseDockerImageBuilder
    _code_id: str
    _fetcher: BaseAgentCodeFetcher
    _reporter: BaseBuildResultReporter
    _result: Optional[BuildResult] = None

    def __init__(
        self,
        code_id: str,
        fetcher: BaseAgentCodeFetcher,
        builder: BaseDockerImageBuilder,
        reporter: BaseBuildResultReporter,
    ):
        self._code_id = code_id

        self._fetcher = fetcher
        self._builder = builder
        self._reporter = reporter

    @property
    def result(self) -> Optional[BuildResult]:
        return self._result

    def __str__(self) -> str:
        return f"BuildTask(code_id={self._code_id})"

    async def execute(self) -> BuildResult:
        build_result: Optional[BuildResult] = None

        try:
            agent_code_tarball_path = await self._fetcher.fetch(self._code_id)

            build_result = await self._builder.build(
                self._code_id, agent_code_tarball_path
            )

        except Exception as e:  # pylint: disable=broad-except
            logging.error(
                "Failed to build agent code %s: (%s) %s", self._code_id, type(e), e
            )

            build_result = BuildResult(
                code_id=self._code_id,
                image=None,
                message=str(e),
            )

        await self._reporter.report(build_result)

        self._result = build_result

        return build_result


class BuildTaskFactory:
    """Factory for building BuildTask instances."""

    _builder: BaseDockerImageBuilder
    _fetcher: BaseAgentCodeFetcher
    _reporter: BaseBuildResultReporter

    def __init__(
        self,
        fetcher: BaseAgentCodeFetcher,
        builder: BaseDockerImageBuilder,
        reporter: BaseBuildResultReporter,
    ):
        self._fetcher = fetcher
        self._builder = builder
        self._reporter = reporter

    def create(self, code_id: str) -> BuildTask:
        """Creates a new BuildTask instance.

        Args:
            code_id: The ID of the agent code to build
        """

        return BuildTask(code_id, self._fetcher, self._builder, self._reporter)
