import json
from pathlib import Path

import aiohttp
from match_result import MatchResult
from base_match_result_reporter import BaseMatchResultReporter

MATCH_REPORT_API = "/judger/matches/{}/"
NO_RECORD_FILE = "no_record.txt"


class ThuaiReporter(BaseMatchResultReporter):
    """Concrete implementation of BaseMatchResultReporter for THUAI."""
    
    _session: aiohttp.ClientSession
    
    def __init__(self, session: aiohttp.ClientSession):
        self._session = session

    async def report(self, result: MatchResult) -> None:
        """Reports the result of a match.

        Args:
            result: The result of the match
        """
        print(f"Reporting match result: {result}")
        scores = result.scores
        state = "评测成功"
        if not result.success:
            state = "评测失败"
        states = [
            {"position": i, "status": "OK", "code": 0, "stderr": "No stderr."}
            for i in range(len(scores))
        ]
        message = {}
        error = result.err_msg
        data = aiohttp.FormData()
        data.add_field("state", state)
        data.add_field("scores", json.dumps(scores))
        data.add_field("states", json.dumps(states))
        data.add_field("message", json.dumps(message))
        data.add_field("error", error)
        # check if record file exists using Path.exists()
        record_file_path = result.record_file_path
        if not record_file_path or not Path(record_file_path).exists():
            record_file_path = NO_RECORD_FILE
        ext=Path(record_file_path).suffix
        with open(record_file_path, "rb") as dat_file:
            # files = {"file": (f"{result.match_id}.dat", dat_file)}
            data.add_field("file", dat_file, filename=f"{result.match_id}.{ext}")
            async with self._session.put(
                MATCH_REPORT_API.format(result.match_id), data=data
            ) as response:
                await response.text()
        
        
