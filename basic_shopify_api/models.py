from typing import Union, Dict, Optional
from httpx._models import Response
from http import HTTPStatus


class RestLink:
    def __init__(self, next: Optional[str], prev: Optional[str]):
        self.next = next
        self.prev = prev


class ApiResult:
    def __int__(
        self,
        response: Response,
        status: HTTPStatus,
        body: Union[Dict[str, str], str],
        errors: Optional[Union[Dict[str, str], str]],
    ):
        self.response = response
        self.status = status,
        self.body = body
        self.errors = errors


class RestResult(ApiResult):
    def __int__(self, link: RestLink, **kwargs):
        super().__init__(**kwargs)
        self.link = link
