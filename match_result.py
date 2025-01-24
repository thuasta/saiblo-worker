"""Contains the match result."""

from dataclasses import dataclass
from typing import List


@dataclass
class MatchResult:
    """Match result.

    Attributes:
        match_id: The match ID
        scores: A list of scores
            achieved by each agent. The index corresponds to the agent's position in the
            original agent_paths list. Higher scores typically indicate better performance.
    """

    match_id: str
    scores: List[float]
