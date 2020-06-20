from dataclasses import dataclass
from typing import Union, Dict, Optional
from httpx._models import Response
from http import HTTPStatus


@dataclass(frozen=True)
class RestLink:
    next: Optional[str]
    prev: Optional[str]


@dataclass(frozen=True)
class ApiResult:
    response: Response
    status: HTTPStatus
    body: Union[Dict[str, str], str]
    errors: Optional[Union[Dict[str, str], str]]


@dataclass(frozen=True)
class RestResult(ApiResult):
    link: RestLink
