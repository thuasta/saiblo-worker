import asyncio
import json

# import threading
from websocket import WebSocketApp
import websocket

from base_agent_code_fetcher import BaseAgentCodeFetcher
from base_compile_result_sender import BaseCompileResultSender
from base_docker_image_builder import BaseDockerImageBuilder
from base_match_judger import BaseMatchJudger
from base_match_result_reporter import BaseMatchResultReporter
from base_task_scheduler import BaseTaskScheduler
from build_task import BuildTask
from judge_task import JudgeTask

HEART_BEAT_INTERVAL = 1
TASK_REQUEST_INTERVAL = 1


class WsClient:

    _url: str
    _ws: WebSocketApp
    _ws_task: asyncio.Task
    _judger_name: str
    _keep_alive_task: asyncio.Task
    _task_scheduler: BaseTaskScheduler
    _task_scheduler_task: asyncio.Task
    _fetcher: BaseAgentCodeFetcher
    _cr_sender: BaseCompileResultSender
    _builder: BaseDockerImageBuilder
    _running: bool = False
    _keep_request_judge_task: asyncio.Task
    _judger: BaseMatchJudger
    _reporter: BaseMatchResultReporter
    _game_host_image_tag: str
    _judge_task_receive_flag: bool = True

    def __init__(
        self,
        url,
        judger_name,
        task_scheduler,
        fetcher,
        builder,
        cr_sender,
        judger,
        reporter,
        game_host_image_tag,
    ):
        self._url = url
        # self._ws = websocket.create_connection(url)
        self._judger_name = judger_name
        self._task_scheduler = task_scheduler
        self._fetcher = fetcher
        self._cr_sender = cr_sender
        self._builder = builder
        self._judger = judger
        self._reporter = reporter
        self._game_host_image_tag = game_host_image_tag

    def send_heart_beat(self):
        data = {"type": "heart_beat"}
        self._ws.send(json.dumps(data))

    async def keep_alive(self):
        # send heart_beat every 3 seconds asynchronizely
        while self._running:
            if self._ws.sock and self._ws.sock.connected:
                self.send_heart_beat()
                # print("send heart beat")
            await asyncio.sleep(HEART_BEAT_INTERVAL)
            # print(f"keep_alive in: {threading.current_thread().name}")
            # print("thread cnt: ", threading.active_count())

    def send_init(self):
        data = {
            "type": "init",
            "data": {"description": self._judger_name, "address": ""},
        }

        self._ws.send(json.dumps(data))

    def request_judge_task(self):
        # print("request_judge_task")
        self._judge_task_receive_flag = False
        data = {"type": "request_judge_task", "data": {"queue": 0}}
        self._ws.send(json.dumps(data))

    def report_finished_judge_task(self, match_id: int):
        print("report_finished_judge_task: ", match_id)
        data = {"type": "finish_judge_task", "data": {"match_id": match_id}}
        print(json.dumps(data))
        self._ws.send(json.dumps(data))

    async def keep_request_judge_task(self):
        while self._running:
            # print("keep_request_judge_task")
            if (
                self._ws.sock
                and self._ws.sock.connected
                and self._task_scheduler.can_accept_judge_task()
            ):
                self.request_judge_task()
                while not self._judge_task_receive_flag:
                    await asyncio.sleep(TASK_REQUEST_INTERVAL)
            else:
                await asyncio.sleep(TASK_REQUEST_INTERVAL)

    async def keep_report_finished_judge_task(self):
        while self._running:
            # print("keep_report_finished_judge_task")
            match_id = await self._task_scheduler.get_finished_judge_tasks_queue().get()
            self.report_finished_judge_task(int(match_id))

    def on_message(self, ws, message):
        # parse message as json
        recv_data: dict = json.loads(message)
        type = recv_data.get("type", "")
        data = recv_data.get("data", {})
        if type == "compilation_task":
            print("compilation_task")
            print(data)
            asyncio.run(
                self._task_scheduler.schedule(
                    BuildTask(
                        code_id=data["code_id"], 
                        fetcher=self._fetcher, 
                        builder=self._builder, 
                        sender=self._cr_sender
                    )
                )
            )
        elif type == "judge_task":
            print("judge_task")
            print(data)
            match_id = str(data["match_id"])
            player_code_ids = [player["code_id"] for player in data["players"]]

            asyncio.run(
                self._task_scheduler.schedule(
                    JudgeTask(
                        match_id,
                        player_code_ids,
                        self._game_host_image_tag,
                        self._fetcher,
                        self._builder,
                        self._judger,
                        self._reporter,
                    )
                )
            )
            self._judge_task_receive_flag = True

        # print("on message in: ", threading.current_thread().name)

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws):
        print("### closed ###")
        # reconnect

    def on_open(self, ws):
        print("### opened ###")
        self.send_init()

    async def start(self):
        self._running = True
        self._ws = websocket.WebSocketApp(
            self._url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        self._ws.on_open = self.on_open

        self._ws_task = asyncio.to_thread(self._ws.run_forever)

        self._task_scheduler_task = asyncio.create_task(self._task_scheduler.start())

        self._keep_alive_task = asyncio.create_task(self.keep_alive())

        self._keep_request_judge_task = asyncio.create_task(
            self.keep_request_judge_task()
        )

        self._keep_report_finished_judge_task = asyncio.create_task(
            self.keep_report_finished_judge_task()
        )

        await self._ws_task
        await self._task_scheduler_task
        await self._keep_alive_task
        await self._keep_request_judge_task
        await self._keep_report_finished_judge_task

        # print("start")

    def stop(self):
        self._running = False
        # print("stop")
        self._ws.close()
