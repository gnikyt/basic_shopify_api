from typing import Union, List, Dict, Optional
from httpx._types import RequestData, QueryParamTypes

UnionRequestData = Union[QueryParamTypes, RequestData]
StoreValue = Union[int, float]
StoreContainer = Dict[str, List[StoreValue]]
ParsedBody = Optional[dict]
ParsedError = Optional[Union[dict, Exception]]
