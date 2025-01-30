"""Compile result sender for thuai."""

import requests

from base_compile_result_sender import BaseCompileResultSender

# https API
COMPILE_RESULT_API = "https://api.dev.saiblo.net/judger/codes/{}/"


class ThuaiCRSender(BaseCompileResultSender):
    """Compile result sender for thuai."""

    async def send(self, code_id: str, status: bool, message: str) -> None:
        status_str = "编译成功" if status else "编译失败"
        print(
            f"Sending compile result for {code_id}: {status_str} with message: {message}"
        )
        # use method PUT to update compile result
        requests.put(
            COMPILE_RESULT_API.format(code_id),
            json={"compile_status": status_str, "compile_message": message},
        )
