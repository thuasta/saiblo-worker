"""The implementation of the agent code fetcher."""

import io
import shutil
import tarfile
import zipfile
from pathlib import Path
from typing import Dict

import aiohttp

import saiblo_worker.path_manager as path_manager
from saiblo_worker.base_agent_code_fetcher import BaseAgentCodeFetcher


class AgentCodeFetcher(BaseAgentCodeFetcher):
    """The agent code fetcher"""

    _session: aiohttp.ClientSession

    def __init__(self, session: aiohttp.ClientSession):
        """Initializes the agent code fetcher.

        Args:
            session: The aiohttp client session initialized with the base URL of the API
        """
        self._session = session

    async def clean(self) -> None:
        agent_code_base_dir_path = path_manager.get_agent_code_base_dir_path()

        if agent_code_base_dir_path.is_dir():
            shutil.rmtree(agent_code_base_dir_path, ignore_errors=True)

    async def fetch(self, code_id: str) -> Path:
        agent_code_tarball_path = path_manager.get_agent_code_tarball_path(code_id)
        agent_code_tarball_path.parent.mkdir(parents=True, exist_ok=True)

        # If fetched, return the cached tarball.
        if agent_code_tarball_path.is_file():
            return agent_code_tarball_path

        async with self._session.get(f"/judger/codes/{code_id}/download") as response:
            # If not OK, raise an exception.
            response.raise_for_status()

            bytes_ = await response.content.read()

        zip_file = zipfile.ZipFile(io.BytesIO(bytes_))

        with tarfile.open(agent_code_tarball_path, "w") as tar_file:
            for file_name in zip_file.namelist():
                # Skip directories.
                if file_name.endswith("/"):
                    continue

                file_data = zip_file.read(file_name)

                tar_info = tarfile.TarInfo(name=file_name)
                tar_info.size = len(file_data)

                tar_file.addfile(tar_info, io.BytesIO(file_data))

        return agent_code_tarball_path

    async def list(self) -> Dict[str, Path]:
        agent_code_tarball_paths = path_manager.get_agent_code_tarball_paths()

        return {path.stem: path for path in agent_code_tarball_paths if path.is_file()}
