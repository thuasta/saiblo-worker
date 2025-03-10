"""The implementation of the match judger."""

import asyncio
import dataclasses
import io
import json
import logging
import shutil
import tarfile
import uuid
from dataclasses import dataclass
from typing import Dict, List, Optional, TypedDict

import dacite
import docker
import docker.models.containers
import docker.models.networks
import requests
import urllib3

import saiblo_worker.path_manager as path_manager
from saiblo_worker.base_match_judger import BaseMatchJudger
from saiblo_worker.match_result import MatchResult

_AGENT_CONTAINER_NAME_PREFIX = "saiblo-worker-agent"
_GAME_HOST_APP_DATA_DIR_PATH = "/app/data/"
_GAME_HOST_CONTAINER_NAME_PREFIX = "saiblo-worker-game-host"
_GAME_HOST_REPLAY_FILE_NAME = "data/replay.dat"
_GAME_HOST_RESULT_FILE_NAME = "data/result.json"
_NETWORK_NAME_PREFIX = "saiblo-worker-network"


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

    _agent_mem_limit: str
    _agent_nano_cpus: int
    _docker_client: docker.DockerClient
    _game_host_mem_limit: str
    _game_host_nano_cpus: int
    _judge_timeout: float

    def __init__(
        self,
        *,
        agent_cpus: float,
        agent_mem_limit: str,
        game_host_cpus: float,
        game_host_mem_limit: str,
        judge_timeout: float,
    ) -> None:
        """Initialize the match judger.

        Args:
            agent_mem_limit: The memory limit for an agent container.
            agent_cpus: The CPU shares for an agent container.
            game_host_mem_limit: The memory limit for a game host container.
            game_host_cpus: The CPU shares for a game host container.
            judge_timeout: The timeout for judging a match.
        """

        self._agent_nano_cpus = int(agent_cpus * 1e9)
        self._agent_mem_limit = agent_mem_limit
        self._game_host_nano_cpus = int(game_host_cpus * 1e9)
        self._game_host_mem_limit = game_host_mem_limit
        self._judge_timeout = judge_timeout

        self._docker_client = docker.from_env()

    async def clean(self) -> None:
        logging.debug("Cleaning match judger environment")

        # Clean containers.
        for container in self._docker_client.containers.list(all=True):
            assert isinstance(container, docker.models.containers.Container)

            if container.name is not None and (
                container.name.startswith(_AGENT_CONTAINER_NAME_PREFIX)
                or container.name.startswith(_GAME_HOST_CONTAINER_NAME_PREFIX)
            ):
                container.stop(timeout=0)
                container.remove(v=True, force=True)

        # Clean networks.
        for network in self._docker_client.networks.list():
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

        logging.info("Match judger environment cleaned")

    async def judge(
        self,
        match_id: str,
        game_host_image: str,
        agent_images: List[Optional[str]],
    ) -> MatchResult:
        logging.debug("Judging match %s", match_id)

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
            logging.debug("Running game host container %s", game_host_container_name)

            game_host_container = await asyncio.to_thread(
                self._docker_client.containers.run,
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
                mem_limit=self._game_host_mem_limit,
                name=game_host_container_name,
                nano_cpus=self._game_host_nano_cpus,
                network_disabled=True,
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

                # Run the agent.
                logging.debug("Running agent container %s", agent_info.container_name)

                agent_container = await asyncio.to_thread(
                    self._docker_client.containers.run,
                    agent_info.image,
                    detach=True,
                    environment={
                        "TOKEN": agent_info.token,
                        "GAME_HOST": f"ws://{game_host_container_name}:14514",
                    },
                    mem_limit=self._agent_mem_limit,
                    name=agent_info.container_name,
                    nano_cpus=self._agent_nano_cpus,
                    network_disabled=True,
                )
                agent_containers.append(agent_container)

                # Create network.
                logging.debug(
                    "Creating network %s for agent %s",
                    agent_info.network_name,
                    agent_info.container_name,
                )

                agent_network = self._docker_client.networks.create(
                    agent_info.network_name
                )
                agent_network.connect(game_host_container_name)
                agent_network.connect(agent_info.container_name)
                agent_networks.append(agent_network)

            # Wait until the game host finishes or timeout.
            logging.debug(
                "Waiting for game host container %s", game_host_container_name
            )

            try:
                await asyncio.to_thread(
                    game_host_container.wait,
                    timeout=self._judge_timeout,
                )
            except requests.exceptions.ConnectionError as exc:
                if len(exc.args) == 1 and isinstance(
                    exc.args[0], urllib3.exceptions.ReadTimeoutError
                ):
                    logging.error("Game host timeout for match %s", match_id)

                    raise TimeoutError("Game host timeout") from exc

                raise

            # Stop the game host and agent containers.
            logging.debug("Stopping game host container %s", game_host_container_name)

            game_host_container.stop(timeout=0)

            # Get and save the result and the replay file.
            logging.debug(
                "Getting result and replay file from game host container %s",
                game_host_container_name,
            )

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
                            status="CANCEL",
                            stderr_output="",
                        )
                    )
                else:
                    container = agent_containers[i]
                    assert container is not None

                    # Reload attributes of the container.
                    container.reload()

                    # Stop the agent container if it is still running.
                    if container.status == "running":
                        logging.debug(
                            "Stopping agent container %s", agent_info.container_name
                        )

                        container.stop(timeout=0)

                        # The agent container is stopped by the judger so we regard it as a
                        # normal exit.
                        exit_code = 0

                    else:
                        # Theoretically, the agent container is already stopped so we don't need to
                        # wait for it. So we don't add a try-except block here.
                        exit_code = (
                            await asyncio.to_thread(
                                container.wait,
                                timeout=1,  # The shortest possible time.
                            )
                        )["StatusCode"]

                    agent_results.append(
                        MatchResult.AgentResult(
                            exit_code=exit_code,
                            score=(
                                game_host_match_result["scores"].get(
                                    agent_info.token, 0.0
                                )
                            ),
                            status="OK" if exit_code == 0 else "RE",
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

            logging.info("Match %s judged", match_id)

            return match_result

        except Exception as exc:  # pylint: disable=broad-except
            logging.error("Match %s judging failed: (%s) %s", match_id, type(exc), exc)

            match_result = MatchResult(
                match_id=match_id,
                agent_results=[
                    MatchResult.AgentResult(
                        exit_code=0,
                        score=0.0,
                        status="UE",
                        stderr_output="",
                    )
                    for _ in range(len(agent_info_list))
                ],
                error_message=str(exc),
                replay_file_path=None,
                stderr_output=(
                    game_host_container.logs(stdout=False).decode("utf-8")
                    if game_host_container is not None
                    else ""
                ),
            )

            return match_result

        finally:
            # Clean containers.
            for container in self._docker_client.containers.list(all=True):
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

            # Clean networks.
            for network in self._docker_client.networks.list():
                if network.name is not None and network.name in [
                    agent_info.network_name
                    for agent_info in agent_info_list
                    if agent_info is not None
                ]:
                    network.remove()

    async def list(self) -> Dict[str, MatchResult]:
        match_result_paths = path_manager.get_match_result_paths()

        return {
            path.stem: dacite.from_dict(MatchResult, json.load(path.open("r")))
            for path in match_result_paths
        }
