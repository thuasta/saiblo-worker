"""Base class for Saiblo clients."""

from abc import ABC, abstractmethod


class BaseSaibloClient(ABC):
    """Abstract base class for Saiblo clients."""

    @abstractmethod
    async def start(self) -> None:
        """Starts the Saiblo client.

        This method should be called to start the Saiblo client and begin executing tasks. This
        method will block forever.
        """
        raise NotImplementedError
