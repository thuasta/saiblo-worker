"""Contains the base classes for build result reporters."""

from abc import ABC, abstractmethod

from build_result import BuildResult


class BaseBuildResultReporter(ABC):
    """Abstract base class for build result reporters."""

    @abstractmethod
    async def report(self, result: BuildResult) -> None:
        """Send the result of a build.

        Args:
            result: The result of the build
        """
