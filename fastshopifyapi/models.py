from typing import Optional
from httpx._models import Response
from http import HTTPStatus
from .types import ParsedBody, ParsedError


class Session:
    def __init__(self, domain: str = None, key: str = None, password: str = None, secret: str = None):
        self.domain = domain
        self.key = key
        self.password = password
        self.secret = secret

    @property
    def base_url(self) -> str:
        return f"https://{self.domain}"


class RestLink:
    def __init__(self, next: Optional[str], prev: Optional[str]):
        self.next = next
        self.prev = prev


class ApiResult:
    def __init__(
        self,
        response: Response,
        status: HTTPStatus,
        body: ParsedBody,
        errors: ParsedError,
        retries: int = 0,
    ):
        self.response = response
        self.status = status,
        self.body = body
        self.errors = errors
        self.retries = retries


class RestResult(ApiResult):
    def __init__(self, link: RestLink, **kwargs):
        super().__init__(**kwargs)
        self.link = link
