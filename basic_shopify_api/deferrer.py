import time
import asyncio
from abc import ABCMeta, abstractmethod


class Deferrer(metaclass=ABCMeta):
    """
    Base deferrer implementation, an abstract class.
    """
    def current_time(self) -> int:
        """
        Get the current time.

        Returns:
            Time in milliseconds.
        """
        return int(round(time.time() * 1000))

    @abstractmethod
    def sleep(self, length: int) -> None:
        """
        Sleep implementation (sync).

        Args:
            length: The length of time to sleep in milliseconds.
        """
        pass  # pragma: no cover

    @abstractmethod
    def asleep(self, length: int) -> None:
        """
        Sleep implementation (async).

        Args:
            length: The length of time to sleep in milliseconds.
        """
        pass  # pragma: no cover


class SleepDeferrer(Deferrer):
    def sleep(self, length: int) -> None:
        time.sleep(length / 1000.0)

    async def asleep(self, length: int) -> None:
        asyncio.sleep(length / 1000.0)
