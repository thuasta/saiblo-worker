"""The implementation of the Saiblo client."""

import asyncio
import json

import websockets.asyncio.client
from websockets import ClientConnection, ConnectionClosed

from base_agent_code_fetcher import BaseAgentCodeFetcher
from base_build_result_reporter import BaseBuildResultReporter
from base_docker_image_builder import BaseDockerImageBuilder
from base_match_judger import BaseMatchJudger
from base_match_result_reporter import BaseMatchResultReporter
from base_saiblo_client import BaseSaibloClient
from base_task_scheduler import BaseTaskScheduler
from build_task import BuildTask
from judge_task import JudgeTask

_CHECK_TASK_SCHEDULER_IDLE_INTERVAL = 1
_SEND_HEART_BEAT_INTERVAL = 3


class SaibloClient(BaseSaibloClient):
    """The Saiblo client."""

    _name: str
    _agent_code_fetcher: BaseAgentCodeFetcher
    _build_result_reporter: BaseBuildResultReporter
    _docker_image_builder: BaseDockerImageBuilder
    _game_host_image: str
    _match_judger: BaseMatchJudger
    _match_result_reporter: BaseMatchResultReporter
    _request_judge_task_condition: asyncio.Condition = asyncio.Condition()
    _task_scheduler: BaseTaskScheduler
    _websocket_url: str

    def __init__(
        self,
        name: str,
        websocket_url: str,
        task_scheduler: BaseTaskScheduler,
        game_host_image: str,
        agent_code_fetcher: BaseAgentCodeFetcher,
        build_result_reporter: BaseBuildResultReporter,
        docker_image_builder: BaseDockerImageBuilder,
        match_judger: BaseMatchJudger,
        match_result_reporter: BaseMatchResultReporter,
    ):
        self._name = name
        self._websocket_url = websocket_url
        self._task_scheduler = task_scheduler
        self._game_host_image = game_host_image
        self._agent_code_fetcher = agent_code_fetcher
        self._build_result_reporter = build_result_reporter
        self._docker_image_builder = docker_image_builder
        self._match_judger = match_judger
        self._match_result_reporter = match_result_reporter

    async def start(self) -> None:
        async for connection in websockets.asyncio.client.connect(self._websocket_url):
            try:
                await connection.send(
                    json.dumps(
                        {
                            "type": "init",
                            "data": {
                                "description": self._name,
                                "address": "",
                            },
                        }
                    )
                )

                await asyncio.gather(
                    self._keep_receive_message(connection),
                    self._keep_request_judge_task(connection),
                    self._keep_heart_beat(connection),
                )

            except ConnectionClosed:
                continue

    async def _keep_finish_judge_task(self, connection: ClientConnection) -> None:
        while True:
            done_task = await self._task_scheduler.pop_done_task()

            if isinstance(done_task, JudgeTask):
                await connection.send(
                    json.dumps(
                        {
                            "type": "finish_judge_task",
                            "data": {
                                "match_id": done_task.match_id,
                            },
                        }
                    )
                )

    async def _keep_receive_message(self, connection: ClientConnection) -> None:
        while True:
            message = json.loads(await connection.recv())

            match message["type"]:
                case "compilation_task":
                    task = BuildTask(
                        message["data"]["code_id"],
                        self._agent_code_fetcher,
                        self._docker_image_builder,
                        self._build_result_reporter,
                    )

                    await self._task_scheduler.schedule(task)

                case "judge_task":
                    self._request_judge_task_condition.notify()

                    task = JudgeTask(
                        message["data"]["match_id"],
                        self._game_host_image,
                        [x["code_id"] for x in message["data"]["players"]],
                        self._agent_code_fetcher,
                        self._docker_image_builder,
                        self._build_result_reporter,
                        self._match_judger,
                        self._match_result_reporter,
                    )

                    await self._task_scheduler.schedule(task)

    async def _keep_request_judge_task(self, connection: ClientConnection) -> None:
        while True:
            if not self._task_scheduler.idle:
                await asyncio.sleep(_CHECK_TASK_SCHEDULER_IDLE_INTERVAL)
                continue

            await connection.send(
                json.dumps(
                    {
                        "type": "request_judge_task",
                        "data": {
                            "queue": 0,
                        },
                    }
                )
            )

            async with self._request_judge_task_condition:
                await self._request_judge_task_condition.wait()

    async def _keep_heart_beat(self, connection: ClientConnection) -> None:
        while True:
            await connection.send(
                json.dumps(
                    {
                        "type": "heart_beat",
                    }
                )
            )

            await asyncio.sleep(_SEND_HEART_BEAT_INTERVAL)
