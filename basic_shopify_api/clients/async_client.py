from . import ApiCommon
from ..options import Options
from ..models import ApiResult, RestResult, Session
from ..constants import REST, GRAPHQL
from httpx import AsyncClient as AsyncHttpxClient
from httpx._types import HeaderTypes, QueryParamTypes
from httpx._models import Response


class AsyncClient(AsyncHttpxClient, ApiCommon):
    """
    Sync client, extends the common client and HTTPX.
    """

    def __init__(
        self,
        session: Session,
        options: Options,
        **kwargs
    ):
        """
        Extend HTTPX's init and setup the client with base URL and auth.
        """

        self.session = session
        self.options = options
        super().__init__(
            base_url=self.session.base_url,
            auth=None if self.options.is_public else (self.session.key, self.session.password),
            **kwargs
        )

    async def _rest_rate_limit(self) -> None:
        """
        Handle rate limiting of REST.
        """

        limiting_required = self._rest_rate_limit_required()
        if limiting_required is not False:
            # Rate limit was determined to be required, sleep for X ms
            await self.options.deferrer.asleep(limiting_required)

    async def _graphql_cost_limit(self) -> None:
        """
        Handle cost limiting for GraphQL.
        """

        limiting_required = self._graphql_cost_limit_required()
        if limiting_required is not False:
            # Cost limit was determined to be required, sleep for X ms
            await self.options.deferrer.asleep(limiting_required)

    async def _rest_pre_actions(self, **kwargs) -> None:
        """
        Actions which fire before REST API call.
        """

        # Determine if rate limiting is required and handle it
        await self._rest_rate_limit()
        # Add to the request times
        self.options.time_store.append(self.session, self.options.deferrer.current_time())
        # Run user-defined actions and pass in the request built
        [await meth(self, **kwargs) for meth in self.options.rest_pre_actions]

    async def _graphql_pre_actions(self, **kwargs) -> None:
        """
        Actions which fire before GraphQL API call.
        """

        # Determine if cost limiting is required and handle it
        await self._graphql_cost_limit()
        # Add to the request times
        self.options.time_store.append(self.session, self.options.deferrer.current_time())
        # Run user-defined actions and pass in the request built
        [await meth(self, **kwargs) for meth in self.options.graphql_pre_actions]

    async def _rest_post_actions(self, response: Response, retries: int) -> RestResult:
        """
        Actions which fire after REST API call.
        """

        # Parse the response from HTTPX
        result = self._parse_response(REST, response, retries)
        # Run user-defined actions and pass in the result object
        [await meth(self, result) for meth in self.options.rest_post_actions]
        return result

    async def _graphql_post_actions(self, response: Response, retries: int) -> ApiResult:
        """
        Actions which fire after GraphQL API call.
        """

        # Parse the response from HTTPX
        result = self._parse_response(GRAPHQL, response, retries)
        # Add to the costs
        self._cost_update(result.body)
        # Run user-defined actions and pass in the result object
        [await meth(self, result) for meth in self.options.graphql_post_actions]
        return result

    def _retry_request(meth: callable) -> callable:
        """
        Determine if retry is required.

        If it is, retry the request.
        If not, return the result.
        """

        async def wrapper(*args, **kwargs) -> ApiResult:
            # Get the instance
            inst: AsyncClient = args[0]
            # Get the number of retries so far
            retries = kwargs.get("_retries", 0)
            # Run the call (rest or graphql)
            result: ApiResult = await meth(*args, **kwargs)
            # Get the response and determine if retry is required
            response = result.response
            retry = inst._retry_required(response, retries)

            if retry is not False:
                # Retry is needed, sleep for X ms
                await inst.options.deferrer.asleep(retry)

                # Re-run the request
                kwargs["_retries"] = retries + 1
                inst_meth = getattr(inst, meth.__name__)
                return await inst_meth(*args[1:], **kwargs)
            return result
        return wrapper

    @_retry_request
    async def rest(
        self,
        method: str,
        path: str,
        params: QueryParamTypes = None,
        headers: HeaderTypes = {},
        _retries: int = 0
    ) -> RestResult:
        """
        Fire a REST API call.
        """

        # Dynamically map to HTTPX's method for get/post/put/etc
        meth = getattr(self, method)
        # Build the request based on the method and inputs
        kwargs = self._build_request(method, path, params, headers)
        # Run the pre-actions
        await self._rest_pre_actions(**kwargs)

        # Run the call and post-actions, and return the result
        response = await meth(**kwargs)
        result = await self._rest_post_actions(response, _retries)
        return result

    @_retry_request
    async def graphql(
        self,
        query: str,
        variables: dict = None,
        headers: HeaderTypes = {},
        _retries: int = 0,
    ) -> ApiResult:
        """
        Fire a GraphQL call.
        """

        # Build the request
        kwargs = self._build_request(
            "post",
            "/admin/api/graphql.json",
            {"query": query, "variables": variables},
            headers,
        )
        # Run the pre-actions
        await self._graphql_pre_actions(**kwargs)

        # Run the call and post-actions, and return the result
        response = await self.post(**kwargs)
        result = await self._graphql_post_actions(response, _retries)
        return result
