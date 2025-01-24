import unittest
from pathlib import Path

import path_manager


class TestPathManager(unittest.TestCase):
    def test_get_agent_code_base_dir_path(self):
        self.assertEqual(
            Path.cwd().joinpath(".data/agent_code"),
            path_manager.get_agent_code_base_dir_path(),
        )

    def test_get_judge_result_base_dir_path(self):
        self.assertEqual(
            Path.cwd().joinpath(".data/judge_results"),
            path_manager.get_judge_result_base_dir_path(),
        )
