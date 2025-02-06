"""The implementation of the build result reporter."""

import aiohttp

from base_build_result_reporter import BaseBuildResultReporter
from build_result import BuildResult

# https API
COMPILE_RESULT_API = "/judger/codes/{}/"


class BuildResultReporter(BaseBuildResultReporter):
    """The build result reporter"""

    _session: aiohttp.ClientSession

    def __init__(self, session: aiohttp.ClientSession):
        self._session = session

    async def report(self, result: BuildResult) -> None:
        async with self._session.put(
            f"/judger/codes/{result.code_id}/",
            json={
                "compile_status": (
                    "编译成功" if result.image is not None else "编译失败"
                ),
                "compile_message": result.message,
            },
        ) as response:
            response.raise_for_status()
