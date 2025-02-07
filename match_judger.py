"""The implementation of the match judger."""

import asyncio
import dataclasses
import io
import json
import shutil
import tarfile
import uuid
from dataclasses import dataclass
from typing import Dict, List, Optional, TypedDict

import dacite
import docker
import docker.models.containers
import docker.models.networks

import path_manager
from base_match_judger import BaseMatchJudger
from match_result import MatchResult

_AGENT_CONTAINER_NAME_PREFIX = "saiblo-worker-agent"
_GAME_HOST_APP_DATA_DIR_PATH = "/app/data/"
_GAME_HOST_CONTAINER_NAME_PREFIX = "saiblo-worker-game-host"
_GAME_HOST_REPLAY_FILE_NAME = "data/replay.dat"
_GAME_HOST_RESULT_FILE_NAME = "data/result.json"
_NETWORK_NAME_PREFIX = "saiblo-worker-network"

JUDGE_TIMEOUT = 600  # In seconds


@dataclass
class _AgentInfo:
    """The information of an agent.

    Attributes:
        code_id: The ID of the agent code.
        image_tag: The image tag of the agent.
    """

    container_name: str
    image: str
    network_name: str
    token: str


class _GameHostMatchResult(TypedDict):
    """The result of a match from the game host.

    Attributes:
        scores: The mapping from agent tokens to scores.
    """

    scores: Dict[str, float]


