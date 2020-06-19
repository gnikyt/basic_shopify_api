from abc import ABCMeta, abstractmethod
from time import time, sleep

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
    return int(round(time() * 1000))

  @abstractmethod
  def sleep(self, length: int) -> None:
    """
    Sleep implementation.

    Args:
      length: The length of time to sleep in milliseconds.
    """
    pass

class SleepDeferrer(Deferrer):
  def sleep(self, length: int) -> None:
    sleep(length / 1000)
