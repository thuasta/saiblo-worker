"""Tests for the match_reslt_reporter module."""

import pathlib
import shutil
import unittest

import aiohttp

from saiblo_worker.match_result import MatchResult
from saiblo_worker.match_result_reporter import MatchResultReporter

HTTP_BASE_URL = "https://api.dev.saiblo.net"
MATCH_ID = "7729"


class TestMatchResultReporter(unittest.IsolatedAsyncioTestCase):
    """Tests for the MatchResultReporter class."""

    _session: aiohttp.ClientSession

    async def asyncSetUp(self) -> None:
        shutil.rmtree(
            pathlib.Path("data"),
            ignore_errors=True,
        )

        self._session = aiohttp.ClientSession(HTTP_BASE_URL)

    async def asyncTearDown(self) -> None:
        shutil.rmtree(
            pathlib.Path("data"),
            ignore_errors=True,
        )

        await self._session.close()

    async def test_report_failed(self):
        """Test report() when failed."""
        # Arrange.
        result = MatchResult(
            match_id=MATCH_ID,
            agent_results=[
                MatchResult.AgentResult(
                    exit_code=0,
                    score=0,
                    status="OK",
                    stderr_output="stderr_output 0".encode(),
                ),
                MatchResult.AgentResult(
                    exit_code=1,
                    score=1,
                    status="UE",
                    stderr_output="stderr_output 1".encode(),
                ),
            ],
            error_message="error_message",
            replay_file_path=None,
            stderr_output="stderr_output".encode(),
        )
        reporter = MatchResultReporter(self._session)

        # Act.
        await reporter.report(result)

    async def test_report_success(self):
        """Test report() when success."""
        # Arrange.
        path = pathlib.Path(f"data/match_replays/{MATCH_ID}.dat")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()

        result = MatchResult(
            match_id=MATCH_ID,
            agent_results=[
                MatchResult.AgentResult(
                    exit_code=0,
                    score=0,
                    status="OK",
                    stderr_output="stderr_output 0".encode(),
                ),
                MatchResult.AgentResult(
                    exit_code=1,
                    score=1,
                    status="UE",
                    stderr_output="stderr_output 1".encode(),
                ),
            ],
            error_message="error_message",
            replay_file_path=str(path),
            stderr_output="stderr_output".encode(),
        )
        reporter = MatchResultReporter(self._session)

        # Act.
        await reporter.report(result)
