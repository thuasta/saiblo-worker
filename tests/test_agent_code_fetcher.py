import shutil
from pathlib import Path
from unittest import IsolatedAsyncioTestCase

import aiohttp

import agent_code_fetcher

CODE_ID = "a09f660a-e0e6-41ac-b721-f8ece8e71f33"
HTTP_BASE_URL = "https://api.dev.saiblo.net"


class TestAgentCodeFetcher(IsolatedAsyncioTestCase):
    _session: aiohttp.ClientSession

    async def asyncSetUp(self) -> None:
        shutil.rmtree(
            Path("data"),
            ignore_errors=True,
        )

        self._session = aiohttp.ClientSession(HTTP_BASE_URL)

    def tearDown(self) -> None:
        shutil.rmtree(
            Path("data"),
            ignore_errors=True,
        )

    async def test_clean_no_dir(self):
        # Arrange.
        fetcher = agent_code_fetcher.AgentCodeFetcher(self._session)

        # Act.
        await fetcher.clean()

        # Assert.
        self.assertTrue(Path("data/agent_code").is_dir())

    async def test_clean_dir_exists(self):
        # Arrange.
        Path("data/agent_code").mkdir(parents=True, exist_ok=True)
        fetcher = agent_code_fetcher.AgentCodeFetcher(self._session)

        # Act.
        await fetcher.clean()

        # Assert.
        self.assertTrue(
            Path("data/agent_code").is_dir(),
        )

    async def test_fetch_cached(self):
        # Arrange.
        Path("data/agent_code").mkdir(parents=True, exist_ok=True)
        path = Path("data/agent_code") / f"{CODE_ID}.tar"
        path.touch()
        fetcher = agent_code_fetcher.AgentCodeFetcher(self._session)

        # Act.
        result = await fetcher.fetch(CODE_ID)

        # Assert.
        self.assertEqual(path.absolute(), result)

    async def test_fetch_not_cached(self):
        # Arrange.
        path = Path("data/agent_code") / f"{CODE_ID}.tar"
        fetcher = agent_code_fetcher.AgentCodeFetcher(self._session)

        # Act.
        result = await fetcher.fetch(CODE_ID)

        # Assert.
        self.assertEqual(path.absolute(), result)
        self.assertTrue(path.is_file())

    async def test_list(self):
        # Arrange.
        Path("data/agent_code").mkdir(parents=True, exist_ok=True)
        path = Path("data/agent_code") / f"{CODE_ID}.tar"
        path.touch()
        fetcher = agent_code_fetcher.AgentCodeFetcher(self._session)

        # Act.
        result = await fetcher.list()

        # Assert.
        self.assertEqual({CODE_ID: path.absolute()}, result)
