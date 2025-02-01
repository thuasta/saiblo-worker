import time
from aiohttp_session_manager import AiohttpSessionManager
from base_task_scheduler import BaseTaskScheduler
from build_task import BuildTask
from match_result import MatchResult
from thuai_builder import ThuaiBuilder
from thuai_cr_sender import ThuaiCRSender
from thuai_fetcher import ThuaiFetcher
from thuai_judger import ThuaiJudger
from thuai_reporter import ThuaiReporter
import asyncio

from thuai_task_scheduler import ThuaiTaskScheduler
from ws_client import WsClient

BASE_URL = "https://api.dev.saiblo.net/"

async def testWsClient():
    async with AiohttpSessionManager().get_session(BASE_URL) as http_session:
        ws_client = WsClient(
            "wss://api.dev.saiblo.net/ws/",
            "thuai8judger",
            ThuaiTaskScheduler(),
            ThuaiFetcher(session=http_session),
            ThuaiBuilder(),
            ThuaiCRSender(session=http_session),
            ThuaiJudger(),
            ThuaiReporter(session=http_session),
            "thuai7judger:latest",
        )
        await ws_client.start()
        print("WsClient started")
        # # print('qwdhkdjwqieuo')
        # time.sleep(10)
        # # print("qhjdqkjwhdjk")
        # ws_client.stop()
        # time.sleep(2)
        # ws_client.start()
        # time.sleep(20)
        # ws_client.stop()

async def testReporter():
    async with AiohttpSessionManager().get_session(BASE_URL) as http_session:
        reporter = ThuaiReporter(session=http_session)
        match_result = MatchResult(
            match_id="7716",
            success=False,
            scores=[0, 0],
            err_msg="Test error message",
            record_file_path="test.dat"
        )
        await reporter.report(match_result)

async def main():
    await testWsClient()
    # await testReporter()


if __name__ == "__main__":
    # asyncio.run(fetch())
    # asyncio.run(clean())
    # print(asyncio.run(buildTask()))
    # asyncio.run(buildTask())
    # print(asyncio.run(compileTask()))
    # testWsClient()
    asyncio.run(main())
