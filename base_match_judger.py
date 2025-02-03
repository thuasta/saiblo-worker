"""Contains the base classes for match judgers."""

from abc import ABC, abstractmethod
from typing import Dict, List

from match_result import MatchResult


class BaseMatchJudger(ABC):
    """Abstract base class for match judgers."""

    @abstractmethod
    async def judge(
        self, match_id: str, game_host_image_tag: str, agent_image_tags: List[str]
    ) -> MatchResult:
        """Judges a match.

        The match will not be judged again if the match has been judged before. So it is OK to get
        the result by calling this method.

        Args:
            match_id: The ID of the match to judge
            game_host_image_tag: The tag of the host image
            agent_image_tags: The tags of the agent images

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
    
    @abstractmethod
    def stop(self) -> None:
        """Stops the judger."""
        raise NotImplementedError
