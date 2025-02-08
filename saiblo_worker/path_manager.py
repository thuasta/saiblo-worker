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


def get_match_replay_base_dir_path() -> Path:
    """Gets the base directory for match replays.

    Returns:
        The base directory for match replays
    """
    return Path("data/match_replays")


def get_match_replay_path(match_id: str) -> Path:
    """Gets the path to the replay for the match with the given match ID.

    Args:
        match_id: The ID of the match

    Returns:
        The path to the replay for the match with the given match ID
    """
    return get_match_replay_base_dir_path() / f"{match_id}.dat"


def get_match_result_base_dir_path() -> Path:
    """Gets the base directory for match results.

    Returns:
        The base directory for match results
    """
    return Path("data/match_results")


def get_match_result_path(match_id: str) -> Path:
    """Gets the path to the result for the match with the given match ID.

    Args:
        match_id: The ID of the match

    Returns:
        The path to the result for the match with the given match ID
    """
    return get_match_result_base_dir_path() / f"{match_id}.json"


def get_match_result_paths() -> List[Path]:
    """Gets the paths to all match result files.

    Returns:
        The paths to all match result files
    """
    return list(get_match_result_base_dir_path().glob("*.json"))
