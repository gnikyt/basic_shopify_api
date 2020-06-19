from collections import UserDict
from .session import Session
from abc import ABC, abstractmethod
from typing import List

class StateStore(ABC):
  def __init__(self):
    self.container: Dict[str, List[int]] = {}

  @abstractmethod
  def all(self, session: Session) -> List[int]:
    pass

  @abstractmethod
  def append(self, session: Session, value: int) -> None:
    pass

  @abstractmethod
  def reset(self, session: Session) -> None:
    pass

class TimeMemoryStore(StateStore):
  def all(self, session: Session) -> List[int]:
    domain = session.domain
    if not domain in self.container:
      self.reset(session)
    return self.container[domain]

  def append(self, session: Session, value: int) -> None:
    domain = session.domain
    if not domain in self.container:
      self.reset(session)
    self.container[domain].append(value)

  def reset(self, session: Session) -> None:
    self.container[session.domain] = []

class CostMemoryStore(StateStore):
  def all(self, session: Session) -> List[int]:
    domain = session.domain
    if not domain in self.container:
      self.reset(session)
    return self.container[domain]

  def append(self, session: Session, value: int) -> None:
    domain = session.domain
    if not domain in self.container:
      self.reset(session)
    self.container[domain].append(value)

  def reset(self, session: Session) -> None:
    self.container[session.domain] = []
