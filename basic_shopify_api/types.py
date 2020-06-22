from typing import Union
from httpx._types import RequestData, QueryParamTypes

UnionRequestData = Union[QueryParamTypes, RequestData]
