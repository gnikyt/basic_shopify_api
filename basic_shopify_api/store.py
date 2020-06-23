from .models import Session
from abc import ABC, abstractmethod
from typing import List
from .types import StoreValue, StoreContainer


class StateStore(ABC):
    def __init__(self):
        self.container: StoreContainer = {}

    @abstractmethod
    def all(self, session: Session) -> List[StoreValue]:
        pass  # pragma: no cover

    @abstractmethod
    def append(self, session: Session, value: StoreValue) -> None:
        pass  # pragma: no cover

    @abstractmethod
    def reset(self, session: Session) -> None:
        pass  # pragma: no cover


class TimeMemoryStore(StateStore):
    def all(self, session: Session) -> List[StoreValue]:
        domain = session.domain
        if domain not in self.container:
            self.reset(session)
        return self.container[domain]

    def append(self, session: Session, value: StoreValue) -> None:
        domain = session.domain
        if domain not in self.container:
            self.reset(session)
        self.container[domain].append(value)

    def reset(self, session: Session) -> None:
        self.container[session.domain] = []


class CostMemoryStore(StateStore):
    def all(self, session: Session) -> List[StoreValue]:
        domain = session.domain
        if domain not in self.container:
            self.reset(session)
        return self.container[domain]

    def append(self, session: Session, value: StoreValue) -> None:
        domain = session.domain
        if domain not in self.container:
            self.reset(session)
        self.container[domain].append(value)

    def reset(self, session: Session) -> None:
        self.container[session.domain] = []
