"""Contains the base classes for compile result senders."""

from abc import ABC, abstractmethod

class BaseCompileResultSender(ABC):
    """Abstract base class for compile result senders."""

    @abstractmethod
    async def send(self, status: bool, message: str) -> None:
        """Send the result of a compile.

        Args:
            status: 1 if compile successfully, 0 if compile failed
            message: The message of the compile result
        """
        raise NotImplementedError
