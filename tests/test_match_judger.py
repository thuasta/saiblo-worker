"""Tests for the match_judger module."""

import dataclasses
import json
import pathlib
import shutil
import tempfile
import unittest

import docker
import docker.models.containers

from match_judger import MatchJudger
from match_result import MatchResult


class TestMatchJudger(unittest.IsolatedAsyncioTestCase):
    """Tests for the MatchJudger class."""

    _docker_client: docker.DockerClient

    async def asyncSetUp(self) -> None:
        self._docker_client = docker.from_env()

        self._clean()

    async def asyncTearDown(self) -> None:
        self._clean()

        self._docker_client.close()

    async def test_clean_everything(self):
        """Test clean() when there is everything to clean."""
        # Arrange.
        self._docker_client.containers.run(
            "hello-world", detach=True, name="saiblo-worker-agent-0"
        )
        self._docker_client.containers.run(
            "hello-world", detach=True, name="saiblo-worker-game-host-0"
        )
        self._docker_client.networks.create("saiblo-worker-network-0")

        replay_file_path = pathlib.Path("data/match_replays/code_id.dat")
        replay_file_path.parent.mkdir(parents=True, exist_ok=True)
        replay_file_path.touch()

        result_file_path = pathlib.Path("data/match_results/code_id.json")
        result_file_path.parent.mkdir(parents=True, exist_ok=True)
        result_file_path.touch()

        match_judger = MatchJudger()

        # Act.
        await match_judger.clean()

        # Assert.
        self.assertFalse(replay_file_path.exists())
        self.assertFalse(result_file_path.exists())

    async def test_clean_nothing(self):
        """Test clean() when there is nothing to clean."""
        # Arrange.
        self._docker_client.containers.run(
            "hello-world", detach=True, name="saiblo-worker-test-0"
        )
        self._docker_client.networks.create("saiblo-worker-test-0")

        match_judger = MatchJudger()

        # Act.
        await match_judger.clean()

        # Assert.
        self.assertTrue(
            any(
                container.name == "saiblo-worker-test-0"
                for container in self._docker_client.containers.list(all=True)
            )
        )
        self.assertTrue(
            any(
                network.name == "saiblo-worker-test-0"
                for network in self._docker_client.networks.list()
            )
        )

    async def test_judge_no_result_nor_replay(self):
        """Test judge() when there is no result nor replay."""
        # Arrange.
        match_judger = MatchJudger()

        # Act.
        result = await match_judger.judge("match_id", "hello-world", [])

        # Assert.
        self.assertEqual(result.match_id, "match_id")
        self.assertEqual(result.agent_results, [])
        self.assertNotEqual(result.error_message, "")
        self.assertEqual(result.replay_file_path, None)

    async def test_judge_normal(self):
        """Test judge() when everything is normal."""
        # Arrange.

        # Build the game host image.
        with tempfile.TemporaryDirectory("w") as dir_path:
            with open(f"{dir_path}/Dockerfile", "wb") as file:
                file.write(
                    b"FROM hello-world\nCOPY result.json /app/data/result.json\nCOPY replay.dat /app/data/replay.dat\n"
                )
            with open(f"{dir_path}/result.json", "w", encoding="utf-8") as file:
                json.dump({"scores": {}}, file)
            with open(f"{dir_path}/replay.dat", "wb") as file:
                file.write(b"")
            self._docker_client.images.build(
                path=dir_path,
                tag="saiblo-worker-test",
            )

        match_judger = MatchJudger()

        # Act.
        result = await match_judger.judge(
            "match_id", "saiblo-worker-test", ["hello-world", None]
        )

        # Assert.
        self.assertEqual(result.match_id, "match_id")
        self.assertEqual(
            result.agent_results,
            [
                MatchResult.AgentResult(
                    exit_code=0, score=0.0, status="OK", stderr_output=""
                ),
                MatchResult.AgentResult(
                    exit_code=0, score=0.0, status="EXIT", stderr_output=""
                ),
            ],
        )
        self.assertEqual(result.error_message, "")
        self.assertEqual(result.replay_file_path, "data/match_replays/match_id.dat")
        self.assertEqual(result.stderr_output, "")

    async def test_judge_result_exists(self):
        """Test judge() when the result already exists."""
        # Arrange.
        match_replay_path = pathlib.Path("data/match_replays/match_id.dat")
        match_replay_path.parent.mkdir(parents=True, exist_ok=True)
        match_replay_path.touch()

        match_result = MatchResult(
            match_id="match_id",
            agent_results=[],
            error_message="error_message",
            replay_file_path=None,
            stderr_output="stderr_output",
        )
        match_result_path = pathlib.Path("data/match_results/match_id.json")
        match_result_path.parent.mkdir(parents=True, exist_ok=True)
        with open(match_result_path, "w", encoding="utf-8") as file:
            json.dump(
                dataclasses.asdict(match_result),
                file,
            )

        match_judger = MatchJudger()

        # Act.
        result = await match_judger.judge("match_id", "", [])

        # Assert.
        self.assertEqual(result, match_result)

    async def test_list(self):
        """Test list()."""
        # Arrange.
        match_result = MatchResult(
            match_id="match_id",
            agent_results=[],
            error_message="error_message",
            replay_file_path=None,
            stderr_output="stderr_output",
        )
        path = pathlib.Path("data/match_results/match_id.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as file:
            json.dump(
                dataclasses.asdict(match_result),
                file,
            )

        match_judger = MatchJudger()

        # Act.
        result = await match_judger.list()

        # Assert.
        self.assertEqual(
            result,
            {
                "match_id": match_result,
            },
        )

    def _clean(self) -> None:
        """Clean up the environment."""

        shutil.rmtree(
            pathlib.Path("data"),
            ignore_errors=True,
        )

        for network in self._docker_client.networks.list():
            if network.name is not None and (
                network.name.startswith("saiblo-worker-network-")
                or network.name.startswith("saiblo-worker-test-")
            ):
                network.remove()

        for container in self._docker_client.containers.list(all=True):
            assert isinstance(container, docker.models.containers.Container)
            if container.name is not None and (
                container.name.startswith("saiblo-worker-agent-")
                or container.name.startswith("saiblo-worker-game-host-")
                or container.name.startswith("saiblo-worker-test-")
            ):
                container.stop(timeout=0)
                container.remove(v=True, force=True)

        for image in self._docker_client.images.list("saiblo-worker-test"):
            image.remove(force=True)
