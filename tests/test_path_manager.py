"""Tests for path_manager module."""

import shutil
from pathlib import Path
from unittest import TestCase

import saiblo_worker.path_manager as path_manager


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

    def test_get_match_replay_base_dir_path(self):
        """Test getting the base directory path for match replays."""
        self.assertEqual(
            Path("data/match_replays"),
            path_manager.get_match_replay_base_dir_path(),
        )

    def test_get_match_replay_path(self):
        """Test getting the path for a specific match replay file."""
        # Arrange.
        match_id = "match_id"

        # Act.
        path = path_manager.get_match_replay_path(match_id)

        # Assert.
        self.assertEqual(Path(f"data/match_replays/{match_id}.dat"), path)

    def test_get_match_result_base_dir_path(self):
        """Test getting the base directory path for match results."""
        self.assertEqual(
            Path("data/match_results"),
            path_manager.get_match_result_base_dir_path(),
        )

    def test_get_match_result_path(self):
        """Test getting the path for a specific match result file."""
        # Arrange.
        match_id = "match_id"

        # Act.
        path = path_manager.get_match_result_path(match_id)

        # Assert.
        self.assertEqual(Path(f"data/match_results/{match_id}.json"), path)

    def test_get_match_result_paths_no_dir(self):
        """Test getting match result paths when directory doesn't exist."""
        # Act.
        paths = path_manager.get_match_result_paths()

        # Assert.
        self.assertEqual([], paths)

    def test_get_match_result_paths_file_exists(self):
        """Test getting match result paths when files exist."""
        # Arrange.
        path = Path("data/match_results/match_id.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()

        # Act.
        paths = path_manager.get_match_result_paths()

        # Assert.
        self.assertEqual([path], paths)
