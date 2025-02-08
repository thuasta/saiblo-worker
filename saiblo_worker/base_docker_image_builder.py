"""Contains the base classes for Docker image builders."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict

from saiblo_worker.build_result import BuildResult


class BaseDockerImageBuilder(ABC):
    """Abstract base class for Docker image builders."""

    @abstractmethod
    async def build(self, code_id: str, file_path: Path) -> BuildResult:
        """Builds a Docker image.

        If the image already exists, it will not be built again. So it is OK to call this method to
        lookup the result.

        Args:
            file_path: The path to the tarball of the Docker context

        Returns:
            The tag to use for the docker image
        """

    @abstractmethod
    async def clean(self) -> None:
        """Removes all Docker images built by this builder."""

    @abstractmethod
    async def list(self) -> Dict[str, str]:
        """Lists all Docker images built by this builder.

        Returns:
            A dictionary mapping code IDs to the tags of their corresponding Docker images
        """
