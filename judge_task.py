"""Contains the task for judging matches."""

import asyncio
from dataclasses import dataclass
from typing import List, Optional

from base_agent_code_fetcher import BaseAgentCodeFetcher
from base_build_result_reporter import BaseBuildResultReporter
from base_docker_image_builder import BaseDockerImageBuilder
from base_match_judger import BaseMatchJudger
from base_match_result_reporter import BaseMatchResultReporter
from base_task import BaseTask
from build_task import BuildTask
from match_result import MatchResult


@dataclass
class JudgeTask(BaseTask):
    """Task for judging a match."""

    _builder: BaseDockerImageBuilder
    _build_result_reporter: BaseBuildResultReporter
    _agent_code_ids: List[str]
    _fetcher: BaseAgentCodeFetcher
    _game_host_image_tag: str
    _judger: BaseMatchJudger
    _match_id: str
    _match_result_reporter: BaseMatchResultReporter
    _result: Optional[MatchResult] = None

    def __init__(
        self,
        match_id: str,
        game_host_image: str,
        agent_code_ids: List[str],
        fetcher: BaseAgentCodeFetcher,
        builder: BaseDockerImageBuilder,
        build_result_reporter: BaseBuildResultReporter,
        judger: BaseMatchJudger,
        match_result_reporter: BaseMatchResultReporter,
    ):
        self._match_id = match_id
        self._game_host_image_tag = game_host_image
        self._agent_code_ids = agent_code_ids

        self._fetcher = fetcher
        self._builder = builder
        self._build_result_reporter = build_result_reporter
        self._judger = judger
        self._match_result_reporter = match_result_reporter

    @property
    def match_id(self) -> str:
        """The ID of the match to judge."""

        return self._match_id

    async def execute(self) -> MatchResult:
        agent_build_results = await asyncio.gather(
            *[
                BuildTask(
                    code_id,
                    self._fetcher,
                    self._builder,
                    self._build_result_reporter,
                ).execute()
                for code_id in self._agent_code_ids
            ]
        )

        match_result = await self._judger.judge(
            self._match_id,
            self._game_host_image_tag,
            [x.image for x in agent_build_results],
        )

        await self._match_result_reporter.report(match_result)

        self._result = match_result

        return match_result

    @property
    def result(self) -> Optional[MatchResult]:
        return self._result
