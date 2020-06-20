from httpx import Client as HttpxClient, AsyncClient as AsyncHttpxClient
from httpx._types import HeaderTypes, QueryParamTypes
from httpx._models import Response
from typing import Pattern, Tuple, Union
from .session import Session
from .models import RestLink, RestResult, ApiResult
from .options import Options
from .constants import NOT_AUTHABLE_PATTERN, \
    NOT_VERSIONABLE_PATTERN, \
    LINK_PATTERN, \
    ACCESS_TOKEN_HEADER, \
    ONE_SECOND, \
    RETRY_HEADER
from .types import DataDict, UnionRequestData
import re


class ApiCommon:
    @property
    def regex_not_authable(self) -> Pattern:
        return re.compile(NOT_AUTHABLE_PATTERN)

    @property
    def regex_not_versionable(self) -> Pattern:
        return re.compile(NOT_VERSIONABLE_PATTERN)

    @property
    def regex_link(self) -> Pattern:
        return re.compile(LINK_PATTERN)

    def is_authable(self, path: str) -> bool:
        return not bool(self.regex_not_authable.match(path))

    def is_versionable(self, path: str) -> bool:
        return not bool(self.regex_not_versionable.match(path))

    def replace_path(self, path: str) -> str:
        return path.replace("/api", f"/api/{self.options.version}")

    def version_path(self, path: str, ignore_check: bool = False) -> str:
        if ignore_check:
            return self.replace_path(path)

        ignore_versioning = (
            not self.is_authable(path) or
            not self.is_versionable(path) or
            self.options.version in path
        )
        return path if ignore_versioning else self.replace_path(path)

    def _build_headers(self, headers: HeaderTypes) -> HeaderTypes:
        if self.options.is_private:
            headers = {ACCESS_TOKEN_HEADER: self.session.password, **headers}
        return {**self.options.headers, **headers}

    def _build_request(
        self,
        method: str,
        path: str,
        params: UnionRequestData = {},
        headers: HeaderTypes = {}
    ) -> dict:
        kwargs = {
            "url": self.version_path(path),
            "headers": self._build_headers(headers),
        }
        if method == "get":
            kwargs["params"] = params
        else:
            kwargs["json"] = params
        return kwargs

    def _rest_extract_link(self, headers: HeaderTypes) -> RestLink:
        link = {}
        if "link" in headers:
            results = self.regex_link.findall(headers["link"])
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
            window_time = all_time[0] + ONE_SECOND
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

        if time_diff < ONE_SECOND and last_cost > points_per_sec:
            deferrer.sleep(ONE_SECOND - time_diff)

        time_store.reset(self.session)
        time_store.append(self.session, deferrer.current_time())

    def _cost_update(self, body: Response) -> None:
        if "extensions" not in body:
            return
        cost_store = self.options.cost_store
        cost_store.append(self.session, int(body["extensions"]["cost"]["actualQueryCost"]))

    def _parse_response(self, response: Response) -> Tuple:
        errors = None
        try:
            body = response.json()
            if "data" in body:
                body = body["data"]
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
            if RETRY_HEADER in response.headers:
                return float(response.headers[RETRY_HEADER]) * ONE_SECOND
        return False

    def _rest_pre_actions(self, **kwargs) -> None:
        self._rest_rate_limit()
        [meth(self, **kwargs) for meth in self.options.rest_pre_actions]

    def _graphql_pre_actions(self, **kwargs) -> None:
        self._cost_rate_limit()
        [meth(self, **kwargs) for meth in self.options.graphql_pre_actions]

    def _rest_post_actions(self, response: Response) -> RestResult:
        (body, errors) = self._parse_response(response)
        result = RestResult(
            response=response,
            status=response.status_code,
            body=body,
            errors=errors,
            link=self._rest_extract_link(response.headers),
        )

        [meth(self, result) for meth in self.options.rest_post_actions]
        return result

    def _graphql_post_actions(self, response: Response) -> ApiResult:
        (body, errors) = self._parse_response(response)
        self._cost_update(body)
        result = ApiResult(
            response=response,
            status=response.status_code,
            body=body,
            errors=errors,
        )

        [meth(self, result) for meth in self.options.graphql_post_actions]
        return result


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
            **kwargs
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
    def rest(
        self,
        method: str,
        path: str,
        params: UnionRequestData = None,
        headers: HeaderTypes = {},
        retries: int = 0
    ) -> RestResult:
        meth = getattr(self, method)
        kwargs = self._build_request(method, path, params, headers)
        self._rest_pre_actions(**kwargs)
        response = meth(**kwargs)
        return self._rest_post_actions(response)

    @_retry_request
    def graphql(self, query: str, variables: DataDict = None) -> ApiResult:
        kwargs = self._build_request(
            "post",
            "/admin/api/graphql.json",
            {
                "query": query,
                "variables": variables,
            },
        )
        self._graphql_pre_actions(**kwargs)
        response = self.post(**kwargs)
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
            **kwargs
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
    async def rest(
        self,
        method: str,
        path: str,
        params: QueryParamTypes = None,
        headers: HeaderTypes = {},
        retries: int = 0
    ) -> RestResult:
        meth = getattr(self, method)
        kwargs = self._build_request(method, path, params, headers)
        self._rest_pre_actions(**kwargs)
        response = await meth(**kwargs)
        return self._rest_post_actions(response)

    @_retry_request
    async def graphql(self, query: str, variables: DataDict = None) -> ApiResult:
        kwargs = self._build_request(
            "post",
            "/admin/api/graphql.json",
            {
                "query": query,
                "variables": variables,
            },
        )
        self._graphql_pre_actions(**kwargs)
        response = await self.post(**kwargs)
        return self._graphql_post_actions(response)
