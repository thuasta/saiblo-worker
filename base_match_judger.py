"""Contains the base classes for match judgers."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from match_result import MatchResult


class BaseMatchJudger(ABC):
    """Abstract base class for match judgers."""

    @abstractmethod
    async def clean(self) -> None:
        """Cleans up judge results."""
        raise NotImplementedError

    @abstractmethod
    async def judge(
        self, match_id: str, game_host_image: str, agent_images: List[Optional[str]]
    ) -> MatchResult:
        """Judges a match.

        The match will not be judged again if the match has been judged before. So it is OK to get
        the result by calling this method.

        Args:
            match_id: The ID of the match to judge
            game_host_image: The host image
            agent_images: A list of agent images

        Returns:
            The result of the match
        """
        raise NotImplementedError

    @abstractmethod
    async def list(self) -> Dict[str, MatchResult]:
        """Lists all the matches that have been judged.

        Returns:
            A dictionary mapping match IDs to their corresponding MatchResult objects
        """
        raise NotImplementedError
