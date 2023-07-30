import time
import asyncio
from abc import ABCMeta, abstractmethod
from .types import SleepTime


class Deferrer(metaclass=ABCMeta):
    def current_time(self) -> int:
        """
        Get the current time in ms.
        """

        return int(round(time.time() * 1000))

    @abstractmethod
    def sleep(self, length: SleepTime) -> None:
        """
        Sleep (sync) for X ms.
        """

        pass  # pragma: no cover

    @abstractmethod
    def asleep(self, length: SleepTime) -> None:
        """
        Sleep (async) for X ms.
        """

        pass  # pragma: no cover


class SleepDeferrer(Deferrer):
    def sleep(self, length: SleepTime) -> None:
        time.sleep(length / 1000.0)

    async def asleep(self, length: SleepTime) -> None:
        asyncio.sleep(length / 1000.0)
