"""Contains the base classes for Docker image builders."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict


class BaseDockerImageBuilder(ABC):
    """Abstract base class for Docker image builders."""

    @abstractmethod
    async def build(self, file_path: Path) -> str:
        """Builds a Docker image.

        If the image already exists, it will not be built again. So it is OK to call this method to
        lookup the result.

        Args:
            file_path: The path to the tarball of the Docker context

        Returns:
            The tag to use for the docker image
        """
        raise NotImplementedError

    @abstractmethod
    async def clean(self) -> None:
        """Removes all Docker images built by this builder."""
        raise NotImplementedError

    @abstractmethod
    async def list(self) -> Dict[Path, str]:
        """Lists all Docker images built by this builder.

        Returns:
            A dictionary mapping paths to the tags of their corresponding Docker images
        """
        raise NotImplementedError
