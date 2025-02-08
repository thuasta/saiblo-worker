"""Main module."""

import asyncio
import logging
import os

import aiohttp
import dotenv
import yarl

from agent_code_fetcher import AgentCodeFetcher
from build_result_reporter import BuildResultReporter
from build_task import BuildTaskFactory
from docker_image_builder import DockerImageBuilder
from judge_task import JudgeTaskFactory
from match_judger import MatchJudger
from match_result_reporter import MatchResultReporter
from saiblo_client import SaibloClient
from task_scheduler import TaskScheduler


async def main():
    """Main function."""

    # Load environment variables.
    dotenv.load_dotenv()

    agent_cpus = float(os.getenv("AGENT_CPUS", "0.5"))

    agent_mem_limit = os.getenv("AGENT_MEM_LIMIT", "1g")

    game_host_cpus = float(os.getenv("GAME_HOST_CPUS", "1"))

    game_host_image = os.getenv("GAME_HOST_IMAGE")
    assert game_host_image is not None, "GAME_HOST_IMAGE must be set"

    game_host_mem_limit = os.getenv("GAME_HOST_MEM_LIMIT", "1g")

    http_base_url = yarl.URL(os.getenv("HTTP_BASE_URL", "https://api.dev.saiblo.net"))

    judge_timeout = float(os.getenv("JUDGE_TIMEOUT", "600"))

    logging_level = os.getenv("LOGGING_LEVEL", "INFO")

    name = os.getenv("NAME")
    assert name is not None, "NAME must be set"

    websocket_url = os.getenv("WEBSOCKET_URL", "wss://api.dev.saiblo.net/ws/")

    # Set up everything.
    logging.getLogger().setLevel(logging_level)

    task_scheduler = TaskScheduler()

    session = aiohttp.ClientSession(http_base_url)

    saiblo_client = SaibloClient(
        name,
        websocket_url,
        task_scheduler,
        BuildTaskFactory(
            AgentCodeFetcher(session),
            DockerImageBuilder(),
            BuildResultReporter(session),
        ),
        JudgeTaskFactory(
            game_host_image,
            AgentCodeFetcher(session),
            DockerImageBuilder(),
            BuildResultReporter(session),
            MatchJudger(
                agent_cpus=agent_cpus,
                agent_mem_limit=agent_mem_limit,
                game_host_cpus=game_host_cpus,
                game_host_mem_limit=game_host_mem_limit,
                judge_timeout=judge_timeout,
            ),
            MatchResultReporter(session),
        ),
    )

    await asyncio.gather(
        asyncio.create_task(task_scheduler.start()),
        asyncio.create_task(saiblo_client.start()),
    )

    await session.close()


if __name__ == "__main__":
    asyncio.run(main())
