from . import ApiCommon
from ..options import Options
from ..models import ApiResult, RestResult, Session
from ..constants import REST, GRAPHQL
from httpx import AsyncClient as AsyncHttpxClient
from httpx._types import HeaderTypes, QueryParamTypes
from httpx._models import Response


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
            base_url=self.session.base_url,
            auth=None if self.options.is_public else (self.session.key, self.session.password),
            **kwargs
        )

    async def _rest_rate_limit(self) -> None:
        limiting_required = self._rest_rate_limit_required()
        if limiting_required is not False:
            await self.options.deferrer.asleep(limiting_required)

    async def _graphql_cost_limit(self) -> None:
        limiting_required = self._graphql_cost_limit_required()
        if limiting_required is not False:
            await self.options.deferrer.asleep(limiting_required)

    async def _rest_pre_actions(self, **kwargs) -> None:
        await self._rest_rate_limit()
        self.options.time_store.append(self.session, self.options.deferrer.current_time())
        [await meth(self, **kwargs) for meth in self.options.rest_pre_actions]

    async def _graphql_pre_actions(self, **kwargs) -> None:
        await self._graphql_cost_limit()
        self.options.time_store.append(self.session, self.options.deferrer.current_time())
        [await meth(self, **kwargs) for meth in self.options.graphql_pre_actions]

    async def _rest_post_actions(self, response: Response, retries: int) -> RestResult:
        result = self._parse_response(REST, response, retries)
        [await meth(self, result) for meth in self.options.rest_post_actions]
        return result

    async def _graphql_post_actions(self, response: Response, retries: int) -> ApiResult:
        result = self._parse_response(GRAPHQL, response, retries)
        self._cost_update(result.body)
        [await meth(self, result) for meth in self.options.graphql_post_actions]
        return result

    def _retry_request(meth: callable) -> callable:
        async def wrapper(*args, **kwargs) -> ApiResult:
            inst: AsyncClient = args[0]
            retries = kwargs.get("_retries", 0)
            result: ApiResult = await meth(*args, **kwargs)
            response = result.response
            retry = inst._retry_required(response, retries)

            if retry is not False:
                await inst.options.deferrer.asleep(retry)

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
        meth = getattr(self, method)
        kwargs = self._build_request(method, path, params, headers)
        await self._rest_pre_actions(**kwargs)

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
        kwargs = self._build_request(
            "post",
            "/admin/api/graphql.json",
            {"query": query, "variables": variables},
            headers,
        )
        await self._graphql_pre_actions(**kwargs)

        response = await self.post(**kwargs)
        result = await self._graphql_post_actions(response, _retries)
        return result
