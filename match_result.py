"""Contains the match result."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class MatchResult:
    """Match result.

    Attributes:
        match_id: The match ID
        success: Whether the match was successfully judged
        err_msg: An error message if the match was not successfully judged
        scores: A list of scores
            achieved by each agent. The index corresponds to the agent's position in the
            original agent_paths list. Higher scores typically indicate better performance.
        record_file_path: The path to the record file.
    """

    match_id: str
    success: bool
    err_msg: str
    scores: List[float]
    record_file_path: Optional[str]
