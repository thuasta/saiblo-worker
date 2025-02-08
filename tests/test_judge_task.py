"""Tests for the judge_task module."""

import dataclasses
import json
import pathlib
import shutil
import unittest

import aiohttp
import docker
import docker.models.containers

from agent_code_fetcher import AgentCodeFetcher
from build_result_reporter import BuildResultReporter
from docker_image_builder import DockerImageBuilder
from judge_task import JudgeTaskFactory
from match_judger import MatchJudger
from match_result import MatchResult
from match_result_reporter import MatchResultReporter

CODE_ID = "7c562b10-287f-44c0-8fc4-0cf853a1859b"
HTTP_BASE_URL = "https://api.dev.saiblo.net"
MATCH_ID = "7729"


class TestJudgeTask(unittest.IsolatedAsyncioTestCase):
    """Tests for the JudgeTask class."""

    _judge_task_factory: JudgeTaskFactory
    _docker_client: docker.DockerClient
    _session: aiohttp.ClientSession

    async def asyncSetUp(self) -> None:
        self._docker_client = docker.from_env()
        self._session = aiohttp.ClientSession(HTTP_BASE_URL)

        self._judge_task_factory = JudgeTaskFactory(
            "saiblo-worker-image:game-host",
            AgentCodeFetcher(self._session),
            DockerImageBuilder(),
            BuildResultReporter(self._session),
            MatchJudger(
                agent_mem_limit="1g",
                agent_cpus=1,
                game_host_mem_limit="1g",
                game_host_cpus=1,
                judge_timeout=60,
            ),
            MatchResultReporter(self._session),
        )

        self._clean()

    async def asyncTearDown(self) -> None:
        self._clean()

        await self._session.close()

    async def test_execute(self):
        """Test execute()."""
        # Arrange.
        agent_code_tarball_path = pathlib.Path(f"data/agent_code/{CODE_ID}.tar")
        agent_code_tarball_path.parent.mkdir(parents=True, exist_ok=True)
        agent_code_tarball_path.touch()

        image = self._docker_client.images.pull("hello-world")
        image.tag("saiblo-worker-image", CODE_ID)

        match_replay_path = pathlib.Path(f"data/match_replays/{MATCH_ID}.dat")
        match_replay_path.parent.mkdir(parents=True, exist_ok=True)
        match_replay_path.touch()

        match_result = MatchResult(
            match_id=MATCH_ID,
            agent_results=[],
            error_message="error_message",
            replay_file_path=None,
            stderr_output="stderr_output",
        )
        match_result_path = pathlib.Path(f"data/match_results/{MATCH_ID}.json")
        match_result_path.parent.mkdir(parents=True, exist_ok=True)
        with open(match_result_path, "w", encoding="utf-8") as file:
            json.dump(
                dataclasses.asdict(match_result),
                file,
            )

        judge_task = self._judge_task_factory.create(MATCH_ID, [CODE_ID, CODE_ID])

        # Assert.
        self.assertIsNone(judge_task.result)

        # Act.
        returned_result = await judge_task.execute()
        property_match_id = judge_task.match_id
        property_result = judge_task.result

        # Assert.
        self.assertEqual(property_match_id, MATCH_ID)
        self.assertEqual(property_result, returned_result)
        self.assertEqual(returned_result, match_result)

    def _clean(self) -> None:
        """Clean up the environment."""

        shutil.rmtree(
            pathlib.Path("data"),
            ignore_errors=True,
        )

        for network in self._docker_client.networks.list():
            if network.name is not None and network.name.startswith(
                "saiblo-worker-network-"
            ):
                network.remove()

        for container in self._docker_client.containers.list(all=True):
            assert isinstance(container, docker.models.containers.Container)
            if container.name is not None and (
                container.name.startswith("saiblo-worker-agent-")
                or container.name.startswith("saiblo-worker-game-host-")
            ):
                container.stop(timeout=0)
                container.remove(v=True, force=True)

        for image in self._docker_client.images.list("saiblo-worker-image"):
            image.remove(force=True)
