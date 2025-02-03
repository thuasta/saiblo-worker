"""Contains the judger class implemented for THUAI matches."""

import base64
import io
import tarfile
from typing import List, Dict
from pathlib import Path
import random
import string
import asyncio
import json

import docker
from docker.types import Mount

from base_match_judger import BaseMatchJudger
from match_result import MatchResult
from path_manager import get_judge_result_base_dir_path


JUDGER_NAME_LENGTH = 10
AGENT_CONTAINER_NAME_PREFIX = "THUAI_agent_"
SERVER_CONTAINER_NAME_PREFIX = "THUAI_server_"
NETWORK_NAME_PREFIX = "THUAI_network_"

JUDGE_TIMEOUT = 600  # In seconds


class JudgeTimeoutException(Exception):
    """Exception class for Judge timeout"""

    def __init__(self):
        pass


class ThuaiJudger(BaseMatchJudger):
    """The Judger implemented for THUAI judgement work."""

    def __init__(self):
        """Initialize the judger."""
        self.client = docker.from_env()
        self.judges = {}

        # Generate a random string for the judger, to avoid name conflict
        chars = string.ascii_letters + string.digits
        self.name = "".join(random.choice(chars) for _ in range(JUDGER_NAME_LENGTH))

        # IDs for the resources, to avoid name conflict
        self.agent_id = 0
        self.server_id = 0
        self.network_id = 0

        # Record resources held by each judge.
        self.judge_server: Dict[str, str] = {}
        self.judge_containers: Dict[str, List[str]] = {}
        self.judge_networks: Dict[str, List[str]] = {}
        self.agent_states: Dict[str, List[Dict]] = {}

    async def judge(
        self, match_id: str, game_host_image_tag: str, agent_image_tags: List[str]
    ) -> MatchResult:

        # If not judged before...
        if match_id not in self.judges:
            try:
                # Judge and memorize the result.

                # Initialize the judge
                self.judge_containers[match_id] = []
                self.judge_networks[match_id] = []
                self.agent_states[match_id] = []

                # Decide name of server.
                server_name = self.get_name("server")

                token = 0

                print(
                    f"Starting Server {server_name} with image {game_host_image_tag}."
                )

                # Run server container.
                record_folder = self.get_name("record", match_id)
                Path(record_folder).mkdir(parents=True)
                # server_mount = Mount("/record", record_folder, type="bind")

                self.client.containers.run(
                    game_host_image_tag,
                    # ports={"14514/tcp": 14514},
                    # remove=True,
                    # mounts=[server_mount],
                    detach=True,
                    name=server_name,
                )
                self.judge_server[match_id] = server_name

                print(
                    f"Server {server_name} is running with image {game_host_image_tag}."
                )

                # Run agent containers, create networks
                for agent_image_tag in agent_image_tags:

                    # Network
                    network_name = self.get_name("network")
                    agent_network = self.client.networks.create(network_name)
                    self.judge_networks[match_id].append(network_name)
                    agent_network.connect(server_name)

                    # Agent Container
                    container_name = self.get_name("agent")
                    self.client.containers.run(
                        agent_image_tag,
                        [
                            "--token",
                            str(token),
                            "--server",
                            f"ws://{server_name}:14514",
                        ],
                        network=network_name,
                        detach=True,
                        name=container_name,
                        # remove=True,
                    )
                    self.judge_containers[match_id].append(container_name)

                    token = token + 1

                # for network in self.judge_networks[match_id]:
                #     self.client.networks.get(network).connect(server_name)

                task_server_run = asyncio.to_thread(self.wait_container, server_name)
                task_force_kill = asyncio.create_task(self.force_kill(match_id))
                try:
                    await task_server_run
                except JudgeTimeoutException:
                    print(f"Timeout: match_id {match_id}")

                self.stop_judge(match_id)
                print("Server stopped")
                success = True
                try:
                    winner = self.get_winner(match_id)
                    print("Winner: ", winner)
                    scores = [1.0 if i == winner else 0.0 for i in range(token)]
                except Exception as e:
                    success = False
                    print(e)
                    scores = [0.0] * token
                record_file_path = Path(record_folder) / "record.dat"
                states = self.agent_states[match_id]
                # Fill in the missing states
                for i in range(len(states), token):
                    states.append(
                        {
                            "position": i,
                            "status": "OK",
                            "code": 0,
                            "stderr": "",
                        }
                    )  
                    
                # print("States: ", states)
                self.judges[match_id] = MatchResult(
                    match_id=match_id,
                    scores=scores,
                    record_file_path=str(record_file_path),
                    success=success,
                    err_msg="",
                    states=states,
                )

                task_force_kill.cancel()
            
            except asyncio.CancelledError:
                self.stop_judge(match_id)
                raise

            except Exception as e:
                self.stop_judge(match_id)
                print(e)
                raise e

        return self.judges[match_id]

    def wait_container(self, container_name: str):
        """Wait before a detached container finishes running.

        Args:
            container_name (str): Name of the container.
        """
        self.client.containers.get(container_name).wait()

    async def list(self) -> Dict[str, MatchResult]:
        return self.judges.copy()

    async def force_kill(self, match_id, waiting: int = JUDGE_TIMEOUT) -> None:
        """Force stop a match and throw an exception.

        Args:
            match_id (str): The ID of match
            waiting (int, optional): The time to wait. Defaults to JUDGE_TIMEOUT.

        Raises:
            JudgeTimeoutException: If judge is force stopped.
        """
        await asyncio.sleep(waiting)
        self.stop_judge(match_id)
        raise JudgeTimeoutException

    def stop_judge(self, match_id: str) -> None:
        """Stop a judge and release its resources

        If match doesn't exist or has already ended, do nothing.

        Args:
            match_id (str): The match to stop.
        """
        print(f"Stopping judge {match_id}")
        if match_id not in self.judge_server:
            return
        server_container = self.client.containers.get(self.judge_server[match_id])
        try:
            server_container.kill()
        except Exception as e:
            print(e)
        record_tar_stream = server_container.get_archive("/record/")[0]
        # print(record_tar_file)
        record_folder = self.get_name("record", match_id)
        record_tar_buf = io.BytesIO()
        for chunk in record_tar_stream:
            record_tar_buf.write(chunk)
        # record_tar_stream is a multipart encoded file, we need to extract it
        with tarfile.open(
            fileobj=io.BytesIO(record_tar_buf.getvalue()), mode="r"
        ) as tar:
            for member in tar.getmembers():
                split_name = member.name.split("/", 1)
                if len(split_name) == 1:
                    continue
                member.name = split_name[1]
                tar.extract(member, record_folder)

        try:
            server_container.remove()
        except Exception as e:
            print(e)

        self.judge_server.pop(match_id)

        if match_id in self.judge_containers:
            for i in range(len(self.judge_containers[match_id])):
                container_name = self.judge_containers[match_id][i]
                print(f"Stopping container {container_name}")
                try:
                    container = self.client.containers.get(container_name)
                    state = {}
                    state["position"] = i
                    state["status"] = "OK"
                    state["code"] = 0
                    state["stderr"] = base64.b64encode(container.logs()).decode("utf-8")
                    self.agent_states[match_id].append(state)
                    container.kill()
                    container.remove()
                except Exception as e:
                    print(e)
            self.judge_containers.pop(match_id)

        if match_id in self.judge_networks:
            for network in self.judge_networks[match_id]:
                self.client.networks.get(network).remove()
            self.judge_networks.pop(match_id)

    def get_winner(self, match_id) -> int:
        """Get the winner of a game

        Args:
            match_id (str): The ID of the match

        Returns:
            int: The player id
        """
        with open(
            Path(self.get_name("record", match_id)) / "result.json",
            "r",
            encoding="utf-8",
        ) as f:
            return int(json.load(f)["winner"])

    def get_name(self, resource_type: str, match_id="") -> str:
        """Generates a no-duplicate name for containers and networks.

        Name format: THUAI_{type}_{judger_name}_{id} (except for "record")
        Record format: $(pwd)/record/{judger_name}/{match_id}

        Record means the folder to store the result.

        Args:
            type (str): Should be "agent", "server", "record" or "network".

        Returns:
            The name.

        Raises:
            ValueError: If type is illegal.
        """
        if resource_type == "agent":
            name = AGENT_CONTAINER_NAME_PREFIX + self.name + "_" + str(self.agent_id)
            self.agent_id = self.agent_id + 1
        elif resource_type == "server":
            name = SERVER_CONTAINER_NAME_PREFIX + self.name + "_" + str(self.server_id)
            self.server_id = self.server_id + 1
        elif resource_type == "network":
            name = NETWORK_NAME_PREFIX + self.name + "_" + str(self.network_id)
            self.network_id = self.network_id + 1
        elif resource_type == "record":
            name = str(get_judge_result_base_dir_path() / self.name / match_id)
        else:
            raise ValueError
        return name

    def stop(self) -> None:
        print("Stopping judger")
        judge_server_copy = self.judge_server.copy()
        for match_id in judge_server_copy:
            self.stop_judge(match_id)
