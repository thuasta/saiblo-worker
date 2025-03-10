"""The implementation of the Docker image builder."""

import asyncio
import logging
from pathlib import Path
from typing import Dict

import docker
import docker.errors
import urllib3

from saiblo_worker.base_docker_image_builder import BaseDockerImageBuilder
from saiblo_worker.build_result import BuildResult

_IMAGE_REPOSITORY = "saiblo-worker-image"


class DockerImageBuilder(BaseDockerImageBuilder):
    """The Docker image builder."""

    _build_timeout: int
    _docker_client: docker.DockerClient

    def __init__(
        self,
        *,
        build_timeout: int,
    ):
        self._build_timeout = build_timeout

        self._docker_client = docker.from_env()

    async def build(self, code_id: str, file_path: Path) -> BuildResult:
        logging.debug("Building agent code %s", code_id)

        # If built, return the image tag.
        matched_image = [
            tag
            for image in self._docker_client.images.list(_IMAGE_REPOSITORY)
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
            with open(file_path, "rb") as tar_file:
                try:
                    await asyncio.to_thread(
                        self._docker_client.images.build,
                        custom_context=True,
                        fileobj=tar_file,
                        forcerm=True,
                        rm=True,
                        tag=tag,
                        timeout=self._build_timeout,
                    )
                except urllib3.exceptions.TimeoutError as exc:
                    logging.error("Timeout when building agent code %s", code_id)

                    raise TimeoutError("Timeout when building agent code") from exc

            logging.info("Agent code %s built", code_id)

            return BuildResult(
                code_id=code_id,
                image=tag,
                message="",
            )

        except Exception as e:  # pylint: disable=broad-except
            logging.error("Failed to build agent code %s: %s", code_id, e)

            return BuildResult(
                code_id=code_id,
                image=None,
                message=str(e),
            )

    async def clean(self) -> None:
        logging.debug("Cleaning images")

        images = self._docker_client.images.list(_IMAGE_REPOSITORY)

        for image in images:
            image.remove(force=True)

        logging.info("Images cleaned")

    async def list(self) -> Dict[str, str]:
        images = [
            tag
            for image in self._docker_client.images.list(_IMAGE_REPOSITORY)
            for tag in image.tags
            if tag.split(":")[0] == _IMAGE_REPOSITORY
        ]

        return {tag.split(":")[-1]: tag for tag in images}
