import asyncio
import json
from websocket import WebSocketApp
import websocket

from base_agent_code_fetcher import BaseAgentCodeFetcher
from base_compile_result_sender import BaseCompileResultSender
from base_docker_image_builder import BaseDockerImageBuilder
from base_task_scheduler import BaseTaskScheduler
from compile_task import CompileTask

HEART_BEAT_INTERVAL = 3


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
    
    def __init__(self, url, judger_name, task_scheduler, fetcher, builder, cr_sender):
        self._url = url
        # self._ws = websocket.create_connection(url)
        self._judger_name = judger_name
        self._task_scheduler = task_scheduler
        self._fetcher = fetcher
        self._cr_sender = cr_sender
        self._builder = builder

    def send_heart_beat(self):
        data = {
            'type': 'heart_beat'
        }
        self._ws.send(json.dumps(data))
    
    async def keep_alive(self):
        # send heart_beat every 3 seconds asynchronizely
        while True:
            if self._ws.sock and self._ws.sock.connected:
                self.send_heart_beat()
                print("send heart beat")
            await asyncio.sleep(HEART_BEAT_INTERVAL)
    
    def send_init(self):
        data = {
            "type": "init",
            "data": {
                "description": self._judger_name,
                "address": ""
            }
        }
        
        self._ws.send(json.dumps(data))
    
    def on_message(self, ws, message):
        # parse message as json
        recv_data: dict = json.loads(message)
        type = recv_data.get("type","")
        data = recv_data.get("data",{})
        if type == "compilation_task":
            print("compilation_task")
            print(data)
            try:
                asyncio.run(self._task_scheduler.schedule(CompileTask(data["code_id"],
                                                          self._fetcher, 
                                                          self._builder, 
                                                          self._cr_sender)))
            except Exception as e:
                print(e)
    
    def on_error(self, ws, error):
        print(error)
    
    def on_close(self, ws):
        print("### closed ###")
    
    def on_open(self, ws):
        print("### opened ###")
        self.send_init()
        
    async def start(self):
        self._ws = websocket.WebSocketApp(self._url, on_message=self.on_message, 
                                          on_error=self.on_error, on_close=self.on_close)
        self._ws.on_open = self.on_open
        
        self._ws_task =asyncio.to_thread(self._ws.run_forever)
        
        self._task_scheduler_task = asyncio.create_task(self._task_scheduler.start())
        
        self._keep_alive_task = asyncio.create_task(self.keep_alive())
        
        await self._ws_task
        await self._task_scheduler_task
        await self._keep_alive_task
        
        # print("start")
        
    def stop(self):
        print("stop")
        self._ws.close()