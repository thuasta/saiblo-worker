"""Contains docker image build for THUAI."""

from typing import Dict
from pathlib import Path
import string
import random
import docker
import docker.errors
from base_docker_image_builder import BaseDockerImageBuilder

BUILDER_NAME_LENGTH = 10
IMAGE_NAME_PREFIX = "THUAI-image"


class ThuaiBuilder(BaseDockerImageBuilder):
    """Docker image builder for THUAI matches."""

    def __init__(self):
        self.client = docker.from_env()
        self.built_images = {}

        # Generate a random string for the builder, to avoid name conflict
        chars = string.ascii_letters + string.digits
        self.name = "".join(random.choice(chars) for _ in range(BUILDER_NAME_LENGTH))

        # ID for image, to avoid name conflict
        self.image_id = 0

    async def build(self, file_path: Path) -> str:
        # if not built yet...
        if file_path not in self.built_images:
            img_tag = self.get_image_name()
            self.client.images.build(path=file_path, tag=img_tag, rm=True)
            self.built_images[file_path] = img_tag

        return self.built_images[file_path]

    async def clean(self) -> None:
        for image_tag in self.built_images.values():
            self.client.images.remove(image=image_tag)
        self.built_images.clear()

    async def list(self) -> Dict[Path, str]:
        return self.built_images.copy()

    async def get_image_name(self) -> str:
        """Get a no-duplicate name for images

        Name format: image-{builder name}-{id}

        Returns:
            The generated image name.
        """
        name = IMAGE_NAME_PREFIX + self.name + "-" + str(self.image_id)
        self.image_id = self.image_id + 1
        return name
