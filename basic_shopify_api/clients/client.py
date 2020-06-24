from . import ApiCommon
from ..options import Options
from ..models import RestResult, ApiResult, Session
from ..types import UnionRequestData
from ..constants import REST, GRAPHQL
from httpx import Client as HttpxClient
from httpx._types import HeaderTypes
from httpx._models import Response


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
            base_url=self.session.base_url,
            auth=None if self.options.is_public else (self.session.key, self.session.password),
            **kwargs
        )

    def _rest_rate_limit(self) -> None:
        limiting_required = self._rest_rate_limit_required()
        if limiting_required is not False:
            self.options.deferrer.sleep(limiting_required)

    def _graphql_cost_limit(self) -> None:
        limiting_required = self._graphql_cost_limit_required()
        if limiting_required is not False:
            self.options.deferrer.sleep(limiting_required)

    def _rest_pre_actions(self, **kwargs) -> None:
        self._rest_rate_limit()
        self.options.time_store.append(self.session, self.options.deferrer.current_time())
        [meth(self, **kwargs) for meth in self.options.rest_pre_actions]

    def _graphql_pre_actions(self, **kwargs) -> None:
        self._graphql_cost_limit()
        self.options.time_store.append(self.session, self.options.deferrer.current_time())
        [meth(self, **kwargs) for meth in self.options.graphql_pre_actions]

    def _rest_post_actions(self, response: Response, retries: int) -> RestResult:
        result = self._parse_response(REST, response, retries)
        [meth(self, result) for meth in self.options.rest_post_actions]
        return result

    def _graphql_post_actions(self, response: Response, retries: int) -> ApiResult:
        result = self._parse_response(GRAPHQL, response, retries)
        self._cost_update(result.body)
        [meth(self, result) for meth in self.options.graphql_post_actions]
        return result

    def _retry_request(meth: callable) -> callable:
        def wrapper(*args, **kwargs) -> ApiResult:
            inst: Client = args[0]
            retries: int = kwargs.get("_retries", 0)
            result: ApiResult = meth(*args, **kwargs)
            response: Response = result.response
            retry = inst._retry_required(response, retries)

            if retry is not False:
                inst.options.deferrer.sleep(retry)

                kwargs["_retries"] = retries + 1
                inst_meth = getattr(inst, meth.__name__)
                return inst_meth(*args[1:], **kwargs)
            return result
        return wrapper

    @_retry_request
    def rest(
        self,
        method: str,
        path: str,
        params: UnionRequestData = None,
        headers: HeaderTypes = {},
        _retries: int = 0
    ) -> RestResult:
        meth = getattr(self, method)
        kwargs = self._build_request(method, path, params, headers)
        self._rest_pre_actions(**kwargs)
        return self._rest_post_actions(meth(**kwargs), _retries)

    @_retry_request
    def graphql(
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
        self._graphql_pre_actions(**kwargs)
        return self._graphql_post_actions(self.post(**kwargs), _retries)
