"""Contains the task for judging matches."""

import asyncio
from dataclasses import dataclass
from typing import List, Optional

from base_agent_code_fetcher import BaseAgentCodeFetcher
from base_docker_image_builder import BaseDockerImageBuilder
from base_match_judger import BaseMatchJudger
from base_match_result_reporter import BaseMatchResultReporter
from base_task import BaseTask
from build_task import BuildTask
from match_result import MatchResult


@dataclass
class JudgeTask(BaseTask):
    """Task for judging a match."""

    _build_tasks: List[BuildTask]
    _game_host_image_tag: str
    _judger: BaseMatchJudger
    _match_id: str
    _reporter: BaseMatchResultReporter
    _result: Optional[MatchResult] = None

    def __init__(
        self,
        match_id: str,
        player_code_ids: List[str],
        game_host_image_tag: str,
        fetcher: BaseAgentCodeFetcher,
        builder: BaseDockerImageBuilder,
        judger: BaseMatchJudger,
        reporter: BaseMatchResultReporter,
    ):
        self._match_id = match_id
        self._game_host_image_tag = game_host_image_tag

        self._judger = judger
        self._reporter = reporter

        self._build_tasks = [
            BuildTask(code_id, fetcher, builder, None) for code_id in player_code_ids
        ]

    async def execute(self) -> MatchResult:
        """Runs the task.

        Returns:
            The match judge result
        """
        try:
            agent_image_tags = await asyncio.gather(
                *[t.execute() for t in self._build_tasks]
            )
            match_result = await self._judger.judge(
                self._match_id, self._game_host_image_tag, agent_image_tags
            )
            await self._reporter.report(match_result)
            self._result = match_result
            return match_result
        except asyncio.CancelledError:
            print("Task cancelled.")
            self._judger.stop()
            raise
        except Exception as e:
            # If any build task failed, the match is judged as failed.
            match_result = MatchResult(
                match_id=self._match_id,
                success=False,
                err_msg=str(e),
                scores=[0] * len(self._build_tasks),
                record_file_path=None,
                states=[
                    {"position": i, "status": "OK", "code": 0, "stderr": ""}
                    for i in range(len(self._build_tasks))
                ],
            )
            await self._reporter.report(match_result)
            self._result = match_result
            return match_result

    @property
    def result(self) -> Optional[MatchResult]:
        """The match judge result"""
        return self._result
