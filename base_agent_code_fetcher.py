"""Contains the base classes for agent code fetchers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict


class BaseAgentCodeFetcher(ABC):
    """Abstract base class for agent code fetchers."""

    @abstractmethod
    async def clean(self) -> None:
        """Cleans up fetched resources."""
        raise NotImplementedError

    @abstractmethod
    async def fetch(self, code_id: str) -> Path:
        """Fetches the code for an agent and saves it to a file in tarball format.

        If the file already exists, the agent code will not be fetched again. So it is OK to call
        this method to lookup the result.

        Args:
            code_id: The ID of the code to fetch

        Returns:
            The path to the tarball file where the code should be saved
        """
        raise NotImplementedError

    @abstractmethod
    async def list(self) -> Dict[str, Path]:
        """Lists all agent code tarballs that are already fetched.

        Returns:
            A dictionary mapping code IDs to the paths of their corresponding tarball files
        """
        raise NotImplementedError
