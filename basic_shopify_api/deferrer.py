import time
import asyncio
from abc import ABCMeta, abstractmethod


class Deferrer(metaclass=ABCMeta):
    def current_time(self) -> int:
        return int(round(time.time() * 1000))

    @abstractmethod
    def sleep(self, length: int) -> None:
        pass  # pragma: no cover

    @abstractmethod
    def asleep(self, length: int) -> None:
        pass  # pragma: no cover


class SleepDeferrer(Deferrer):
    def sleep(self, length: int) -> None:
        time.sleep(length / 1000.0)

    async def asleep(self, length: int) -> None:
        asyncio.sleep(length / 1000.0)
