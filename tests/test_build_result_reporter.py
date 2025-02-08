"""Tests for the build result reporter."""

from unittest import IsolatedAsyncioTestCase

import aiohttp

from saiblo_worker.build_result import BuildResult
from saiblo_worker.build_result_reporter import BuildResultReporter

CODE_ID = "7c562b10-287f-44c0-8fc4-0cf853a1859b"
HTTP_BASE_URL = "https://api.dev.saiblo.net"


class TestBuildResultReporter(IsolatedAsyncioTestCase):
    """Tests for the BuildResultReporter class."""

    _session: aiohttp.ClientSession

    async def asyncSetUp(self) -> None:
        self._session = aiohttp.ClientSession(HTTP_BASE_URL)

    async def asyncTearDown(self) -> None:
        await self._session.close()

    async def test_report_failed(self):
        """Test report() when failed."""
        # Arrange.
        build_result = BuildResult(
            code_id=CODE_ID,
            image=None,
            message="message",
        )
        reporter = BuildResultReporter(self._session)

        # Act.
        await reporter.report(build_result)

    async def test_report_success(self):
        """Test report() when success."""
        # Arrange.
        build_result = BuildResult(
            code_id=CODE_ID,
            image="image",
            message="message",
        )
        reporter = BuildResultReporter(self._session)

        # Act.
        await reporter.report(build_result)
