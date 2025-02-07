"""The immplementation of the match result reporter."""

import base64
import json

import aiohttp

from base_match_result_reporter import BaseMatchResultReporter
from match_result import MatchResult

REPLAY_FILE_NAME_PREFIX = "saiblo-worker-replay"


class MatchResultReporter(BaseMatchResultReporter):
    """The match result reporter."""

    _session: aiohttp.ClientSession

    def __init__(self, session: aiohttp.ClientSession):
        self._session = session

    async def report(self, result: MatchResult) -> None:
        form_data = aiohttp.FormData(
            {
                "message": json.dumps({}),
                "state": (
                    "评测成功" if result.replay_file_path is not None else "评测失败"
                ),
                "states": json.dumps(
                    [
                        {
                            "position": i,
                            "status": agent_result.status,
                            "code": agent_result.exit_code,
                            "stderr": base64.b64encode(
                                agent_result.stderr_output.encode()
                            ).decode(),
                        }
                        for i, agent_result in enumerate(result.agent_results)
                    ]
                ),
            }
        )

        replay_file_name = f"{REPLAY_FILE_NAME_PREFIX}-{result.match_id}.dat"

        if result.replay_file_path is not None:  # If success.
            with open(result.replay_file_path, "rb") as replay_file:
                replay_file_bytes = replay_file.read()

            form_data.add_field("file", replay_file_bytes, filename=replay_file_name)

            form_data.add_field(
                "scores",
                json.dumps(
                    [agent_result.score for agent_result in result.agent_results]
                ),
            )

        else:
            form_data.add_field(
                "err", base64.b64encode(result.stderr_output.encode()).decode()
            )
            form_data.add_field("error", result.error_message)
            form_data.add_field("file", b"", filename=replay_file_name)

        async with self._session.put(
            f"/judger/matches/{result.match_id}/", data=form_data
        ) as response:
            response.raise_for_status()
