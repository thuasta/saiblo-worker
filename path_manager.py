"""Manages paths for different components of the application."""

from pathlib import Path


def get_agent_code_base_dir_path() -> Path:
    """Gets the base directory for agent code.

    Returns:
        The base directory for agent code
    """

    return Path("data/agent_code").absolute()


def get_judge_replay_base_dir_path() -> Path:
    """Gets the base directory for judge replays.

    Returns:
        The base directory for judge replays
    """
    return Path("data/judge_replays").absolute()


def get_judge_result_base_dir_path() -> Path:
    """Gets the base directory for judge results.

    Returns:
        The base directory for judge results
    """
    return Path("data/judge_results").absolute()
