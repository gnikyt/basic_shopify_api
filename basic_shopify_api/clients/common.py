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
    """
    A common class shared between all clients to help prevent duplicated
    code between sync and async.
    """

    @property
    def _regex_not_authable(self) -> Pattern:
        """
        Compile NOT_AUTHABLE_PATTERN once.
        """

        return re.compile(NOT_AUTHABLE_PATTERN)

    @property
    def _regex_not_versionable(self) -> Pattern:
        """
        Compile NOT_VERSIONABLE_PATH once.
        """

        return re.compile(NOT_VERSIONABLE_PATTERN)

    @property
    def _regex_link(self) -> Pattern:
        """
        Compile LINK_PATTERN once.
        """

        return re.compile(LINK_PATTERN)

    def is_authable(self, path: str) -> bool:
        """
        Determine if the path need authentication.

        Args:
            path: The URL path.
        """

        return not bool(self._regex_not_authable.match(path))

    def is_versionable(self, path: str) -> bool:
        """
        Determine if the path needs API version.

        Args:
            path: The URL path.
        """

        return not bool(self._regex_not_versionable.match(path))

    def replace_path(self, path: str) -> str:
        """
        Adds versioning to the path.

        Args:
            path: The URL path.
        """

        return path.replace("/api", f"/api/{self.options.version}")

    def version_path(self, path: str, ignore_check: bool = False) -> str:
        """
        Determines if the path needs to be versioned.

        Args:
            path: The URL path.
            ignore_check: Ignore checks if version is required, simply replace it anyways.
        """

        if ignore_check:
            return self.replace_path(path)

        ignore_versioning = (
            not self.is_authable(path) or
            not self.is_versionable(path) or
            self.options.version in path
        )
        return path if ignore_versioning else self.replace_path(path)

    def _build_headers(self, headers: HeaderTypes) -> HeaderTypes:
        """
        Build headers to send with the request.
        Combines headers defined in options with inputted headers.
        Also will add in ACCESS_TOKEN_HEADER if the API call is public.

        Args:
            headers: Dict of headers to add to the request.
        """

        if self.options.is_public:
            headers = {ACCESS_TOKEN_HEADER: self.session.password, **headers}
        return {**self.options.headers, **headers}

    def _build_request(
        self,
        method: str,
        path: str,
        params: UnionRequestData = {},
        headers: HeaderTypes = {}
    ) -> dict:
        """
        Builds a request based on the method of request (GET/POST).
        """

        kwargs = {
            "url": self.version_path(path),
            "headers": self._build_headers(headers),
        }
        if method == "get":
            # GET, send as query
            kwargs["params"] = params
        else:
            # POST, send as JSON
            kwargs["json"] = params
        return kwargs

    def _rest_extract_link(self, headers: HeaderTypes) -> RestLink:
        """
        REST responses, if paginated, will contain a header which will
        contain a string (pageinfo) for the next and previous calls.
        """

        link = {"next": None, "prev": None}
        if LINK_HEADER in headers:
            results = self._regex_link.findall(headers[LINK_HEADER])
            for result in results:
                link[result[1]] = result[0]
        return RestLink(**link)

    def _rest_rate_limit_required(self) -> Union[bool, int]:
        """
        Determines if rate limiting is required.

        First, we check the number of requests. If they're below the limit, we allow it.

        Next, we check if the number of requests happened within a "window of time".
        A "window of time" is the first request time, plus 1 second.

        If the request is inside the window, we must sleep the difference.
        If the request is outside the window, we allow it and reset the request times.
        """

        all_time = self.options.time_store.all(self.session)
        if len(all_time) < self.options.rest_limit:
            # Number of requests is below the limit, no limiting required
            return False

        # We've reached the limit, lets see if the request happened within or outside the window of time
        current_time = self.options.deferrer.current_time()
        window_time = all_time[0] + ONE_SECOND

        # Reset the request times, return result... False = no limiting, else limit for X ms
        self.options.time_store.reset(self.session)
        return False if current_time > window_time else window_time - current_time

    def _graphql_cost_limit_required(self) -> Union[bool, int]:
        """
        Determine if cost limiting is required.

        First we check if the number of requests is empty or the costs are empty.
        If they are, we allow the request to continue as normal.

        Next, we compare the last request time and current time.
        If its over 1 second, we allow it through without limiting.
        If its under 1 second, we check the cost of the query to determine if its over the limit.
        If its over the limit, we sleep the difference in ms.
        If its under the limit, we allow it through without limiting.

        In both cases, request times and costing is reset.
        """

        all_time = self.options.time_store.all(self.session)
        all_cost = self.options.cost_store.all(self.session)
        if len(all_time) == 0 or len(all_cost) == 0:
            # Nothing was done to warrant checking
            return False

        # Determine time difference between last request and current
        last_time, last_cost = all_time[-1], all_cost[-1]
        time_diff = self.options.deferrer.current_time() - last_time
        points_per_sec = self.options.graphql_limit

        # Reset request times and costing, return if sleeping should happen or not
        self.options.time_store.reset(self.session)
        self.options.cost_store.reset(self.session)
        return False if time_diff > ONE_SECOND or last_cost < points_per_sec else ONE_SECOND - time_diff

    def _cost_update(self, body: ParsedBody) -> None:
        """
        Read the body and grab the "actualQueryCost" to use for cost limiting.
        """

        if "extensions" not in body:
            return
        self.options.cost_store.append(self.session, int(body["extensions"]["cost"]["actualQueryCost"]))

    def _parse_response(self, api: str, response: Response, retries: int) -> Union[ApiResult, RestResult]:
        """
        Get the response from HTTPX and parse it for a JSON body and errors.
        """

        try:
            # Try to decode the JSON
            errors = None
            body = response.json()
            if "errors" in body or "error" in body:
                # JSON body has an "error" or "errors" key, grab it, kill the body
                errors = body.get("errors", body.get("error", None))
                body = None
        except Exception as e:
            # Error decoding for some reason, get the exception and kill the body
            errors = e
            body = None

        # Return the HTTPX response, HTTP status code, JSON body, errors body/exception, and number of retires
        kwargs = {
            "response": response,
            "status": response.status_code,
            "body": body,
            "errors": errors,
            "retries": retries,
        }
        if api == REST:
            # Include "link" for REST calls
            return RestResult(
                link=self._rest_extract_link(response.headers),
                **kwargs,
            )
        return ApiResult(**kwargs)

    def _retry_required(self, response: Response, retries: int) -> Union[bool, float]:
        """
        Determine if a retry of the request is required.
        """

        if response.status_code in self.options.retry_on_status and retries < self.options.max_retries:
            # Status code is within the checks
            if RETRY_HEADER in response.headers:
                # Use retry header timer since is available to use
                return float(response.headers[RETRY_HEADER]) * ONE_SECOND
            return 0.0
        return False
