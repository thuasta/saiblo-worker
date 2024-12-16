"""Docker builder abstraction module.

This module provides the base abstract class for Docker image builders.
It defines the common interface that all concrete Docker builder implementations
must follow, ensuring consistent behavior across different builder implementations.
"""

from abc import ABC, abstractmethod
from typing import List


class BaseDockerBuilder(ABC):
    """Abstract base class for Docker image builders."""

    @abstractmethod
    def build(self, path: str) -> str:
        """Builds a docker image

        Args:
            path: The path to the archive of the Docker context
            tag: The tag to use for the docker image

        Returns:
            The tag of the built docker image
        """
        raise NotImplementedError

    @abstractmethod
    def list(self) -> List[str]:
        """Lists all the docker images

        This method should return a list of all the docker images that were
        built by this builder instance.

        Returns:
            A list of docker image tags
        """
        raise NotImplementedError

    @abstractmethod
    def cleanup(self) -> None:
        """Removes all Docker images built by this builder.

        This method should clean up any Docker images that were created
        through this builder instance. It helps prevent disk space issues
        by removing unused images.
        """
        raise NotImplementedError
