"""Contains the task for judging matches."""

from dataclasses import dataclass
from typing import List, Optional

from saiblo_worker.base_agent_code_fetcher import BaseAgentCodeFetcher
from saiblo_worker.base_build_result_reporter import BaseBuildResultReporter
from saiblo_worker.base_docker_image_builder import BaseDockerImageBuilder
from saiblo_worker.base_match_judger import BaseMatchJudger
from saiblo_worker.base_match_result_reporter import BaseMatchResultReporter
from saiblo_worker.base_task import BaseTask
from saiblo_worker.build_result import BuildResult
from saiblo_worker.build_task import BuildTask
from saiblo_worker.match_result import MatchResult


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

    @property
    def result(self) -> Optional[MatchResult]:
        return self._result

    def __str__(self) -> str:
        return f"JudgeTask(match_id={self._match_id})"

    async def execute(self) -> MatchResult:
        match_result: Optional[MatchResult] = None

        try:
            cached_agent_build_results = await self._builder.list()

            agent_build_results = [
                (
                    await BuildTask(
                        code_id,
                        self._fetcher,
                        self._builder,
                        self._build_result_reporter,
                    ).execute()
                    if code_id not in cached_agent_build_results
                    else BuildResult(
                        code_id=code_id,
                        image=cached_agent_build_results[code_id],
                        message="",
                    )
                )
                for code_id in self._agent_code_ids
            ]

            match_result = await self._judger.judge(
                self._match_id,
                self._game_host_image_tag,
                [x.image for x in agent_build_results],
            )

        except Exception as e:  # pylint: disable=broad-except
            match_result = MatchResult(
                match_id=self._match_id,
                agent_results=[
                    MatchResult.AgentResult(
                        exit_code=0,
                        score=0.0,
                        status="UE",
                        stderr_output="",
                    )
                    for _ in self._agent_code_ids
                ],
                error_message=str(e),
                replay_file_path=None,
                stderr_output="",
            )

        await self._match_result_reporter.report(match_result)

        self._result = match_result

        return match_result


class JudgeTaskFactory:
    """Factory for building JudgeTask instances."""

    _builder: BaseDockerImageBuilder
    _build_result_reporter: BaseBuildResultReporter
    _fetcher: BaseAgentCodeFetcher
    _game_host_image: str
    _judger: BaseMatchJudger
    _match_result_reporter: BaseMatchResultReporter

    def __init__(
        self,
        game_host_image: str,
        fetcher: BaseAgentCodeFetcher,
        builder: BaseDockerImageBuilder,
        build_result_reporter: BaseBuildResultReporter,
        judger: BaseMatchJudger,
        match_result_reporter: BaseMatchResultReporter,
    ):
        self._game_host_image = game_host_image
        self._fetcher = fetcher
        self._builder = builder
        self._build_result_reporter = build_result_reporter
        self._judger = judger
        self._match_result_reporter = match_result_reporter

    def create(
        self,
        match_id: str,
        agent_code_ids: List[str],
    ) -> JudgeTask:
        """Creates a new JudgeTask instance.

        Args:
            match_id: The ID of the match to judge
            agent_code_ids: The IDs of the agent code to use in the match
        """

        return JudgeTask(
            match_id,
            self._game_host_image,
            agent_code_ids,
            self._fetcher,
            self._builder,
            self._build_result_reporter,
            self._judger,
            self._match_result_reporter,
        )
