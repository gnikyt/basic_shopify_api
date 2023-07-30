from typing import Union, List, Dict, Optional
from httpx._types import RequestData, QueryParamTypes

# Joins HTTPX's query or post data
UnionRequestData = Union[QueryParamTypes, RequestData]
# Value for cost/time storage
StoreValue = Union[int, float]
# Container dict setup for cost/time storage
StoreContainer = Dict[str, List[StoreValue]]
# Parsed JSON body from response
ParsedBody = Optional[dict]
# Parsed error body from response
ParsedError = Optional[Union[dict, Exception]]
# Time to sleep for deferrer
SleepTime = Union[float, int]