class MatchJudger(BaseMatchJudger):
    """The match judger."""

    def __init__(self):
        self._client = docker.from_env()

    async def clean(self) -> None:
        # Clean containers.
        for container in self._client.containers.list(all=True):
            assert isinstance(container, docker.models.containers.Container)

            if container.name is not None and (
                container.name.startswith(_AGENT_CONTAINER_NAME_PREFIX)
                or container.name.startswith(_GAME_HOST_CONTAINER_NAME_PREFIX)
            ):
                container.stop(timeout=0)
                container.remove(v=True, force=True)

        # Clean networks.
        for network in self._client.networks.list():
            if network.name is not None and network.name.startswith(
                _NETWORK_NAME_PREFIX
            ):
                network.remove()

        # Clean replays.
        match_replay_base_dir_path = path_manager.get_match_replay_base_dir_path()

        if match_replay_base_dir_path.is_dir():
            shutil.rmtree(match_replay_base_dir_path, ignore_errors=True)

        # Clean results.
        match_result_base_dir_path = path_manager.get_match_result_base_dir_path()

        if match_result_base_dir_path.is_dir():
            shutil.rmtree(match_result_base_dir_path, ignore_errors=True)

    async def judge(
        self,
        match_id: str,
        game_host_image: str,
        agent_images: List[Optional[str]],
    ) -> MatchResult:
        match_replay_file_path = path_manager.get_match_replay_path(match_id)
        match_replay_file_path.parent.mkdir(parents=True, exist_ok=True)

        match_result_file_path = path_manager.get_match_result_path(match_id)
        match_result_file_path.parent.mkdir(parents=True, exist_ok=True)

        # If judged before, return the result.
        if match_replay_file_path.is_file() and match_result_file_path.is_file():
            return dacite.from_dict(
                MatchResult, json.load(match_result_file_path.open("r"))
            )

        game_host_container_name = f"{_GAME_HOST_CONTAINER_NAME_PREFIX}-{match_id}"

        agent_info_list: List[Optional[_AgentInfo]] = [
            (
                _AgentInfo(
                    container_name=f"{_AGENT_CONTAINER_NAME_PREFIX}-{match_id}-{i}",
                    image=image,
                    network_name=f"{_NETWORK_NAME_PREFIX}-{match_id}-{i}",
                    token=uuid.uuid4().hex,
                )
                if image is not None
                else None
            )
            for i, image in enumerate(agent_images)
        ]

        game_host_container: Optional[docker.models.containers.Container] = None

        try:
            # Run the game host.
            game_host_container = self._client.containers.run(
                game_host_image,
                detach=True,
                environment={
                    "TOKENS": ",".join(
                        [
                            agent_info.token
                            for agent_info in agent_info_list
                            if agent_info
                        ]
                    )
                },
                name=game_host_container_name,
            )

            # Run agent containers.
            agent_containers: List[Optional[docker.models.containers.Container]] = []
            agent_networks: List[Optional[docker.models.networks.Network]] = []

            for agent_info in agent_info_list:
                # For agents that are not provided, append None.
                if agent_info is None:
                    agent_containers.append(None)
                    agent_networks.append(None)
                    continue

                # Create container.
                agent_container = self._client.containers.run(
                    agent_info.image,
                    detach=True,
                    environment={
                        "TOKEN": agent_info.token,
                        "GAME_HOST": f"ws://{game_host_container_name}:14514",
                    },
                    name=agent_info.container_name,
                )
                agent_containers.append(agent_container)

                # Create network.
                agent_network = self._client.networks.create(agent_info.network_name)
                agent_network.connect(game_host_container_name)
                agent_network.connect(agent_info.container_name)
                agent_networks.append(agent_network)

            # Wait until the game host finishes or timeout.
            await asyncio.to_thread(game_host_container.wait, timeout=JUDGE_TIMEOUT)

            # Stop the game host and agent containers.
            # For game host, we give it some time after SIGTERM to write the result file.
            game_host_container.stop()

            for agent_container in agent_containers:
                if agent_container is not None:
                    agent_container.stop(timeout=0)

            # Get and save the result and the replay file.
            game_host_app_data_tarball_stream, _ = game_host_container.get_archive(
                _GAME_HOST_APP_DATA_DIR_PATH
            )

            game_host_app_data_tarball_bytesio = io.BytesIO()
            for chunk in game_host_app_data_tarball_stream:
                game_host_app_data_tarball_bytesio.write(chunk)

            with tarfile.open(
                fileobj=io.BytesIO(game_host_app_data_tarball_bytesio.getvalue()),
                mode="r",
            ) as tar_file:
                result_file = tar_file.extractfile(
                    _GAME_HOST_RESULT_FILE_NAME
                ) or io.BytesIO("{}".encode("utf-8"))

                game_host_match_result: _GameHostMatchResult = json.loads(
                    result_file.read().decode("utf-8")
                )

                replay_file = (
                    tar_file.extractfile(_GAME_HOST_REPLAY_FILE_NAME) or io.BytesIO()
                )

                with match_replay_file_path.open("wb") as f:
                    f.write(replay_file.read())

            # Build the result.
            agent_results: List[MatchResult.AgentResult] = []

            for i, _ in enumerate(agent_info_list):
                agent_info = agent_info_list[i]

                if agent_info is None:
                    agent_results.append(
                        MatchResult.AgentResult(
                            exit_code=0,
                            score=0.0,
                            status="EXIT",
                            stderr_output="",
                        )
                    )
                else:
                    container = agent_containers[i]
                    assert container is not None

                    agent_results.append(
                        MatchResult.AgentResult(
                            exit_code=(await asyncio.to_thread(container.wait))[
                                "StatusCode"
                            ],
                            score=(
                                game_host_match_result["scores"].get(
                                    agent_info.token, 0.0
                                )
                            ),
                            status="OK",
                            stderr_output=container.logs(stdout=False).decode("utf-8"),
                        )
                    )

            match_result = MatchResult(
                match_id=match_id,
                agent_results=agent_results,
                error_message="",
                replay_file_path=str(match_replay_file_path),
                stderr_output=game_host_container.logs(stdout=False).decode("utf-8"),
            )

            with open(match_result_file_path, "w", encoding="utf-8") as f:
                json.dump(dataclasses.asdict(match_result), f)

            return match_result

        except Exception as e:  # pylint: disable=broad-except
            return MatchResult(
                match_id=match_id,
                agent_results=[
                    MatchResult.AgentResult(
                        exit_code=0,
                        score=0.0,
                        status="CANCEL",
                        stderr_output="",
                    )
                    for _ in range(len(agent_info_list))
                ],
                error_message=str(e),
                replay_file_path=None,
                stderr_output=(
                    game_host_container.logs(stdout=False).decode("utf-8")
                    if game_host_container is not None
                    else ""
                ),
            )

        finally:
            # Clean networks.
            for network in self._client.networks.list():
                if network.name is not None and network.name in [
                    agent_info.network_name
                    for agent_info in agent_info_list
                    if agent_info is not None
                ]:
                    network.remove()

            # Clean containers.
            for container in self._client.containers.list(all=True):
                assert isinstance(container, docker.models.containers.Container)

                if container.name is not None and (
                    container.name == game_host_container_name
                    or container.name
                    in [
                        agent_info.container_name
                        for agent_info in agent_info_list
                        if agent_info
                    ]
                ):
                    container.stop(timeout=0)
                    container.remove(v=True, force=True)

    async def list(self) -> Dict[str, MatchResult]:
        match_result_paths = path_manager.get_match_result_paths()

        return {
            path.stem: dacite.from_dict(MatchResult, json.load(path.open("r")))
            for path in match_result_paths
        }
