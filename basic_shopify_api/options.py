from typing import Pattern
from http import HTTPStatus
from .store import TimeMemoryStore, CostMemoryStore
from .deferrer import SleepDeferrer
import re

class Options(object):
  VERSION_PATTERN = r"([0-9]{4}-[0-9]{2})|unstable"
  NOT_AUTHABLE_PATTERN = r"/\/oauth\/(authorize|access_token)"
  NOT_VERSIONABLE_PATTERN = r"/\/(oauth\/access_scopes)/"
  LINK_PATTERN = r"<.*page_info=([a-zA-Z0-9\-_]+).*>; rel=\"(next|previous)\""
  RETRY_HEADER = "retry-after"
  DEFAULT_VERSION = "2020-04"
  DEFAULT_TYPE = "public"

  def __init__(self):
    self.max_retries = 2
    self.retry_on_status = [
      HTTPStatus.TOO_MANY_REQUESTS,
      HTTPStatus.BAD_GATEWAY,
      HTTPStatus.SERVICE_UNAVAILABLE,
      HTTPStatus.GATEWAY_TIMEOUT,
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
    self._version = self.DEFAULT_VERSION
    self._type = self.DEFAULT_TYPE
  
  @property
  def version_compiled(self) -> Pattern:
    return re.compile(self.VERSION_PATTERN)

  @property
  def not_authable_compiled(self) -> Pattern:
    return re.compile(self.NOT_AUTHABLE_PATTERN)

  @property
  def not_versionable_compiled(self) -> Pattern:
    return re.compile(self.NOT_VERSIONABLE_PATTERN)

  @property
  def link_compiled(self) -> Pattern:
    return re.compile(self.LINK_PATTERN)

  @property
  def version(self) -> str:
    return self._version

  @version.setter
  def version(self, value: str) -> None:
    if not bool(self.version_compiled.match(value)):
      raise ValueError(f"Version: {value} does not match YYYY-MM format or unstable")
    self._version = value
  
  @property
  def type(self) -> str:
    return self._type
  
  @type.setter
  def type(self, value: str) -> None:
    if value != "public" and value != "private":
      raise ValueError("Type must be public or private")
    self._type = type

  @property
  def is_public(self) -> bool:
    return self.type == "public"
  
  @property
  def is_private(self) -> bool:
    return not self.is_public
