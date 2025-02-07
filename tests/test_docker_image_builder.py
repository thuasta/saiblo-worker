"""Tests for the docker_image_builder module."""

import io
import pathlib
import shutil
import tarfile
import unittest

import aiohttp
import docker

from docker_image_builder import DockerImageBuilder

CODE_ID = "7c562b10-287f-44c0-8fc4-0cf853a1859b"


class TestDockerImageBuilder(unittest.IsolatedAsyncioTestCase):
    """Tests for the DockerImageBuilder class."""

    _docker_client: docker.DockerClient
    _session: aiohttp.ClientSession

    async def asyncSetUp(self) -> None:
        shutil.rmtree(
            pathlib.Path("data"),
            ignore_errors=True,
        )

        self._docker_client = docker.from_env()

    async def asyncTearDown(self) -> None:
        shutil.rmtree(
            pathlib.Path("data"),
            ignore_errors=True,
        )

        for image in self._docker_client.images.list("saiblo-worker-image"):
            image.remove(force=True)

        self._docker_client.close()

    async def test_build_image_exists(self):
        """Test build() when target image exists."""
        # Arrange.
        image = self._docker_client.images.pull("hello-world")
        image.tag("saiblo-worker-image", CODE_ID)
        builder = DockerImageBuilder()

        # Act.
        result = await builder.build(CODE_ID, pathlib.Path())

        # Assert.
        self.assertEqual(result.code_id, CODE_ID)
        self.assertEqual(result.image, f"saiblo-worker-image:{CODE_ID}")
        self.assertEqual(result.message, "")

    async def test_build_invalid_tarball(self):
        """Test build() when the tarball is invalid."""
        # Arrange.
        path = pathlib.Path(f"data/agent_code/{CODE_ID}.tar")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
        builder = DockerImageBuilder()

        # Act.
        result = await builder.build(CODE_ID, path)

        # Assert.
        self.assertEqual(result.code_id, CODE_ID)
        self.assertEqual(result.image, None)
        self.assertNotEqual(result.message, "")

    async def test_build_valid_tarball(self):
        """Test build() when the tarball is valid."""
        # Arrange.
        path = pathlib.Path(f"data/agent_code/{CODE_ID}.tar")
        path.parent.mkdir(parents=True, exist_ok=True)
        dockerfile_bytes = b"FROM hello-world\n"
        tar_info = tarfile.TarInfo("Dockerfile")
        tar_info.size = len(dockerfile_bytes)
        with tarfile.open(path, "w") as tar:
            tar.addfile(tar_info, io.BytesIO(dockerfile_bytes))
        builder = DockerImageBuilder()

        # Act.
        result = await builder.build(CODE_ID, path)

        # Assert.
        self.assertEqual(result.code_id, CODE_ID)
        self.assertEqual(result.image, f"saiblo-worker-image:{CODE_ID}")
        self.assertEqual(result.message, "")
        self.assertEqual(len(self._docker_client.images.list("saiblo-worker-image")), 1)

    async def test_clean(self):
        """Test clean()."""
        # Arrange.
        image = self._docker_client.images.pull("hello-world")
        image.tag("saiblo-worker-image", CODE_ID)
        builder = DockerImageBuilder()

        # Act.
        await builder.clean()

        # Assert.
        self.assertEqual(len(self._docker_client.images.list("saiblo-worker-image")), 0)

    async def test_list(self):
        """Test list()."""
        # Arrange.
        image = self._docker_client.images.pull("hello-world")
        image.tag("saiblo-worker-image", CODE_ID)
        builder = DockerImageBuilder()

        # Act.
        result = await builder.list()

        # Assert.
        self.assertEqual(result, {CODE_ID: f"saiblo-worker-image:{CODE_ID}"})
