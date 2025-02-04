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
        states: A list of states for each agent. Each state is a dictionary.
            state:
                position: the rank of the agent
                status: the status of the agent,  ["OK", "RE", "TLE", "MLE", "OLE", "STLE", "EXIT", "UE", "CANCEL", "IA"]
                code: the exit code of the agent
                stderr: the stderr of the agent, base64 encoded
    """

    match_id: str
    success: bool
    err_msg: str
    scores: List[float]
    record_file_path: Optional[str]
    states: List[dict]
