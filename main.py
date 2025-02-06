"""Main module."""

import asyncio
import os

import aiohttp
import dotenv
import yarl

from agent_code_fetcher import AgentCodeFetcher
from build_result_reporter import BuildResultReporter
from docker_image_builder import DockerImageBuilder
from match_judger import MatchJudger
from match_result_reporter import MatchResultReporter
from saiblo_client import SaibloClient
from task_scheduler import TaskScheduler

DEFAULT_HTTP_BASE_URL = "https://api.dev.saiblo.net"
DEFAULT_WEBSOCKET_URL = "wss://api.dev.saiblo.net/ws/"


async def main():
    """Main function."""

    # Load environment variables.
    dotenv.load_dotenv()

    game_host_image = os.getenv("GAME_HOST_IMAGE")
    if game_host_image is None:
        raise ValueError("GAME_HOST_IMAGE must be set")

    name = os.getenv("NAME")
    if name is None:
        raise ValueError("NAME must be set")

    http_base_url = yarl.URL(os.getenv("HTTP_BASE_URL", DEFAULT_HTTP_BASE_URL))

    websocket_url = os.getenv("WEBSOCKET_URL", DEFAULT_WEBSOCKET_URL)

    # Set up everything.
    task_scheduler = TaskScheduler()

    async with aiohttp.ClientSession(http_base_url) as session:
        saiblo_client = SaibloClient(
            name,
            websocket_url,
            task_scheduler,
            game_host_image,
            AgentCodeFetcher(session),
            BuildResultReporter(session),
            DockerImageBuilder(),
            MatchJudger(),
            MatchResultReporter(session),
        )

        await asyncio.gather(
            asyncio.create_task(task_scheduler.start()),
            asyncio.create_task(saiblo_client.start()),
        )


if __name__ == "__main__":
    asyncio.run(main())
