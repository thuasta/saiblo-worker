"""Contains the task for building agents."""

import logging
from typing import Optional

from base_agent_code_fetcher import BaseAgentCodeFetcher
from base_build_result_reporter import BaseBuildResultReporter
from base_docker_image_builder import BaseDockerImageBuilder
from base_task import BaseTask
from build_result import BuildResult


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

    async def execute(self) -> BuildResult:
        logging.info("Fetching agent code %s", self._code_id)
        agent_code_tarball_path = await self._fetcher.fetch(self._code_id)

        logging.info("Building agent code %s", self._code_id)
        build_result = await self._builder.build(self._code_id, agent_code_tarball_path)

        logging.info("Reporting build result for agent code %s", self._code_id)
        await self._reporter.report(build_result)

        self._result = build_result

        return build_result

    @property
    def result(self) -> Optional[BuildResult]:
        return self._result


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
