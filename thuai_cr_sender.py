"""Compile result sender for thuai."""

import aiohttp

from base_compile_result_sender import BaseCompileResultSender

# https API
COMPILE_RESULT_API = "/judger/codes/{}/"


class ThuaiCRSender(BaseCompileResultSender):
    """Compile result sender for thuai."""
    
    _session: aiohttp.ClientSession
    
    def __init__(self, session: aiohttp.ClientSession):
        self._session = session

    async def send(self, code_id: str, status: bool, message: str) -> None:
        status_str = "编译成功" if status else "编译失败"
        print(
            f"Sending compile result for {code_id}: {status_str} with message: {message}"
        )
        async with self._session.put(
            COMPILE_RESULT_API.format(code_id),
            json={"compile_status": status_str, "compile_message": message},
        ) as response:
            await response.text()
