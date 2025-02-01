import io
from pathlib import Path
import tarfile
from typing import Dict
import zipfile

import aiohttp
from base_agent_code_fetcher import BaseAgentCodeFetcher
import shutil

from path_manager import get_agent_code_base_dir_path

# https API
CODE_INFO_API = "/judger/codes/{}"
CODE_DOWNLOAD_API = "/judger/codes/{}/download"


class ThuaiFetcher(BaseAgentCodeFetcher):
    """Fetches agent code for THUAI."""
    
    _session: aiohttp.ClientSession
    
    def __init__(self, session: aiohttp.ClientSession):
        self._session = session

    async def clean(self) -> None:
        """Cleans up fetched resources."""
        shutil.rmtree(get_agent_code_base_dir_path(), ignore_errors=True)

    async def fetch(self, code_id: str) -> Path:
        """Fetches the code for an agent and saves it to a directory(containing the dockerfile)

        If the file already exists, the agent code will not be fetched again. So it is OK to call
        this method to lookup the result.

        Args:
            code_id: The ID of the code to fetch

        Returns:
            The path to the directory where the code should be saved
        """
        # if fetched_codes/code_id exists, return
        if Path(f"fetched_codes/{code_id}").exists():
            return Path(f"fetched_codes/{code_id}")

        # get code info
        # code_info = requests.get(CODE_INFO_API.format(code_id)).json()
        # get code download link
        code_download_link = CODE_DOWNLOAD_API.format(code_id)
        # download code
        async with self._session.get(code_download_link) as code_zip:
            content = await code_zip.read()
            if code_zip.status == 200:
                zip_file = zipfile.ZipFile(io.BytesIO(content))
                tar_path = get_agent_code_base_dir_path() / f"{code_id}.tar"
                tar_path.parent.mkdir(parents=True, exist_ok=True)
                with tarfile.open(tar_path, "w") as tar:
                    for file_name in zip_file.namelist():
                        if file_name.endswith("/"):
                            continue
                        file_data = zip_file.read(file_name)
                        tarinfo = tarfile.TarInfo(name=file_name)
                        tarinfo.size = len(file_data)
                        tar.addfile(tarinfo, io.BytesIO(file_data))
                return tar_path
            else:
                raise Exception("Failed to download code: " + code_zip.status)

    async def list(self) -> Dict[str, Path]:
        """Lists all the code IDs that are already fetched.

        Returns:
            A dictionary mapping code IDs to the paths of their corresponding tarball files
        """
        pass
