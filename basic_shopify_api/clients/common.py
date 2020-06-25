from ..constants import NOT_AUTHABLE_PATTERN, \
    NOT_VERSIONABLE_PATTERN, \
    LINK_PATTERN, \
    ACCESS_TOKEN_HEADER, \
    ONE_SECOND, \
    RETRY_HEADER
from ..types import UnionRequestData, ParsedBody
from ..models import RestLink, RestResult, ApiResult
from ..constants import REST, LINK_HEADER
from httpx._types import HeaderTypes
from httpx._models import Response
from typing import Pattern, Union
import re


class ApiCommon:
    @property
    def _regex_not_authable(self) -> Pattern:
        return re.compile(NOT_AUTHABLE_PATTERN)

    @property
    def _regex_not_versionable(self) -> Pattern:
        return re.compile(NOT_VERSIONABLE_PATTERN)

    @property
    def _regex_link(self) -> Pattern:
        return re.compile(LINK_PATTERN)

    def is_authable(self, path: str) -> bool:
        return not bool(self._regex_not_authable.match(path))

    def is_versionable(self, path: str) -> bool:
        return not bool(self._regex_not_versionable.match(path))

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
        link = {"next": None, "prev": None}
        if LINK_HEADER in headers:
            results = self._regex_link.findall(headers[LINK_HEADER])
            for result in results:
                link[result[1]] = result[0]
        return RestLink(**link)

    def _rest_rate_limit_required(self) -> Union[bool, int]:
        all_time = self.options.time_store.all(self.session)
        if len(all_time) < self.options.rest_limit:
            return False

        current_time = self.options.deferrer.current_time()
        window_time = all_time[0] + ONE_SECOND
        self.options.time_store.reset(self.session)
        return False if current_time > window_time else window_time - current_time

    def _graphql_cost_limit_required(self) -> Union[bool, int]:
        all_time = self.options.time_store.all(self.session)
        all_cost = self.options.cost_store.all(self.session)
        if len(all_time) == 0 or len(all_cost) == 0:
            return False

        last_time, last_cost = all_time[-1], all_cost[-1]
        time_diff = self.options.deferrer.current_time() - last_time
        points_per_sec = self.options.graphql_limit

        self.options.time_store.reset(self.session)
        self.options.cost_store.reset(self.session)
        return False if time_diff > ONE_SECOND or last_cost < points_per_sec else ONE_SECOND - time_diff

    def _cost_update(self, body: ParsedBody) -> None:
        if "extensions" not in body:
            return
        self.options.cost_store.append(self.session, int(body["extensions"]["cost"]["actualQueryCost"]))

    def _parse_response(self, api: str, response: Response, retries: int) -> Union[ApiResult, RestResult]:
        try:
            errors = None
            body = response.json()
            if "errors" in body or "error" in body:
                errors = body.get("errors", body.get("error", None))
                body = None
        except Exception as e:
            errors = e
            body = None

        kwargs = {
            "response": response,
            "status": response.status_code,
            "body": body,
            "errors": errors,
            "retries": retries,
        }
        if api == REST:
            return RestResult(
                link=self._rest_extract_link(response.headers),
                **kwargs,
            )
        return ApiResult(**kwargs)

    def _retry_required(self, response: Response, retries: int) -> Union[bool, float]:
        if response.status_code in self.options.retry_on_status and retries < self.options.max_retries:
            if RETRY_HEADER in response.headers:
                return float(response.headers[RETRY_HEADER]) * ONE_SECOND
            return 0.0
        return False
