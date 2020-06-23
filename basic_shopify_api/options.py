from http import HTTPStatus
from .store import TimeMemoryStore, CostMemoryStore
from .deferrer import SleepDeferrer
from .constants import DEFAULT_VERSION, DEFAULT_MODE, ALT_MODE, VERSION_PATTERN
import re


class Options(object):
    def __init__(self):
        self.max_retries = 2
        self.retry_on_status = [
            HTTPStatus.TOO_MANY_REQUESTS.value,
            HTTPStatus.BAD_GATEWAY.value,
            HTTPStatus.SERVICE_UNAVAILABLE.value,
            HTTPStatus.GATEWAY_TIMEOUT.value,
        ]
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.time_store = TimeMemoryStore()
        self.cost_store = CostMemoryStore()
        self.deferrer = SleepDeferrer()
        self.rest_limit = 2
        self.graphql_limit = 50
        self.rest_pre_actions = []
        self.rest_post_actions = []
        self.graphql_pre_actions = []
        self.graphql_post_actions = []
        self._version = DEFAULT_VERSION
        self._mode = DEFAULT_MODE

    @property
    def version(self) -> str:
        return self._version

    @version.setter
    def version(self, value: str) -> None:
        if not bool(re.match(VERSION_PATTERN, value)):
            raise ValueError(f"Version: {value} does not match YYYY-MM format or unstable")
        self._version = value

    @property
    def mode(self) -> str:
        return self._mode

    @mode.setter
    def mode(self, value: str) -> None:
        if value != DEFAULT_MODE and value != ALT_MODE:
            raise ValueError(f"Type must be either {DEFAULT_MODE} or {ALT_MODE}")
        self._mode = value

    @property
    def is_public(self) -> bool:
        return self.mode == DEFAULT_MODE

    @property
    def is_private(self) -> bool:
        return not self.is_public
