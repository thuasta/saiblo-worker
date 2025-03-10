"""Tests for the docker_image_builder module."""

import io
import pathlib
import shutil
import tarfile
import unittest

import docker

from saiblo_worker.docker_image_builder import DockerImageBuilder


class TestDockerImageBuilder(unittest.IsolatedAsyncioTestCase):
    """Tests for the DockerImageBuilder class."""

    _docker_client: docker.DockerClient

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
        image.tag("saiblo-worker-image", "code_id")
        builder = DockerImageBuilder(build_timeout=60)

        # Act.
        result = await builder.build("code_id", pathlib.Path())

        # Assert.
        self.assertEqual(result.code_id, "code_id")
        self.assertEqual(result.image, "saiblo-worker-image:code_id")
        self.assertEqual(result.message, "")

    async def test_build_invalid_tarball(self):
        """Test build() when the tarball is invalid."""
        # Arrange.
        path = pathlib.Path("data/agent_code/code_id.tar")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
        builder = DockerImageBuilder(build_timeout=60)

        # Act.
        result = await builder.build("code_id", path)

        # Assert.
        self.assertEqual(result.code_id, "code_id")
        self.assertEqual(result.image, None)
        self.assertNotEqual(result.message, "")

    async def test_build_valid_tarball(self):
        """Test build() when the tarball is valid."""
        # Arrange.
        path = pathlib.Path("data/agent_code/code_id.tar")
        path.parent.mkdir(parents=True, exist_ok=True)
        dockerfile_bytes = b"FROM hello-world\n"
        tar_info = tarfile.TarInfo("Dockerfile")
        tar_info.size = len(dockerfile_bytes)
        with tarfile.open(path, "w") as tar:
            tar.addfile(tar_info, io.BytesIO(dockerfile_bytes))
        builder = DockerImageBuilder(build_timeout=60)

        # Act.
        result = await builder.build("code_id", path)

        # Assert.
        self.assertEqual(result.code_id, "code_id")
        self.assertEqual(result.image, "saiblo-worker-image:code_id")
        self.assertEqual(result.message, "")
        self.assertEqual(len(self._docker_client.images.list("saiblo-worker-image")), 1)

    async def test_clean(self):
        """Test clean()."""
        # Arrange.
        image = self._docker_client.images.pull("hello-world")
        image.tag("saiblo-worker-image", "code_id")
        builder = DockerImageBuilder(build_timeout=60)

        # Act.
        await builder.clean()

        # Assert.
        self.assertEqual(len(self._docker_client.images.list("saiblo-worker-image")), 0)

    async def test_list(self):
        """Test list()."""
        # Arrange.
        image = self._docker_client.images.pull("hello-world")
        image.tag("saiblo-worker-image", "code_id")
        builder = DockerImageBuilder(build_timeout=60)

        # Act.
        result = await builder.list()

        # Assert.
        self.assertEqual(result, {"code_id": "saiblo-worker-image:code_id"})
