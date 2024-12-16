from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class Judgement:
    """Judgement result data class.

    This class represents the result of judging a game between agents.
    It contains information about the game outcome, scores, and any
    additional metadata from the judging process.

    Attributes:
        scores: A list of floating point numbers representing the numerical scores
            achieved by each agent. The index corresponds to the agent's position in the
            original agent_paths list. Higher scores typically indicate better performance.
    """

    scores: List[float]


class BaseJudger(ABC):
    """Abstract base class for implementing game judgers.

    This class defines the interface for judging games between multiple agents.
    Concrete implementations should inherit from this class and implement the
    judge method according to their specific game rules and scoring systems.
    """

    @abstractmethod
    def judge(self, agent_paths: List[str], host_path: str) -> Judgement:
        """Judges a game between agents.

        This method executes a game between the provided agents and evaluates their
        performance according to the game's rules and scoring system.

        Args:
            agent_paths: A list of file paths to the archives containing
                the agent implementations as a Docker context
            host_path: The file path to the archive containing the host/game
                implementation as a Docker context

        Returns:
            A Judgement object containing the final rankings and scores
                of all participating agents.
        """
        raise NotImplementedError
