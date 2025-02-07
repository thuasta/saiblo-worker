"""The implementation of the Docker image builder."""

import asyncio
from pathlib import Path
from typing import Dict

import docker
import docker.errors

from base_docker_image_builder import BaseDockerImageBuilder
from build_result import BuildResult

_IMAGE_REPOSITORY = "saiblo-worker-image"


class DockerImageBuilder(BaseDockerImageBuilder):
    """The Docker image builder."""

    def __init__(self):
        self._client = docker.from_env()

    async def build(self, code_id: str, file_path: Path) -> BuildResult:
        # If built, return the image tag.
        matched_image = [
            tag
            for image in self._client.images.list(_IMAGE_REPOSITORY)
            for tag in image.tags
            if tag.split(":")[-1] == code_id
        ]

        if len(matched_image) > 0:
            return BuildResult(
                code_id=code_id,
                image=matched_image[0],
                message="",
            )

        tag = f"{_IMAGE_REPOSITORY}:{code_id}"

        try:
            await asyncio.to_thread(self._build_image, file_path, tag)

            return BuildResult(
                code_id=code_id,
                image=tag,
                message="",
            )

        except docker.errors.BuildError as e:
            return BuildResult(
                code_id=code_id,
                image=None,
                message=str(e),
            )

    async def clean(self) -> None:
        images = self._client.images.list(_IMAGE_REPOSITORY)

        for image in images:
            image.remove(force=True)

    async def list(self) -> Dict[str, str]:
        images = [
            tag
            for image in self._client.images.list(_IMAGE_REPOSITORY)
            for tag in image.tags
            if tag.split(":")[0] == _IMAGE_REPOSITORY
        ]

        return {tag.split(":")[-1]: tag for tag in images}

    def _build_image(self, file_path: Path, tag: str):
        with open(file_path, "rb") as tar_file:
            self._client.images.build(
                fileobj=tar_file,
                custom_context=True,
                tag=tag,
                rm=True,
                forcerm=True,
            )
