import time
from base_task_scheduler import BaseTaskScheduler
from build_task import BuildTask
from compile_task import CompileTask
from thuai_builder import ThuaiBuilder
from thuai_cr_sender import ThuaiCRSender
from thuai_fetcher import ThuaiFetcher
from thuai_judger import ThuaiJudger
from thuai_reporter import ThuaiReporter
import asyncio

from thuai_task_scheduler import ThuaiTaskScheduler
from ws_client import WsClient

async def fetch():
    await ThuaiFetcher().fetch("cbd96c3c5a934e0cabac0a3f006a823b")

async def clean():
    await ThuaiFetcher().clean()

async def buildTask():
    return await BuildTask("cbd96c3c5a934e0cabac0a3f006a823b", 
                    ThuaiFetcher(), 
                    ThuaiBuilder()).execute()
    
async def compileTask():
    return await CompileTask("cbd96c3c5a934e0cabac0a3f006a823b", 
                             ThuaiFetcher(), ThuaiBuilder(), ThuaiCRSender()).execute()

async def testWsClient():
    ws_client=WsClient("wss://api.dev.saiblo.net/ws/", "thuai8judger", 
                        ThuaiTaskScheduler(), 
                        ThuaiFetcher(), 
                        ThuaiBuilder(), 
                        ThuaiCRSender(), 
                        ThuaiJudger(), 
                        ThuaiReporter(), 
                        "thuai7judger:latest")
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
    
async def main():
    await testWsClient()

if __name__ == "__main__":
    # asyncio.run(fetch())
    # asyncio.run(clean())
    # print(asyncio.run(buildTask()))
    # asyncio.run(buildTask())
    # print(asyncio.run(compileTask()))
    # testWsClient()
    asyncio.run(main())
    