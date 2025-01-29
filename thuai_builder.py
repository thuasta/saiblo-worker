"""Contains docker image build for THUAI."""

import asyncio
from typing import Dict
from pathlib import Path
import string
import random
import docker
import docker.errors
from base_docker_image_builder import BaseDockerImageBuilder

# BUILDER_NAME_LENGTH = 10
# IMAGE_NAME_PREFIX = "thuai-image-"


class ThuaiBuilder(BaseDockerImageBuilder):
    """Docker image builder for THUAI matches."""

    def __init__(self):
        self.client = docker.from_env()
        self.built_images = {}

        # # Generate a random string for the builder, to avoid name conflict
        # chars = string.ascii_letters + string.digits
        # self.name = "".join(random.choice(chars) for _ in range(BUILDER_NAME_LENGTH))

        # # ID for image, to avoid name conflict
        # self.image_id = 0
    
    def _build_image(self, file_path: Path, code_id: str):
        """Block in a separate thread to build Docker image."""
        self.client.images.build(path=str(file_path), tag=code_id, rm=True)

    async def build(self, file_path: Path, code_id: str) -> str:
        # get all image tags
        built_image_tags = [tag.split(':')[0] 
                                for image in self.client.images.list() 
                                for tag in image.tags]
        # print(f"Built image tags: {built_image_tags}")
        # if not built yet...
        if code_id not in built_image_tags:
            # print(f"Building image {code_id} from {file_path}")
            try:
                await asyncio.to_thread(self._build_image, file_path, code_id)
            except docker.errors.BuildError as e:
                error_logs = e.build_log
                error_msg = ""
                for log in error_logs:
                    log_line = log.get("stream", "")
                    # if 'error' in log_line:
                    #     error_msg += log_line
                    error_msg += log_line
                # print(error_msg)
                return f"E:{error_msg}"
            
        
        self.built_images[file_path] = code_id

        return self.built_images[file_path]

    async def clean(self) -> None:
        for image_tag in self.built_images.values():
            self.client.images.remove(image=image_tag)
        self.built_images.clear()

    async def list(self) -> Dict[Path, str]:
        return self.built_images.copy()

    # def get_image_name(self) -> str:
    #     """Get a no-duplicate name for images

    #     Name format: image-{builder name}-{id}

    #     Returns:
    #         The generated image name.
    #     """
    #     # name = IMAGE_NAME_PREFIX + self.name + "-" + str(self.image_id)
    #     name = IMAGE_NAME_PREFIX + "-" + str(self.image_id)
    #     self.image_id = self.image_id + 1
    #     return name
