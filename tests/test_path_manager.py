"""Tests for path_manager module."""

import shutil
from pathlib import Path
from unittest import TestCase

import path_manager


class TestPathManager(TestCase):
    """Test cases for path_manager module functions that handle various file paths."""

    def setUp(self) -> None:
        shutil.rmtree(
            Path("data"),
            ignore_errors=True,
        )

    def tearDown(self) -> None:
        shutil.rmtree(
            Path("data"),
            ignore_errors=True,
        )

    def test_get_agent_code_base_dir_path(self):
        """Test getting the base directory path for agent code."""
        # Act.
        path = path_manager.get_agent_code_base_dir_path()

        # Assert.
        self.assertEqual(Path("data/agent_code"), path)

    def test_get_agent_code_tarball_path(self):
        """Test getting the path for a specific agent code tarball file."""
        # Arrange.
        code_id = "code_id"

        # Act.
        path = path_manager.get_agent_code_tarball_path(code_id)

        # Assert.
        self.assertEqual(Path(f"data/agent_code/{code_id}.tar"), path)

    def test_get_agent_code_tarball_paths_no_dir(self):
        """Test getting agent code tarball paths when directory doesn't exist."""
        # Act.
        paths = path_manager.get_agent_code_tarball_paths()

        # Assert.
        self.assertEqual([], paths)

    def test_get_agent_code_tarball_paths_file_exists(self):
        """Test getting agent code tarball paths when files exist."""
        # Arrange.
        path = Path("data/agent_code/code_id.tar")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()

        # Act.
        paths = path_manager.get_agent_code_tarball_paths()

        # Assert.
        self.assertEqual([path], paths)

    def test_get_judge_replay_base_dir_path(self):
        """Test getting the base directory path for judge replays."""
        self.assertEqual(
            Path("data/judge_replays"),
            path_manager.get_judge_replay_base_dir_path(),
        )

    def test_get_judge_replay_path(self):
        """Test getting the path for a specific judge replay file."""
        # Arrange.
        match_id = "match_id"

        # Act.
        path = path_manager.get_judge_replay_path(match_id)

        # Assert.
        self.assertEqual(Path(f"data/judge_replays/{match_id}.dat"), path)

    def test_get_judge_result_base_dir_path(self):
        """Test getting the base directory path for judge results."""
        self.assertEqual(
            Path("data/judge_results"),
            path_manager.get_judge_result_base_dir_path(),
        )

    def test_get_judge_result_path(self):
        """Test getting the path for a specific judge result file."""
        # Arrange.
        match_id = "match_id"

        # Act.
        path = path_manager.get_judge_result_path(match_id)

        # Assert.
        self.assertEqual(Path(f"data/judge_results/{match_id}.json"), path)

    def test_get_judge_result_paths_no_dir(self):
        """Test getting judge result paths when directory doesn't exist."""
        # Act.
        paths = path_manager.get_judge_result_paths()

        # Assert.
        self.assertEqual([], paths)

    def test_get_judge_result_paths_file_exists(self):
        """Test getting judge result paths when files exist."""
        # Arrange.
        path = Path("data/judge_results/match_id.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()

        # Act.
        paths = path_manager.get_judge_result_paths()

        # Assert.
        self.assertEqual([path], paths)
