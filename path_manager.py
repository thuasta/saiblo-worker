"""Manages paths for different components of the application."""

from pathlib import Path
from typing import List


def get_agent_code_base_dir_path() -> Path:
    """Gets the base directory for agent code.

    Returns:
        The base directory for agent code
    """

    return Path("data/agent_code")


def get_agent_code_tarball_path(code_id: str) -> Path:
    """Gets the path to the tarball for the agent code with the given ID.

    Args:
        code_id: The ID of the agent code

    Returns:
        The path to the tarball for the agent code with the given ID
    """
    return get_agent_code_base_dir_path() / f"{code_id}.tar"


def get_agent_code_tarball_paths() -> List[Path]:
    """Gets the paths to all agent code tarballs.

    Returns:
        The paths to all agent code tarballs
    """
    return list(get_agent_code_base_dir_path().glob("*.tar"))


def get_judge_replay_base_dir_path() -> Path:
    """Gets the base directory for judge replays.

    Returns:
        The base directory for judge replays
    """
    return Path("data/judge_replays")


def get_judge_replay_path(match_id: str) -> Path:
    """Gets the path to the replay for the judge with the given match ID.

    Args:
        match_id: The ID of the match

    Returns:
        The path to the replay for the judge with the given match ID
    """
    return get_judge_replay_base_dir_path() / f"{match_id}.dat"


def get_judge_result_base_dir_path() -> Path:
    """Gets the base directory for judge results.

    Returns:
        The base directory for judge results
    """
    return Path("data/judge_results")


def get_judge_result_path(match_id: str) -> Path:
    """Gets the path to the result for the judge with the given match ID.

    Args:
        match_id: The ID of the match

    Returns:
        The path to the result for the judge with the given match ID
    """
    return get_judge_result_base_dir_path() / f"{match_id}.json"


def get_judge_result_paths() -> List[Path]:
    """Gets the paths to all judge result files.

    Returns:
        The paths to all judge result files
    """
    return list(get_judge_result_base_dir_path().glob("*.json"))
