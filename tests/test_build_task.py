"""Tests for the build_task module."""

import pathlib
import shutil
import unittest

import aiohttp
import docker
import docker.models.containers

from agent_code_fetcher import AgentCodeFetcher
from build_result_reporter import BuildResultReporter
from build_task import BuildTaskFactory
from docker_image_builder import DockerImageBuilder

CODE_ID = "7c562b10-287f-44c0-8fc4-0cf853a1859b"
HTTP_BASE_URL = "https://api.dev.saiblo.net"


class TestBuildTask(unittest.IsolatedAsyncioTestCase):
    """Tests for the BuildTask class."""

    _build_task_factory: BuildTaskFactory
    _docker_client: docker.DockerClient
    _session: aiohttp.ClientSession

    async def asyncSetUp(self) -> None:
        self._docker_client = docker.from_env()
        self._session = aiohttp.ClientSession(HTTP_BASE_URL)

        self._build_task_factory = BuildTaskFactory(
            AgentCodeFetcher(self._session),
            DockerImageBuilder(),
            BuildResultReporter(self._session),
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

        build_task = self._build_task_factory.create(CODE_ID)

        # Assert.
        self.assertIsNone(build_task.result)

        # Act.
        returned_result = await build_task.execute()
        property_result = build_task.result

        # Assert.
        self.assertEqual(property_result, returned_result)

        self.assertEqual(returned_result.code_id, CODE_ID)
        self.assertTrue(returned_result.image, f"saiblo-worker-image:{CODE_ID}")
        self.assertEqual(returned_result.message, "")

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
