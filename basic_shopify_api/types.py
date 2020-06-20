from typing import Dict, Union
from httpx._types import PrimitiveData, RequestData, QueryParamTypes

DataDict = Dict[str, PrimitiveData]
UnionRequestData = Union[QueryParamTypes, RequestData]
