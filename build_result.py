"""Contains the build result."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class BuildResult:
    """Build result.

    Attributes:
        code_id: The code ID
        image: The built image
        message: The message of the build
    """

    code_id: str

    image: Optional[str]
    message: str
