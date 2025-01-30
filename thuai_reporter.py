import json
from match_result import MatchResult
from base_match_result_reporter import BaseMatchResultReporter
import requests

MATCH_REPORT_API = "https://api.dev.saiblo.net/judger/matches/{}/"
NO_RECORD_FILE = "no_record.txt"


class ThuaiReporter(BaseMatchResultReporter):
    """Concrete implementation of BaseMatchResultReporter for THUAI."""

    async def report(self, result: MatchResult) -> None:
        """Reports the result of a match.

        Args:
            result: The result of the match
        """
        print(f"Reporting match result: {result}")
        scores = result.scores
        state = "评测成功"
        states = [
            {"position": i, "status": "OK", "code": 0, "stderr": ""}
            for i in range(len(scores))
        ]
        message = {}
        data = {
            "message": json.dumps(message),
            "state": state,
            "scores": json.dumps(scores),
            "states": json.dumps(states),
        }
        # json_data = json.dumps(data)
        try:
            with open(result.record_file_path, "rb") as dat_file:
                files = {"file": (f"{result.match_id}.dat", dat_file)}
                response = requests.put(
                    MATCH_REPORT_API.format(result.match_id), files=files, data=data
                )
        except Exception as e:
            with open(NO_RECORD_FILE, "rb") as no_record_file:
                files = {"file": (f"{result.match_id}.txt", no_record_file)}
                response = requests.put(
                    MATCH_REPORT_API.format(result.match_id), files=files, data=data
                )
