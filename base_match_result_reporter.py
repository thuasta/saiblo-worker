"""Contains the base classes for match result reporters."""

from abc import ABC, abstractmethod

from match_result import MatchResult


class BaseMatchResultReporter(ABC):
    """Abstract base class for match result reporters."""

    @abstractmethod
    async def report(self, result: MatchResult) -> None:
        """Reports the result of a match.

        Args:
            result: The result of the match
        """
