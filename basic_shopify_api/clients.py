from httpx import Client as HttpxClient, AsyncClient as AsyncHttpxClient
from httpx._types import HeaderTypes, QueryParamTypes, PrimitiveData
from httpx._models import Response
from typing import Pattern, Dict, Tuple, Union, Awaitable
from time import sleep
from .session import Session
from .models import RestLink, RestResult, ApiResult
from .options import Options
import datetime

DataDict = Dict[str, PrimitiveData]

class ApiCommon:
  ONE_SECOND = 1000

  def is_authable_request(self, path: str) -> bool:
    return not bool(self.options.not_authable_compiled.match(path))
  
  def is_versionable_request(self, path: str) -> bool:
    return not bool(self.options.not_versionable_compiled.match(path))

  def version_path(self, path: str, ignore_check: bool=False) -> str:
    replace_path = lambda: path.replace("/api", f"/api/{self.options.version}")
    if ignore_check:
      return replace_path()

    ignore_versioning = (
      not self.is_authable_request(path)
      or not self.is_versionable_request(path)
      or self.options.version in path
    )
    return path if ignore_versioning else replace_path()

  def _rest_extract_link(self, headers: HeaderTypes) -> RestLink:
    link = {}
    if "link" in headers:
      results = self.options.link_compiled.findall(headers["link"])
      if len(results) > 0:
        for result in results:
          link[result[1]] = result[0]
    return RestLink(
      next=link.get("next", None),
      prev=link.get("prev", None),
    )

  def _rest_rate_limit(self) -> None:
    deferrer = self.options.deferrer
    time_store = self.options.time_store
    all_time = time_store.all(self.session)

    if len(all_time) >= self.options.rest_limit:
      current_time = deferrer.current_time()
      window_time = all_time[0] + self.ONE_SECOND
      time_store.reset(self.session)

      if current_time < window_time:
        deferrer.sleep(window_time - current_time)
    time_store.append(self.session, deferrer.current_time())
  
  def _cost_rate_limit(self) -> None:
    deferrer = self.options.deferrer
    time_store = self.options.time_store
    cost_store = self.options.cost_store
    all_time = time_store.all(self.session)
    all_cost = cost_store.all(self.session)

    if len(all_time) == 0 or len(all_cost) == 0:
      return

    last_time = all_time[-1]
    last_cost = all_cost[-1]
    time_diff = deferrer.current_time() - last_time
    points_per_sec = self.options.graphql_limit

    if time_diff < self.ONE_SECOND and last_cost > points_per_sec:
      deferrer.sleep(self.ONE_SECOND - time_diff)

    time_store.reset(self.session)
    time_store.append(self.session, deferrer.current_time())

  def _cost_update(self, body: Response) -> None:
    if "extensions" not in body:
      return

    cost_store = self.options.cost_store
    cost_store.append(self.session, int(body["extensions"]["cost"]["actualCost"]))

  def _parse_response(self, response: Response) -> Tuple:
    errors = None
    try:
      body = response.json()
      if "errors" in body:
        errors = body["errors"]
      elif "error" in body:
        errors = body["error"]
    except:
      body = response.text
      errors = True if "error" in body else None
    return (body, errors)

  def _retry_required(self, response: Response, retries: int) -> Union[bool, float]:
    if response.status_code in self.options.retry_on_status and retries < self.options.max_retries:
      if self.options.RETRY_HEADER in response.headers:
        return float(response.headers[self.options.RETRY_HEADER]) * self.ONE_SECOND
    return False

  def _rest_pre_actions(self) -> None:
    self._rest_rate_limit()
    [meth(self) for meth in self.options.rest_pre_actions]

  def _graphql_pre_actions(self) -> None:
    self._cost_rate_limit()
    [meth(self) for meth in self.options.graphql_pre_actions]
  
  def _rest_post_actions(self, response: Response) -> RestResult:
    (body, errors) = self._parse_response(response)
    [meth(self, response, body, errors) for meth in self.options.rest_post_actions]

    return RestResult(
      response=response,
      status=response.status_code,
      body=body,
      errors=errors,
      link=self._rest_extract_link(response.headers),
    )
  
  def _graphql_post_actions(self, response: Response) -> ApiResult:
    (body, errors) = self._parse_response(response)
    self._cost_update(body)
    [meth(self, response, body, errors) for meth in self.options.graphql_post_actions]

    return ApiResult(
      response=response,
      status=response.status_code,
      body=body,
      errors=errors,
    )

class Client(HttpxClient, ApiCommon):
  def __init__(
      self,
      session: Session,
      options: Options,
      **kwargs
  ):
    self.session = session
    self.options = options
    super().__init__(
      base_url=f"https://{self.session.domain}",
      auth=None if self.options.is_public else (self.session.key, self.session.password),
      *kwargs
    )

  def _retry_request(meth: callable) -> callable:
    def wrapper(*args, **kwargs) -> ApiResult:
      inst: Client = args[0]
      retries: int = kwargs.get("retries", 0)
      result: ApiResult = meth(*args, **kwargs)
      response: Response = result.response

      retry = inst._retry_required(response, retries)
      if retry is not False:
        inst.options.deferrer.sleep(retry)
        return inst.rest(*args[1:], **kwargs, retries=retries + 1)
      return result
    return wrapper

  @_retry_request
  def rest(self, method: str, path: str, params: QueryParamTypes=None, headers: HeaderTypes={}, retries: int=0) -> RestResult:
    self._rest_pre_actions()
    meth = getattr(self, method)
    response = meth(
      url=self.version_path(path),
      headers={**self.options.headers, **headers},
      params=params,
    )
    return self._rest_post_actions(response)

  @_retry_request
  def graphql(self, query: str, variables: DataDict=None) -> ApiResult:
    self._graphql_pre_actions()
    response = self.post(
      url=self.version_path("/admin/api/graphql.json", True),
      json={
        "query": query,
        "variables": variables,
      }
    )
    return self._graphql_post_actions(response)

class AsyncClient(AsyncHttpxClient, ApiCommon):
  def __init__(
      self,
      session: Session,
      options: Options,
      **kwargs
  ):
    self.session = session
    self.options = options
    super().__init__(
      base_url=f"https://{self.session.domain}",
      auth=None if self.options.is_public else (self.session.key, self.session.password),
      *kwargs
    )

  def _retry_request(meth: callable) -> callable:
    async def wrapper(*args, **kwargs) -> ApiResult:
      inst: AsyncClient = args[0]
      retries = kwargs.get("retries", 0)
      result: ApiResult = await meth(*args, **kwargs)
      response = result.response

      retry = inst._retry_required(response, retries)
      if retry is not False:
        await inst.options.deferrer.asleep(retry)
        return inst.rest(*args[1:], **kwargs, retries=retries + 1)
      return result
    return wrapper

  @_retry_request
  async def rest(self, method: str, path: str, params: QueryParamTypes=None, headers: HeaderTypes={}, retries: int=0) -> RestResult:
    self._rest_pre_actions()
    meth = getattr(self, method)
    response = await meth(
      url=self.version_path(path),
      headers={**self.options.headers, **headers},
      params=params,
    )
    return self._rest_post_actions(response)

  @_retry_request
  async def graphql(self, query: str, variables: DataDict=None) -> ApiResult:
    self._graphql_pre_actions()
    response = await self.post(
      url=self.version_path("/admin/api/graphql.json", True),
      json={
        "query": query,
        "variables": variables,
      }
    )
    return self._graphql_post_actions(response)
