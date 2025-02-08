"""Contains the match result."""

from dataclasses import dataclass
from typing import List, Literal, Optional


@dataclass
class MatchResult:
    """Match result.

    Attributes:
        match_id: The match ID
        agent_results: The match result for each agent
        error_message: The error message of the match result
        success: Whether the match was successful
        replay_file_path: The path to the replay file
    """

    @dataclass
    class AgentResult:
        """Match result for an agent.

        Attributes:
            exit_code: The exit code of the agent
            score: The score of the agent
            status: The status of the agent
            stderr_output: The stderr output of the agent
        """

        exit_code: int
        score: float
        status: Literal[
            "OK", "RE", "TLE", "MLE", "OLE", "STLE", "EXIT", "UE", "CANCEL", "IA"
        ]
        stderr_output: str

    match_id: str

    agent_results: List[AgentResult]
    error_message: str
    replay_file_path: Optional[str]
    stderr_output: str
